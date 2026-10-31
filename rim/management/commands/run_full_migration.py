"""
RIM-BMT Engine Loader (Compiled Binary Distribution)
Proprietary & Confidential - Budstech Consultancy
"""
import os
import importlib.util

# Load pre-compiled binary core
_pyc_path = os.path.join(os.path.dirname(__file__), 'run_full_migration_core.pyc')
if os.path.exists(_pyc_path):
    _spec = importlib.util.spec_from_file_location('run_full_migration_core', _pyc_path)
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    Command = _module.Command
else:
    try:
        from .run_full_migration_core import Command
    except ImportError:
        raise ImportError("RIM core binary 'run_full_migration_core.pyc' not found.")
