"""
Minimal Django settings for RIM-BMT Migration Engine (standalone).
Only rim app and database connection are required - no full backend needed.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
for p in [str(BASE_DIR), str(BASE_DIR.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET',
    'rim-bmt-standalone-secret-key-migration-tool-only-not-for-web'
)

DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
]

# Register all domain apps present in directory
DOMAIN_APPS = [
    'core',
    'company',
    'masters',
    'accounting',
    'inventory',
    'vendors',
    'customerportal',
    'payroll',
    'rbac',
    'transactions',
    'dashboard',
    'users',
    'reports',
    'vouchers',
    'ocr_pipeline',
    'gst_reconciliation',
    'bank_upload',
    'bank_staging',
    'pending_purchases',
    'services',
    'rim',
]
for app_name in DOMAIN_APPS:
    if (BASE_DIR / app_name).is_dir() or (BASE_DIR.parent / app_name).is_dir():
        if app_name not in INSTALLED_APPS:
            INSTALLED_APPS.append(app_name)
if 'rim' not in INSTALLED_APPS:
    INSTALLED_APPS.append('rim')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'ai_accounting'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'connect_timeout': 10,
        },
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
