import os

CONNECTIONS = {
    'default': {
        'driver': 'postgresql',
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'invoice_crm'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'secret123'),
        'pool_size': 10,
        'max_overflow': 20,
        'echo': False
    }
}