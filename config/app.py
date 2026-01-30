import os

APP_NAME = os.getenv('APP_NAME', 'Invoice CRM')
DEBUG = os.getenv('APP_DEBUG', 'False').lower() in ('true', '1', 't')
DEFAULT_LANGUAGE = os.getenv('APP_DEFAULT_LANGUAGE', 'en')
FALLBACK_LANGUAGE = os.getenv('APP_FALLBACK_LANGUAGE', 'en')

#mail
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_SSL_TLS = os.getenv('MAIL_SSL_TLS')