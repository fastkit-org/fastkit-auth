<div align="center">
  <h1>🔐 FastKit Auth</h1>
  
  <p><strong>Authentication & Authorization for FastKit</strong></p>
  
  <p>Production-ready authentication with JWT, OAuth2, and permissions</p>
  
  [![PyPI version](https://badge.fury.io/py/fastkit-auth.svg)](https://pypi.org/project/fastkit-auth/)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![Tests](https://github.com/fastkit/fastkit-auth/workflows/Tests/badge.svg)](https://github.com/fastkit/fastkit-auth/actions)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  
</div>

---

## 🚀 What is FastKit Auth?

FastKit Auth provides a complete, production-ready authentication and authorization system for FastAPI applications. It handles the hard parts of auth so you can focus on building your application.

**Stop writing authentication from scratch for every project.**

### Features at a Glance

- 🔑 **JWT Authentication** - Secure token-based auth
- 🔐 **Password Hashing** - Bcrypt with secure defaults
- 👤 **User Management** - Registration, login, password reset
- 🎫 **OAuth2 Support** - Social login ready
- 🛡️ **Permissions** - Role-based access control (RBAC)
- 🔄 **Token Refresh** - Automatic token rotation
- 📱 **Multi-Device** - Support for multiple sessions
- 🧪 **Fully Tested** - 95%+ test coverage

---

## 📦 Installation
```bash
pip install fastkit-auth
```

Requires `fastkit-core` (installed automatically as dependency).

---

## 🎯 Quick Start

### 1. Setup Authentication
```python
from fastapi import FastAPI, Depends
from fastkit_auth import JWTAuth, get_current_user
from fastkit_auth.models import User

app = FastAPI()
auth = JWTAuth(secret_key="your-secret-key")

# User model (inherit from Authenticatable)
class User(Base, Authenticatable):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True)
    password = Column(String(255))
    name = Column(String(100))
```

### 2. Registration Endpoint
```python
from fastkit_auth import hash_password

@app.post("/register")
def register(email: str, password: str, name: str):
    # Check if user exists
    if User.query.filter_by(email=email).first():
        raise HTTPException(400, "Email already registered")
    
    # Create user
    user = User(
        email=email,
        password=hash_password(password),
        name=name
    )
    db.add(user)
    db.commit()
    
    return {"message": "User registered successfully"}
```

### 3. Login Endpoint
```python
from fastkit_auth import verify_password

@app.post("/login")
def login(email: str, password: str):
    # Find user
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(401, "Invalid credentials")
    
    # Generate tokens
    access_token = auth.create_access_token(user_id=user.id)
    refresh_token = auth.create_refresh_token(user_id=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

### 4. Protected Routes
```python
@app.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }

@app.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_admin)):
    return {"message": "Welcome to admin dashboard"}
```

---

## 🔑 JWT Authentication

### Configuration
```python
from fastkit_auth import JWTAuth

auth = JWTAuth(
    secret_key="your-secret-key-here",  # Use environment variable!
    algorithm="HS256",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)
```

### Token Generation
```python
# Access token (short-lived)
access_token = auth.create_access_token(
    user_id=user.id,
    additional_claims={"role": "admin"}
)

# Refresh token (long-lived)
refresh_token = auth.create_refresh_token(user_id=user.id)
```

### Token Validation
```python
# Decode and validate token
try:
    payload = auth.decode_token(token)
    user_id = payload.get("sub")
except JWTError:
    raise HTTPException(401, "Invalid token")
```

### Token Refresh Flow
```python
@app.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = auth.decode_token(refresh_token)
        user_id = payload.get("sub")
        
        # Generate new access token
        new_access_token = auth.create_access_token(user_id=user_id)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")
```

---

## 👤 User Model

### Authenticatable Mixin
```python
from fastkit_auth.models import Authenticatable
from fastkit_core.database import Base

class User(Base, Authenticatable):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Optional: Add roles relationship
    roles = relationship("Role", secondary="user_roles")
```

**Authenticatable provides:**
- Password hashing utilities
- Token validation helpers
- Account status methods (is_active, is_verified, etc.)

---

## 🛡️ Permissions & RBAC

### Define Permissions
```python
from fastkit_auth.permissions import Permission, require_permission

# Define permissions
class Permissions:
    CREATE_POST = "posts.create"
    EDIT_POST = "posts.edit"
    DELETE_POST = "posts.delete"
    VIEW_ANALYTICS = "analytics.view"
```

### Role-Based Access Control
```python
from fastkit_auth import require_role, require_permission

@app.post("/posts")
def create_post(
    title: str,
    content: str,
    current_user: User = Depends(require_permission("posts.create"))
):
    # Only users with posts.create permission can access
    post = Post(title=title, content=content, author_id=current_user.id)
    db.add(post)
    db.commit()
    return post

@app.get("/admin/users")
def list_all_users(current_user: User = Depends(require_role("admin"))):
    # Only admins can access
    return User.query.all()
