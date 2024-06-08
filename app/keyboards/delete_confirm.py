from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DeleteCofirmResult(IntEnum):
    NO = auto()
    YES = auto()


class DeleteConfirmCallbackData(CallbackData, prefix="delete_confirm"):
    result: DeleteCofirmResult


def get_delete_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Нет ❌",
        callback_data=DeleteConfirmCallbackData(result=DeleteCofirmResult.NO).pack(),
    )

    builder.button(
        text="Да ✅",
        callback_data=DeleteConfirmCallbackData(result=DeleteCofirmResult.YES).pack(),
    )

    return builder.as_markup()
