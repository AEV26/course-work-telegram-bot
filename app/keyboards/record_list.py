from enum import IntEnum, auto
import math
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.formatting import Bold, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.middlewares.menu_middleware import MenuStateData
from app.service.create_xlsx_document import format_date

from app.service.models.record import Record
from app.service.rent_object_service import RentObjectService
from app.states.object_menu import ObjectMenuState


RECORDS_ON_PAGE = 8


class RecordListAction(IntEnum):
    OPEN_RECORD = auto()
    ADD_RECORD = auto()
    PREV_PAGE = auto()
    NEXT_PAGE = auto()

    CANCEL = auto()


class RecordListCallbackData(CallbackData, prefix="record_list"):
    record_index: int = 0
    action: RecordListAction


def get_record_list_keyboard(records: list[Record], page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    RECORDS_COUNT = len(records)
    PAGES_COUNT = math.ceil(RECORDS_COUNT / RECORDS_ON_PAGE)
    reversed = records[::-1]
    records_on_page = reversed[page * RECORDS_ON_PAGE : (page + 1) * RECORDS_ON_PAGE]

    for index, record in enumerate(records_on_page):
        builder.button(
            text=f"Дата: {format_date(record.date)}",
            callback_data=RecordListCallbackData(
                record_index=RECORDS_COUNT - 1 - page * RECORDS_ON_PAGE - index,
                action=RecordListAction.OPEN_RECORD,
            ).pack(),
        )

    builder.adjust(1)

    pagination_buttons = []
    if page != 0:
        prev_page_button = InlineKeyboardButton(
            text=f"{page} ⬅️",
            callback_data=RecordListCallbackData(
                action=RecordListAction.PREV_PAGE
            ).pack(),
        )
        pagination_buttons.append(prev_page_button)

    if page + 1 < PAGES_COUNT:
        next_page_button = InlineKeyboardButton(
            text=f"➡️ {page+2}",
            callback_data=RecordListCallbackData(
                action=RecordListAction.NEXT_PAGE
            ).pack(),
        )
        pagination_buttons.append(next_page_button)
    builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text="Добавить запись ➕",
            callback_data=RecordListCallbackData(
                action=RecordListAction.ADD_RECORD
            ).pack(),
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="Назад ⬅️",
            callback_data=RecordListCallbackData(action=RecordListAction.CANCEL).pack(),
        )
    )

    return builder.as_markup()


async def edit_text_record_list(
    message: Message,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    await _send_record_list(
        message.edit_text, message, state, menu, rent_object_service
    )


async def send_record_list(
    message: Message,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    await _send_record_list(message.answer, message, state, menu, rent_object_service)


async def _send_record_list(
    method,
    message: Message,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    obj = await menu.get_object()
    is_new = await menu.is_new_object()
    if is_new:
        records = obj.records
    else:
        records = await rent_object_service.get_all_records(message.chat.id, obj.name)

    content = Text(
        Bold("Список записей"),
        "\n",
        Bold("Новый объект: " if is_new else "Объект: "),
        obj.name,
        "\n\n",
        Bold("Описание: "),
        obj.description,
        "\n\n",
        Bold("Площадь: "),
        obj.area,
    )
    current_page = await menu.get_current_page()
    await state.set_state(ObjectMenuState.record_list)
    await method(
        **content.as_kwargs(),
        reply_markup=get_record_list_keyboard(records, current_page),
    )
