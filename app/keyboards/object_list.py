from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.service.models.rent_object import RentObject
from app.service.rent_object_service import RentObjectService


class ObjectListAction(IntEnum):
    CREATE_OBJECT = auto()
    OPEN_OBJECT = auto()


class ObjectListCallbackData(CallbackData, prefix="object_menu"):
    object_name: str
    action: ObjectListAction


def get_objects_menu_keyboard(objects: list[RentObject]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for obj in objects:
        if len(obj.name) > 40:
            raise Exception("Name of object is too long", obj)

        builder.row(
            InlineKeyboardButton(
                text=obj.name,
                callback_data=ObjectListCallbackData(
                    object_name=obj.name, action=ObjectListAction.OPEN_OBJECT
                ).pack(),
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="Добавить объект ➕",
            callback_data=ObjectListCallbackData(
                object_name="", action=ObjectListAction.CREATE_OBJECT
            ).pack(),
        )
    )

    return builder.as_markup()


async def edit_text_object_list(
    message: Message, state: FSMContext, rent_object_service: RentObjectService
):
    await _send_object_list(message.edit_text, message, state, rent_object_service)


async def send_object_list(
    message: Message, state: FSMContext, rent_object_service: RentObjectService
):
    await _send_object_list(message.answer, message, state, rent_object_service)


async def _send_object_list(
    method, message: Message, state: FSMContext, rent_object_service: RentObjectService
):
    await state.set_state(None)

    try:
        objects = await rent_object_service.get_all(message.chat.id)
    except Exception as e:
        await message.answer(text="Error: " + str(e))
        return

    await method("Меню", reply_markup=get_objects_menu_keyboard(objects))
