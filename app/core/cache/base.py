from abc import ABC, abstractmethod
from typing import Protocol, Any


class Serializer(Protocol):
    def dumps(self, obj: Any) -> str: ...
    def loads(self, data: str) -> Any: ...


class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> Any: ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 60) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...
