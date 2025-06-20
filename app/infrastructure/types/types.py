from typing import Awaitable, Callable, TypeVar

from pydantic import BaseModel


DTO_Type = TypeVar('DTO_Type', bound=BaseModel)
EventCallback = Callable[[DTO_Type, int | None], Awaitable[None]]
