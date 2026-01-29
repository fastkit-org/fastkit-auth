from fastkit_core.validation import BaseSchema
from uuid import UUID
from datetime import datetime
from fastkit_auth.tokens.enums import TokenType
from pydantic import ConfigDict

class TokenCreate(BaseSchema):
    user_id: UUID
    token: str
    type: TokenType
    expires_at: datetime

class TokenResponse(BaseSchema):
    id: int
    user_id: UUID
    type: TokenType
    expires_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }
    )
