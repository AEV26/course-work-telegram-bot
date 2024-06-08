from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from app.service.models.record import Record

from app.service.models.rent_object import RentObject


class MenuStateData:
    def __init__(self, state: FSMContext):
        self.state = state

    async def get_data(self) -> dict:
        return await self.state.get_data()

    async def set_data(self, data: dict):
        await self.state.set_data(data)

    async def set_object(self, obj: RentObject, is_new: bool):
        data = await self.get_data()
        data["object"] = obj.to_dict()
        data["object"]["new"] = is_new

        await self.set_data(data)

    async def is_new_object(self):
        data = await self.get_data()
        return data["object"]["new"] is True

    async def create_new_object(self):
        await self.set_object(RentObject(), True)

    async def get_object(self) -> RentObject:
        data = await self.get_data()
        object_data = data["object"]
        return RentObject.from_dict(object_data)

    async def set_object_field(self, key: str, value):
        data = await self.get_data()
        data["object"][key] = value
        await self.set_data(data)

    async def get_object_field(self, key: str):
        data = await self.get_data()
        return data["object"].get(key)

    async def set_object_name(self, name: str):
        await self.set_object_field("name", name)

    async def set_object_description(self, description: str):
        await self.set_object_field("description", description)

    async def set_object_area(self, area: float):
        await self.set_object_field("area", area)

    async def create_new_record(self) -> int:
        return await self.add_record_to_object(Record(), True)

    async def get_selected_record(self) -> Record:
        data = await self.get_data()
        record_index = await self.get_selected_record_index()
        record_data = data["object"]["records"][record_index]
        return Record.from_dict(record_data)

    async def set_selected_record_field(self, key: str, value: Any):
        data = await self.get_data()
        record_index = await self.get_selected_record_index()
        data["object"]["records"][record_index][key] = value
        await self.set_data(data)

    async def add_record_to_object(self, record: Record, is_new: bool) -> int:
        data = await self.get_data()
        data["object"]["records"].append(record.to_dict())
        data["object"]["records"][-1]["is_new"] = is_new
        await self.set_data(data)
        return len(data["object"]["records"]) - 1

    async def is_new_record(self, record_index: int) -> bool:
        data = await self.get_data()
        return data["object"]["records"][record_index].get("is_new") is True

    async def is_updated_record(self, record_index: int) -> int:
        data = await self.get_data()
        return data["object"]["records"][record_index].get("is_updated") is True

    async def select_record(self, record_index: int):
        await self.set_selected_record_index(record_index)

    async def set_selected_record_index(self, record_index: int):
        data = await self.get_data()
        data["selected_record_index"] = record_index
        await self.set_data(data)

    async def get_selected_record_index(self):
        data = await self.get_data()
        return data["selected_record_index"]

    async def delete_selected_record(self):
        data = await self.get_data()
        record_index = await self.get_selected_record_index()
        data["object"]["records"].pop(record_index)
        await self.set_data(data)

    async def update_selected_record(self, record: Record):
        data = await self.get_data()
        record_index = await self.get_selected_record_index()
        data["object"]["records"][record_index] = record.to_dict()
        data["object"]["records"][record_index]["is_updated"] = True
        data["object"]["records"].sort(key=lambda x: x["date"])
        await self.set_data(data)

    async def get_current_page(self) -> int:
        data = await self.get_data()
        return data["current_page"]

    async def set_current_page(self, page: int) -> None:
        data = await self.get_data()
        data["current_page"] = page
        await self.set_data(data)


class MenuMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["menu"] = MenuStateData(data["state"])
        return await handler(event, data)
