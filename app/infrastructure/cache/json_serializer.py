import json
from typing import Any
from fastapi.encoders import jsonable_encoder


class JsonSerializer:
    def dumps(self, obj: Any) -> str:
        return json.dumps(jsonable_encoder(obj), default=str)

    def loads(self, data: str) -> Any:
        return json.loads(data)
