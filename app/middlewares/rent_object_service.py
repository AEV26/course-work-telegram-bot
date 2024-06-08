from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.service.rent_object_service import RentObjectService


class RentObjectServiceMiddleware(BaseMiddleware):
    def __init__(self, service: RentObjectService):
        self.service = service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["rent_object_service"] = self.service
        return await handler(event, data)
