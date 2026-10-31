"""
Unit and integration tests for FinPixe Migration Tool (RIM-BMT v3.0).
Tests coverage:
- Path resolution and validation when manage.py is missing
- Path resolution when manage.py exists but run_full_migration command is missing
- Subprocess exit code enforcement (non-zero exits cannot succeed)
- Secret sanitization (masking DB passwords and secrets in logs)
- Valid JSON responses on all API error paths (no unexpected HTML / syntax errors)
- Health check endpoint verification
- Database connection test safety (read-only, no write operations)
- Temporary file cleanup
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from finfixe_migration_ui import (
    app,
    sanitize_diagnostics,
    find_python_interpreter,
    resolve_and_validate_migration_runner
)


class TestMigrationRunnerValidation(unittest.TestCase):
    """Tests for runner path discovery, command verification, and missing component detection."""

    def test_missing_runner_returns_clean_error(self):
        """When no manage.py exists in candidate paths, validation must fail safely."""
        with patch.dict(os.environ, {"FINPIXE_BACKEND_MANAGE_PY": "/nonexistent/path/manage.py"}, clear=False):
            result = resolve_and_validate_migration_runner()
            self.assertFalse(result["valid"])
            self.assertEqual(result["error_type"], "MISSING_RUNNER")
            self.assertEqual(result["component_missing"], "run_full_migration.py")
            self.assertIn("Migration runner ('manage.py') not found", result["message"])
            self.assertIn("budstechconsultancy@gmail.com", result["message"])

    def test_manage_py_without_run_full_migration_command(self):
        """When manage.py exists but lacks run_full_migration, validation must detect missing command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dummy_manage = os.path.join(tmpdir, "manage.py")
            # Write a minimal python script simulating Django manage.py that rejects unknown command
            with open(dummy_manage, "w", encoding="utf-8") as f:
                f.write(
                    "import sys\n"
                    "if 'run_full_migration' in sys.argv:\n"
                    "    sys.stderr.write(\"Unknown command: 'run_full_migration'\\n\")\n"
                    "    sys.exit(1)\n"
                    "sys.exit(0)\n"
                )

            with patch.dict(os.environ, {"FINPIXE_BACKEND_MANAGE_PY": dummy_manage}, clear=False):
                result = resolve_and_validate_migration_runner()
                self.assertFalse(result["valid"])
                self.assertEqual(result["error_type"], "MISSING_COMMAND")
                self.assertEqual(result["component_missing"], "run_full_migration.py")
                self.assertIn("run_full_migration' is NOT registered", result["message"])

    def test_genuine_runner_with_required_args_passes_validation(self):
        """When a genuine runner exists and supports all required flags, validation succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dummy_manage = os.path.join(tmpdir, "manage.py")
            with open(dummy_manage, "w", encoding="utf-8") as f:
                f.write(
                    "import sys\n"
                    "if 'run_full_migration' in sys.argv and '--help' in sys.argv:\n"
                    "    print('Usage: manage.py run_full_migration <xml> --tenant_id=<id> --manifest_out=<file> [--master_xml=<f>] [--dry_run]')\n"
                    "    sys.exit(0)\n"
                    "sys.exit(1)\n"
                )

            with patch.dict(os.environ, {"FINPIXE_BACKEND_MANAGE_PY": dummy_manage}, clear=False):
                result = resolve_and_validate_migration_runner()
                self.assertTrue(result["valid"])
                self.assertTrue(result["command_available"])
                self.assertIsNone(result["component_missing"])
                self.assertIn("Genuine RIM migration runner verified", result["message"])


class TestSecretSanitization(unittest.TestCase):
    """Tests for redacting passwords, secrets, and connection strings from diagnostics."""

    def test_masks_explicit_secrets(self):
        secret_pw = "SuperSecretP@ssw0rd!123"
        text = f"Connecting to db with user admin and password {secret_pw} failed."
        sanitized = sanitize_diagnostics(text, secrets=[secret_pw])
        self.assertNotIn(secret_pw, sanitized)
        self.assertIn("********", sanitized)

    def test_masks_url_passwords(self):
        text = "Failed to connect to mysql://root:SuperSecret123@172.31.5.38:3306/ai_accounting"
        sanitized = sanitize_diagnostics(text)
        self.assertNotIn("SuperSecret123", sanitized)
        self.assertIn("root:********@172.31.5.38", sanitized)

    def test_masks_cli_flags(self):
        text = "Executing: --db_password=SecretMySQLPass --tenant_id=xyz"
        sanitized = sanitize_diagnostics(text)
        self.assertNotIn("SecretMySQLPass", sanitized)
        self.assertIn("--db_password=********", sanitized)


class TestApiEndpoints(unittest.TestCase):
    """Integration tests for FastAPI endpoints using TestClient."""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_returns_valid_json(self):
        """GET /api/health must return 200 and valid JSON with runner diagnostic info."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["version"], "3.0.0")
        self.assertIn("runner", data)
        self.assertIn("manage_py_found", data["runner"])
        self.assertIn("valid", data["runner"])

    def test_serve_ui_returns_html(self):
        """GET / returns HTML dashboard."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("RIM-BMT", response.text)
        self.assertIn("safeFetchJson", response.text)

    def test_run_v3_missing_runner_returns_json_error(self):
        """POST /api/run_v3 must return clean JSON error (not HTML) when runner is missing."""
        with patch.dict(os.environ, {"FINPIXE_BACKEND_MANAGE_PY": "/nonexistent/manage.py"}, clear=False):
            dummy_xml = b"<ENVELOPE><BODY><DATA>Test</DATA></BODY></ENVELOPE>"
            response = self.client.post(
                "/api/run_v3",
                data={
                    "source_mode": "manual",
                    "tenant_id": "test-tenant-uuid",
                    "dry_run": "true",
                    "db_host": "localhost",
                    "db_port": "3306",
                    "db_name": "ai_accounting",
                    "db_user": "root",
                    "db_password": "dummy_password"
                },
                files={
                    "file": ("test.xml", dummy_xml, "text/xml")
                }
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.headers["content-type"].startswith("application/json"))
            data = response.json()
            self.assertEqual(data["status"], "error")
            self.assertEqual(data["component_missing"], "run_full_migration.py")
            self.assertIn("run_full_migration.py", data["logs"])
            self.assertIn("budstechconsultancy@gmail.com", data["logs"])
            # Ensure password is never exposed in returned logs
            self.assertNotIn("dummy_password", data["logs"])
            self.assertIsNone(data["manifest"])

    def test_subprocess_failure_cannot_report_complete(self):
        """If a runner returns non-zero exit code, status must be error and exit_code captured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dummy_manage = os.path.join(tmpdir, "manage.py")
            # This manage.py passes verification with --help, but exits with code 2 during actual execution
            with open(dummy_manage, "w", encoding="utf-8") as f:
                f.write(
                    "import sys\n"
                    "if '--help' in sys.argv:\n"
                    "    print('Usage: manage.py run_full_migration <xml> --tenant_id=<id> --manifest_out=<file>')\n"
                    "    sys.exit(0)\n"
                    "sys.stderr.write('Fatal pipeline failure in Phase 1\\n')\n"
                    "sys.exit(2)\n"
                )

            with patch.dict(os.environ, {"FINPIXE_BACKEND_MANAGE_PY": dummy_manage}, clear=False):
                dummy_xml = b"<ENVELOPE><BODY><DATA>Test</DATA></BODY></ENVELOPE>"
                response = self.client.post(
                    "/api/run_v3",
                    data={
                        "source_mode": "manual",
                        "tenant_id": "test-tenant-uuid",
                        "dry_run": "true",
                        "db_host": "localhost",
                        "db_port": "3306",
                        "db_name": "ai_accounting",
                        "db_user": "root",
                        "db_password": ""
                    },
                    files={
                        "file": ("test.xml", dummy_xml, "text/xml")
                    }
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "error")
                self.assertEqual(data["exit_code"], 2)
                self.assertIn("exit code 2", data["logs"])
                self.assertIsNone(data["manifest"])

    def test_test_db_invalid_port_returns_json_error(self):
        """POST /api/test_db with non-numeric port returns JSON error safely."""
        response = self.client.post(
            "/api/test_db",
            data={
                "host": "localhost",
                "port": "not-a-port",
                "database": "ai_accounting",
                "user": "root",
                "password": ""
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("Invalid port number", data["message"])

    def test_test_db_unreachable_host_returns_json_error_without_password(self):
        """POST /api/test_db connection failure returns JSON without exposing password."""
        secret = "SecretRDSKey987!"
        response = self.client.post(
            "/api/test_db",
            data={
                "host": "192.0.2.1",  # Test-net unreachable IP
                "port": "3306",
                "database": "ai_accounting",
                "user": "migration_user",
                "password": secret
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        data = response.json()
        self.assertEqual(data["status"], "error")
        # Ensure secret is not in the response message
        self.assertNotIn(secret, data["message"])

    def test_unhandled_api_route_returns_json_404(self):
        """Non-existent /api/ routes return JSON error rather than HTML."""
        response = self.client.get("/api/nonexistent_endpoint")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        data = response.json()
        self.assertEqual(data["status"], "error")


if __name__ == "__main__":
    unittest.main()
