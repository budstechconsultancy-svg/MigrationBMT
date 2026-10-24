#!/usr/bin/env python
"""Django manage.py for FinPixe RIM-BMT Migration Engine (standalone)."""
import os
import sys
from pathlib import Path

# Ensure both current directory and parent directory are on sys.path
CUR_DIR = Path(__file__).resolve().parent
for p in [str(CUR_DIR), str(CUR_DIR.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rim_settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Please activate the venv:\n"
            "  source /opt/finpixe_migration_tool/venv311/bin/activate"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
