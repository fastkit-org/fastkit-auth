import os

APP_NAME = os.getenv('APP_NAME', 'Invoice CRM')
DEBUG = os.getenv('APP_DEBUG', 'False').lower() in ('true', '1', 't')
DEFAULT_LANGUAGE = os.getenv('APP_DEFAULT_LANGUAGE', 'en')
FALLBACK_LANGUAGE = os.getenv('APP_FALLBACK_LANGUAGE', 'en')

#mail
MAIL_PROVIDER = os.getenv('MAIL_PROVIDER')
MAIL_API_KEY = os.getenv('MAIL_API_KEY')
MAIL_ENDPOINT = os.getenv('MAIL_ENDPOINT')
MAIL_FROM = os.getenv('MAIL_FROM')