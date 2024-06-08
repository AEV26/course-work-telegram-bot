from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.formatting import Bold, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.middlewares.menu_middleware import MenuStateData
from app.states.object_menu import ObjectMenuState


class ObjectMenuAction(IntEnum):
    CHANGE_NAME = auto()
    CHANGE_DESCRIPTION = auto()
    CHANGE_AREA = auto()
    RECORD_LIST = auto()
    ADD_RECORD = auto()

    DELETE_OBJECT = auto()
    GET_DOCUMENT = auto()

    CANCEL = auto()
    ENTER = auto()


class ObjectMenuCallbackData(CallbackData, prefix="object"):
    action: ObjectMenuAction


def get_object_menu_keyboard(is_new: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Изменить имя",
            callback_data=ObjectMenuCallbackData(
                action=ObjectMenuAction.CHANGE_NAME
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Изменить описание",
            callback_data=ObjectMenuCallbackData(
                action=ObjectMenuAction.CHANGE_DESCRIPTION
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Изменить площадь",
            callback_data=ObjectMenuCallbackData(
                action=ObjectMenuAction.CHANGE_AREA
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Список записей 📋",
            callback_data=ObjectMenuCallbackData(
                action=ObjectMenuAction.RECORD_LIST
            ).pack(),
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="Добавить запись ➕",
            callback_data=ObjectMenuCallbackData(
                action=ObjectMenuAction.ADD_RECORD
            ).pack(),
        )
    )

    if not is_new:
        builder.row(
            InlineKeyboardButton(
                text="Удалить объект ❌",
                callback_data=ObjectMenuCallbackData(
                    action=ObjectMenuAction.DELETE_OBJECT
                ).pack(),
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="Получить документ",
                callback_data=ObjectMenuCallbackData(
                    action=ObjectMenuAction.GET_DOCUMENT
                ).pack(),
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="Отмена ⬅️" if is_new else "Назад ⬅️",
            callback_data=ObjectMenuCallbackData(action=ObjectMenuAction.CANCEL).pack(),
        ),
        InlineKeyboardButton(
            text="Готово ✅",
            callback_data=ObjectMenuCallbackData(action=ObjectMenuAction.ENTER).pack(),
        ),
    )

    return builder.as_markup()


async def edit_text_object_menu(
    message: Message, state: FSMContext, menu: MenuStateData
):
    await _send_object_menu(message.edit_text, message, state, menu)


async def send_object_menu(message: Message, state: FSMContext, menu: MenuStateData):
    await _send_object_menu(message.answer, message, state, menu)


async def _send_object_menu(
    method, message: Message, state: FSMContext, menu: MenuStateData
):
    obj = await menu.get_object()
    is_new = await menu.is_new_object()
    name = await menu.get_object_field("new_name") or obj.name
    content = Text(
        Bold("Новый объект: " if is_new else "Объект: "),
        name,
        "\n\n",
        Bold("Описание: "),
        obj.description,
        "\n\n",
        Bold("Площадь: "),
        obj.area,
    )

    await state.set_state(ObjectMenuState.menu)
    await method(**content.as_kwargs(), reply_markup=get_object_menu_keyboard(is_new))