```

### Custom Permission Checks
```python
from fastkit_auth import get_current_user

@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user)
):
    post = Post.query.get_or_404(post_id)
    
    # Check if user is author or admin
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}
```

---

## 🔐 Password Security

### Hashing
```python
from fastkit_auth import hash_password, verify_password

# Hash password (automatically uses bcrypt with secure defaults)
hashed = hash_password("user_password")

# Verify password
is_valid = verify_password("user_password", hashed)  # True
is_valid = verify_password("wrong_password", hashed)  # False
```

### Password Reset Flow
```python
from fastkit_auth import create_reset_token, verify_reset_token

# 1. User requests password reset
@app.post("/forgot-password")
def forgot_password(email: str):
    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, reset link sent"}
    
    # Generate reset token
    reset_token = create_reset_token(user.id)
    
    # Send email with reset link (implement email sending)
    send_email(
        to=user.email,
        subject="Password Reset",
        body=f"Reset link: https://example.com/reset?token={reset_token}"
    )
    
    return {"message": "If email exists, reset link sent"}

# 2. User resets password
@app.post("/reset-password")
def reset_password(token: str, new_password: str):
    try:
        user_id = verify_reset_token(token)
    except:
        raise HTTPException(400, "Invalid or expired token")
    
    user = User.query.get(user_id)
    user.password = hash_password(new_password)
    db.commit()
    
    return {"message": "Password reset successfully"}
```

---

## 🎫 OAuth2 Support

### Social Login (Google, GitHub, etc.)
```python
from fastkit_auth.oauth import OAuth2Provider

# Configure OAuth provider
google = OAuth2Provider(
    name="google",
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    token_url="https://oauth2.googleapis.com/token",
    userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo"
)

@app.get("/auth/google")
def google_login():
    # Redirect to Google OAuth
    return google.authorize_redirect(
        redirect_uri="http://localhost:8000/auth/google/callback"
    )

@app.get("/auth/google/callback")
def google_callback(code: str):
    # Exchange code for tokens
    token = google.get_token(code)
    
    # Get user info
    user_info = google.get_userinfo(token)
    
    # Find or create user
    user = User.query.filter_by(email=user_info["email"]).first()
    if not user:
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            oauth_provider="google",
            oauth_id=user_info["id"]
        )
        db.add(user)
        db.commit()
    
    # Generate JWT tokens
    access_token = auth.create_access_token(user_id=user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 📱 Multi-Device Support

### Session Management
```python
from fastkit_auth.sessions import SessionManager

session_manager = SessionManager()

# Create session on login
@app.post("/login")
def login(email: str, password: str, device_name: str = "Web"):
    user = authenticate(email, password)
    
    # Create session
    session = session_manager.create_session(
        user_id=user.id,
        device_name=device_name,
        ip_address=request.client.host
    )
    
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token
    }

# List user sessions
@app.get("/sessions")
def list_sessions(current_user: User = Depends(get_current_user)):
    return session_manager.get_user_sessions(current_user.id)

# Revoke session
@app.delete("/sessions/{session_id}")
def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user)
):
    session_manager.revoke_session(session_id, current_user.id)
    return {"message": "Session revoked"}
```

---

## 🧪 Testing

### Test Utilities
```python
from fastkit_auth.testing import create_test_user, create_test_token

# In your tests
def test_protected_route(client):
    # Create test user
    user = create_test_user(email="test@example.com")
    
    # Create test token
    token = create_test_token(user_id=user.id)
    
    # Make authenticated request
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

---

## 📚 Documentation

- [**Getting Started**](https://docs.fastkit.dev/auth/getting-started)
- [**JWT Authentication**](https://docs.fastkit.dev/auth/jwt)
- [**OAuth2**](https://docs.fastkit.dev/auth/oauth2)
- [**Permissions & RBAC**](https://docs.fastkit.dev/auth/permissions)
- [**Password Security**](https://docs.fastkit.dev/auth/passwords)
- [**API Reference**](https://docs.fastkit.dev/auth/api)

---

## 🎓 Examples

See [`examples/`](examples/) for complete working examples:

- [**Basic JWT Auth**](examples/jwt-basic/) - Simple login/register
- [**OAuth2 Social Login**](examples/oauth2/) - Google, GitHub login
- [**RBAC System**](examples/rbac/) - Roles and permissions
- [**Multi-Device**](examples/sessions/) - Session management
- [**Complete Auth**](examples/complete/) - Production-ready setup

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- [**FastKit Core**](https://github.com/fastkit/fastkit-core) - Core framework
- [**Documentation**](https://docs.fastkit.dev/auth) - Full documentation
- [**PyPI**](https://pypi.org/project/fastkit-auth/) - Package repository
- [**Discord**](https://discord.gg/fastkit) - Community chat

---

<div align="center">
  
**Built with ❤️ by the FastKit team**

[⭐ Star us on GitHub](https://github.com/fastkit/fastkit-auth)

</div>
