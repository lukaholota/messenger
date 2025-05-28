from typing import Dict, Awaitable, Callable


EventCallback = Callable[[Dict], Awaitable[None]]
EventHandlerMap = Dict[str, EventCallback]
