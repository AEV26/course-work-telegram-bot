from datetime import timezone
import dateparser
import pytz
from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.keyboards.delete_confirm import (
    DeleteCofirmResult,
    DeleteConfirmCallbackData,
    get_delete_confirm_keyboard,
)
from app.keyboards.object_menu import edit_text_object_menu

from app.keyboards.record_menu import (
    RecordMenuAction,
    RecordMenuCallbackData,
    edit_text_record_menu,
    send_record_menu,
)
from app.middlewares.menu_middleware import MenuStateData
from app.service.models.record import Record, UpdateRecordInput
from app.service.rent_object_service import RentObjectService
from app.states.object_menu import ObjectMenuState
from app.states.record_menu import RecordMenuState

record_menu_router = Router()


MENU_ACTION_TO_STATE_AND_MESSAGE = {
    RecordMenuAction.CHANGE_DATE: (
        RecordMenuState.change_date,
        "Введите дату в формате МЕСЯЦ.ГОД",
    ),
    RecordMenuAction.CHANGE_RENT: (RecordMenuState.change_rent, "Введите аренду"),
    RecordMenuAction.CHANGE_HEAT: (
        RecordMenuState.change_heat,
        "Введите затраты на тепло",
    ),
    RecordMenuAction.CHANGE_EXPLOITATION: (
        RecordMenuState.change_exploitation,
        "Введите затраты на  содержание",
    ),
    RecordMenuAction.CHANGE_MOP: (RecordMenuState.change_mop, "Введите затраты на МОП"),
    RecordMenuAction.CHANGE_RENOVATION: (
        RecordMenuState.change_renovation,
        "Введите затраты капремонт",
    ),
    RecordMenuAction.CHANGE_TBO: (
        RecordMenuState.change_tbo,
        "Введите затраты на  ТБО",
    ),
    RecordMenuAction.CHANGE_ELECTRICITY: (
        RecordMenuState.change_electricity,
        "Введите затраты на электирику счётчик",
    ),
    RecordMenuAction.CHANGE_EARTHRENT: (
        RecordMenuState.change_earthrent,
        "Введите затраты на аренду земли",
    ),
    RecordMenuAction.CHANGE_OTHER: (
        RecordMenuState.change_other,
        "Введите затраты на прочие расходы",
    ),
    RecordMenuAction.CHANGE_SECURITY: (
        RecordMenuState.change_security,
        "Введите затраты на охрану",
    ),
}

FIELD_NAME_BY_STATE = {
    RecordMenuState.change_rent: "rent",
    RecordMenuState.change_heat: "heat",
    RecordMenuState.change_exploitation: "exploitation",
    RecordMenuState.change_mop: "mop",
    RecordMenuState.change_renovation: "renovation",
    RecordMenuState.change_tbo: "tbo",
    RecordMenuState.change_electricity: "electricity",
    RecordMenuState.change_earthrent: "earth_rent",
    RecordMenuState.change_other: "other",
    RecordMenuState.change_security: "security",
}


@record_menu_router.callback_query(
    RecordMenuCallbackData.filter(
        F.action.in_(
            [
                RecordMenuAction.CHANGE_DATE,
                RecordMenuAction.CHANGE_RENT,
                RecordMenuAction.CHANGE_HEAT,
                RecordMenuAction.CHANGE_EXPLOITATION,
                RecordMenuAction.CHANGE_MOP,
                RecordMenuAction.CHANGE_RENOVATION,
                RecordMenuAction.CHANGE_TBO,
                RecordMenuAction.CHANGE_ELECTRICITY,
                RecordMenuAction.CHANGE_EARTHRENT,
                RecordMenuAction.CHANGE_OTHER,
                RecordMenuAction.CHANGE_SECURITY,
            ]
        )
    )
)
async def change_param(
    cb: CallbackQuery,
    callback_data: RecordMenuCallbackData,
    state: FSMContext,
):
    await cb.answer()
    field_change_state, message = MENU_ACTION_TO_STATE_AND_MESSAGE[callback_data.action]

    await state.set_state(field_change_state)
    await cb.message.answer(message)


