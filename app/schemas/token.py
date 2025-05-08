from datetime import datetime

from pydantic import BaseModel


class TokenRead(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: str
    token_type: str
    jti: str


class CreatedTokenInfo(BaseModel):
    token: str
    expires_at: datetime
    jti: str


class TokenPairInfo(BaseModel):
    access_token_info: CreatedTokenInfo
    refresh_token_info: CreatedTokenInfo



