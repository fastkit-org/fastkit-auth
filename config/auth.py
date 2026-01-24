import os

RESET_PASSWORD_TOKEN_SECRET = os.getenv(
    'RESET_PASSWORD_TOKEN_SECRET',
    'change-me-in-production-reset'
)

# Email Verification Tokens
VERIFICATION_TOKEN_SECRET = os.getenv(
    'VERIFICATION_TOKEN_SECRET',
    'change-me-in-production-verify'
)

# JWT Authentication
JWT_TOKEN_SECRET = os.getenv(
    'JWT_TOKEN_SECRET',
    'change-me-in-production-jwt'
)

JWT_LIFETIME_SECONDS = int(os.getenv(
    'JWT_LIFETIME_SECONDS',
    '3600'  # 1 hour default
))

# Optional: Token refresh settings
JWT_REFRESH_LIFETIME_SECONDS = int(os.getenv(
    'JWT_REFRESH_LIFETIME_SECONDS',
    '2592000'  # 30 days default
))