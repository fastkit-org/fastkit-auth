from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastkit_core.database import BaseWithTimestamps
from typing import Optional
from datetime import datetime

class User(BaseWithTimestamps, SQLAlchemyBaseUserTableUUID):
    __tablename__ = "users"

    __table_args__ = {'extend_existing': True}

    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    tokens: Mapped[list["UserToken"]] = relationship(
        "UserToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

