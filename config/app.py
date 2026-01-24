import os

APP_NAME = os.getenv('APP_NAME', 'Invoice CRM')
DEBUG = os.getenv('APP_DEBUG', 'False').lower() in ('true', '1', 't')
DEFAULT_LANGUAGE = os.getenv('APP_DEFAULT_LANGUAGE', 'en')
FALLBACK_LANGUAGE = os.getenv('APP_FALLBACK_LANGUAGE', 'en')