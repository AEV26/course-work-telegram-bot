from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.formatting import Bold, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.middlewares.menu_middleware import MenuStateData
from app.service.create_xlsx_document import format_date

from app.service.models.record import Record
from app.states.record_menu import RecordMenuState


class RecordMenuAction(IntEnum):
    CHANGE_DATE = auto()
    CHANGE_RENT = auto()
    CHANGE_HEAT = auto()
    CHANGE_EXPLOITATION = auto()
    CHANGE_MOP = auto()
    CHANGE_RENOVATION = auto()
    CHANGE_TBO = auto()
    CHANGE_ELECTRICITY = auto()
    CHANGE_EARTHRENT = auto()
    CHANGE_OTHER = auto()
    CHANGE_SECURITY = auto()

    DELETE = auto()

    CANCEL = auto()
    ENTER = auto()


class RecordMenuCallbackData(CallbackData, prefix="record_data"):
    action: RecordMenuAction


def get_create_record_keyboard(
    record: Record, is_new: bool = False
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Дата: {format_date(record.date)}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_DATE
        ).pack(),
    )
    builder.button(
        text=f"Аренда: {record.rent}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_RENT
        ).pack(),
    )
    builder.button(
        text=f"Тепло: {record.heat}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_HEAT
        ).pack(),
    )
    builder.button(
        text=f"Содержание: {record.exploitation}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_EXPLOITATION
        ).pack(),
    )
    builder.button(
        text=f"МОП: {record.mop}",
        callback_data=RecordMenuCallbackData(action=RecordMenuAction.CHANGE_MOP).pack(),
    )
    builder.button(
        text=f"Капремнот: {record.renovation}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_RENOVATION
        ).pack(),
    )
    builder.button(
        text=f"ТБО: {record.tbo}",
        callback_data=RecordMenuCallbackData(action=RecordMenuAction.CHANGE_TBO).pack(),
    )
    builder.button(
        text=f"Эл. счётчик: {record.electricity}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_ELECTRICITY
        ).pack(),
    )
    builder.button(
        text=f"Аренда земли: {record.earth_rent}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_EARTHRENT
        ).pack(),
    )
    builder.button(
        text=f"Прочие расходы: {record.other}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_OTHER
        ).pack(),
    )
    builder.button(
        text=f"Охрана: {record.security}",
        callback_data=RecordMenuCallbackData(
            action=RecordMenuAction.CHANGE_SECURITY
        ).pack(),
    )

    if not is_new:
        builder.button(
            text="Удалить запись ❌",
            callback_data=RecordMenuCallbackData(action=RecordMenuAction.DELETE).pack(),
        )

    builder.button(
        text="Отмена ⬅️" if is_new else "Назад ⬅️",
        callback_data=RecordMenuCallbackData(action=RecordMenuAction.CANCEL).pack(),
    )

    builder.adjust(1)

    builder.button(
        text="Готово ✅",
        callback_data=RecordMenuCallbackData(action=RecordMenuAction.ENTER).pack(),
    )

    return builder.as_markup()


async def edit_text_record_menu(
    message: Message, state: FSMContext, menu: MenuStateData
):
    await _send_record_menu(message.edit_text, message, state, menu)


async def send_record_menu(message: Message, state: FSMContext, menu: MenuStateData):
    await _send_record_menu(message.answer, message, state, menu)


async def _send_record_menu(
    method, message: Message, state: FSMContext, menu: MenuStateData
):
    record = await menu.get_selected_record()
    obj = await menu.get_object()
    is_new_object = await menu.is_new_object()
    record_index = await menu.get_selected_record_index()
    is_new_record = await menu.is_new_record(record_index)
    content = Text(
        Bold("Добавление записи" if is_new_record else "Изменение записи"),
        "\n",
        Bold("Новый объект: " if is_new_object else "Объект: "),
        obj.name,
        "\n\n",
        Bold("Описание: "),
        obj.description,
        "\n\n",
        Bold("Площадь: "),
        obj.area,
    )

    await state.set_state(RecordMenuState.menu)
    await method(
        **content.as_kwargs(),
        reply_markup=get_create_record_keyboard(record, is_new_record),
    )
