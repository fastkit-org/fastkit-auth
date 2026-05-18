<div align="center">
  <h1>🔐 FastKit Auth</h1>
  <p><strong>Authentication package for FastKit / FastAPI applications</strong></p>

  [![PyPI version](https://badge.fury.io/py/fastkit-auth.svg)](https://pypi.org/project/fastkit-auth/)
  [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

---

## What is FastKit Auth?

FastKit Auth is part of the [FastKit](https://fastkit.org/) ecosystem.
It provides ready-to-use authentication building blocks for FastAPI applications
built on top of [fastkit-core](https://github.com/fastkit-org/fastkit-core).

> ⚠️ **Early release.** The API may change before 1.0. Not recommended for production yet.

---

## Features

- **JWT Authentication** — Access + refresh token flow
- **User Registration** — With email verification via OTP token
- **Password Reset** — Token-based reset flow via email
- **Profile Management** — Get and update authenticated user profile
- **Password Hashing** — Bcrypt via passlib
- **Auth Dependencies** — `get_current_user`, `get_current_verified_user`, `get_current_superuser`
- **Email Sending** — Integrated with [mailbridge](https://github.com/fastkit-org/mailbridge)

### Roadmap
- [ ] 2FA (TOTP + Backup codes)
- [ ] RBAC (Roles + Permissions)
- [ ] Decorators (`@require_permission`, `@require_role`)
- [ ] Audit Logging
- [ ] Rate Limiting + Account Locking

---

## Requirements

- Python 3.12+
- PostgreSQL
- `fastkit-core >= 0.4.0`
- `mailbridge >= 2.0.0`

---

## Installation

```bash
pip install fastkit-auth
```

---

## Configuration

FastKit Auth reads configuration through `fastkit-core`'s `ConfigManager`.
You need `app` and `auth` config modules in your project.

**`config/auth.py` (example):**
```python
JWT_ALGORITHM = "HS256"
JWT_TOKEN_SECRET = "your-secret"
JWT_LIFETIME_SECONDS = 3600
JWT_REFRESH_SECRET_KEY = "your-refresh-secret"
JWT_REFRESH_LIFETIME_SECONDS = 604800
PASSWORD_ENCRYPTION_SCHEMES = ["bcrypt"]
```

**`config/app.py` (example):**
```python
MAIL_PROVIDER = "smtp"
MAIL_API_KEY = ""
MAIL_ENDPOINT = "smtp://localhost:1025"
MAIL_FROM = "noreply@example.com"
```

---

## Quick Start

```python
from fastapi import FastAPI
from fastkit_auth.authentication.router import router as auth_router
from fastkit_auth.users.router import registration_router, profile_router
from fastkit_core.database import init_async_database
from fastkit_core.config import ConfigManager
from fastkit_core.http.exception_handlers import register_exception_handlers

configuration = ConfigManager(modules=['app', 'database', 'auth'])
init_async_database(configuration)

app = FastAPI()
register_exception_handlers(app=app)

app.include_router(auth_router)
app.include_router(registration_router)
app.include_router(profile_router)
```

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/registration` | Register a new user |
| `PUT` | `/verify-email?token=` | Verify email with OTP token |
| `POST` | `/auth/login` | Login, returns JWT tokens |
| `POST` | `/auth/reset-password` | Request password reset email |
| `POST` | `/auth/update-password` | Set new password using reset token |
| `GET` | `/profile` | Get authenticated user profile |
| `PUT` | `/profile` | Update authenticated user profile |

---

## Auth Dependencies

Use these in your route dependencies:

```python
from fastkit_auth.authentication.dependencies import (
    get_current_user,
    get_current_verified_user,
    get_current_superuser,
)
```

```python
@router.get("/me")
async def me(user = Depends(get_current_user)):
    return user

@router.get("/admin")
async def admin_only(user = Depends(get_current_superuser)):
    ...
```

---

## User Model

```python
from fastkit_auth.users.models import User
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `first_name` | str | |
| `last_name` | str | |
| `email` | str | Unique |
| `hashed_password` | str | Bcrypt |
| `is_active` | bool | Activated after email verification |
| `is_verified` | bool | Email verified |
| `is_superuser` | bool | Superuser flag |
| `email_verified_at` | datetime | Timestamp of verification |

---

## Links

- [fastkit-core](https://github.com/fastkit-org/fastkit-core)
- [PyPI](https://pypi.org/project/fastkit-auth/)