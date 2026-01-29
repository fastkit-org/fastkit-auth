from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastkit_core.database import BaseWithTimestamps, IntIdMixin
from fastkit_auth.tokens.enums import TokenType
from fastkit_auth.users.models import User
from datetime import datetime
from uuid import UUID
import secrets


class UserToken(IntIdMixin, BaseWithTimestamps):
    __tablename__ = "user_tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    type: Mapped[TokenType] = mapped_column(SQLEnum(TokenType))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationship
    user: Mapped[User] = relationship("User", back_populates="tokens")

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)

    def is_valid(self) -> bool:
        return self.expires_at > datetime.now()
