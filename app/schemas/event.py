from pydantic import BaseModel


class WebSocketEvent(BaseModel):
    event: str
    data: dict

class RedisEvent(BaseModel):
    event: str
    data: dict