@record_menu_router.message(RecordMenuState.change_date, F.text)
async def set_date(message: Message, state: FSMContext, menu: MenuStateData):
    date = message.text or ""
    try:
        date = dateparser.parse(date, date_formats=["%m.%y", "%m.%Y"])

        if date is None:
            raise Exception()

        date = pytz.utc.localize(date)
    except Exception:
        await message.answer("Неверный формат!")
        return
    date = date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    await menu.set_selected_record_field("date", date)
    await send_record_menu(message, state, menu)


@record_menu_router.message(
    or_f(
        RecordMenuState.change_rent,
        RecordMenuState.change_heat,
        RecordMenuState.change_exploitation,
        RecordMenuState.change_mop,
        RecordMenuState.change_renovation,
        RecordMenuState.change_tbo,
        RecordMenuState.change_electricity,
        RecordMenuState.change_earthrent,
        RecordMenuState.change_other,
        RecordMenuState.change_security,
    ),
    F.text,
)
async def set_numeric_param(message: Message, state: FSMContext, menu: MenuStateData):
    value = message.text
    try:
        value = float(value)
    except Exception:
        await message.answer("Введите число!")
        return

    current_state = await state.get_state()

    field_name = FIELD_NAME_BY_STATE[current_state]

    await menu.set_selected_record_field(field_name, value)

    await send_record_menu(message, state, menu)


@record_menu_router.callback_query(
    RecordMenuCallbackData.filter(F.action == RecordMenuAction.DELETE)
)
async def delete(
    cb: CallbackQuery,
    state: FSMContext,
):
    await cb.answer()
    await state.set_state(RecordMenuState.delete_confirm)
    await cb.message.edit_text(
        "Вы точно хотите удалить запись?", reply_markup=get_delete_confirm_keyboard()
    )


@record_menu_router.callback_query(
    RecordMenuState.delete_confirm,
    DeleteConfirmCallbackData.filter(F.result == DeleteCofirmResult.NO),
)
async def delete_no(
    cb: CallbackQuery,
    state: FSMContext,
    menu: MenuStateData,
):
    await cb.answer()
    await state.set_state(RecordMenuState.menu)
    await edit_text_record_menu(cb.message, state, menu)


@record_menu_router.callback_query(
    RecordMenuState.delete_confirm,
    DeleteConfirmCallbackData.filter(F.result == DeleteCofirmResult.YES),
)
async def delete_yes(
    cb: CallbackQuery,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    await cb.answer()
    obj = await menu.get_object()
    record_index = await menu.get_selected_record_index()

    if await menu.is_new_object():
        await menu.delete_selected_record()
    else:
        await rent_object_service.delete_record(cb.from_user.id, obj.name, record_index)

    await state.set_state(ObjectMenuState.menu)
    await edit_text_object_menu(cb.message, state, menu)


@record_menu_router.callback_query(
    RecordMenuCallbackData.filter(F.action == RecordMenuAction.CANCEL)
)
async def cancel(cb: CallbackQuery, state: FSMContext, menu: MenuStateData):
    await cb.answer()
    record_index = await menu.get_selected_record_index()
    if await menu.is_new_record(record_index):
        await menu.delete_selected_record()

    await state.set_state(ObjectMenuState.menu)
    await edit_text_object_menu(cb.message, state, menu)


@record_menu_router.callback_query(
    RecordMenuCallbackData.filter(F.action == RecordMenuAction.ENTER)
)
async def enter(
    cb: CallbackQuery,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    await cb.answer()

    record = await menu.get_selected_record()

    obj = await menu.get_object()
    record_index = await menu.get_selected_record_index()
    if not await menu.is_new_object():
        if await menu.is_new_record(record_index):
            await rent_object_service.add_record(cb.from_user.id, obj.name, record)

        else:
            update_input = get_update_record_input(record)
            await rent_object_service.update_record(
                cb.from_user.id, obj.name, record_index, update_input
            )

    await menu.update_selected_record(record)

    await state.set_state(ObjectMenuState.menu)
    await edit_text_object_menu(cb.message, state, menu)


def get_update_record_input(record: Record) -> UpdateRecordInput:
    return UpdateRecordInput(
        date=record.date,
        rent=record.rent,
        heat=record.heat,
        exploitation=record.exploitation,
        mop=record.mop,
        renovation=record.renovation,
        tbo=record.tbo,
        electricity=record.electricity,
        earth_rent=record.earth_rent,
        other=record.other,
        security=record.security,
    )
