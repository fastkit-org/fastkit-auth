from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastkit_core.database import BaseWithTimestamps, IntIdMixin
from fastkit_auth.tokens.enums import TokenType
from datetime import datetime, timezone
from uuid import UUID
import random
import string


class UserToken(BaseWithTimestamps, IntIdMixin):
    __tablename__ = "user_tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    type: Mapped[TokenType] = mapped_column(SQLEnum(TokenType))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    @staticmethod
    def generate_token(length: int = 8) -> str:
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=length))

    def is_valid(self) -> bool:
        return self.expires_at > datetime.now(timezone.utc)
