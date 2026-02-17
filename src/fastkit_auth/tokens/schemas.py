from fastkit_core.validation import BaseSchema
from uuid import UUID
from datetime import datetime
from fastkit_auth.tokens.enums import TokenType
from pydantic import ConfigDict, field_serializer

class TokenCreate(BaseSchema):
    user_id: UUID
    token: str
    type: TokenType
    expires_at: datetime

class TokenResponse(BaseSchema):
    id: int
    user_id: UUID
    type: TokenType
    token: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('user_id')
    def serialize_uuid(self, v: UUID) -> str:
        return str(v)

    @field_serializer('expires_at')
    def serialize_dt(self, v: datetime) -> str | None:
        return v.isoformat() if v else None
