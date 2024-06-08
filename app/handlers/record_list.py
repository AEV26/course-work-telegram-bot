from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.keyboards.object_menu import edit_text_object_menu

from app.keyboards.record_list import (
    RecordListAction,
    RecordListCallbackData,
    edit_text_record_list,
)
from app.keyboards.record_menu import edit_text_record_menu, send_record_menu
from app.middlewares.menu_middleware import MenuStateData
from app.service.rent_object_service import RentObjectService


record_list_router = Router()


@record_list_router.callback_query(
    RecordListCallbackData.filter(F.action == RecordListAction.OPEN_RECORD)
)
async def open_record(
    cb: CallbackQuery,
    callback_data: RecordListCallbackData,
    state: FSMContext,
    menu: MenuStateData,
):
    await cb.answer()
    await menu.select_record(callback_data.record_index)
    await send_record_menu(cb.message, state, menu)


@record_list_router.callback_query(
    RecordListCallbackData.filter(
        F.action.in_([RecordListAction.PREV_PAGE, RecordListAction.NEXT_PAGE])
    )
)
async def prev_page(
    cb: CallbackQuery,
    callback_data: RecordListCallbackData,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    await cb.answer()
    current_page = await menu.get_current_page()

    if callback_data.action == RecordListAction.PREV_PAGE:
        current_page -= 1
    else:
        current_page += 1

    await menu.set_current_page(current_page)
    await edit_text_record_list(cb.message, state, menu, rent_object_service)


@record_list_router.callback_query(
    RecordListCallbackData.filter(F.action == RecordListAction.ADD_RECORD)
)
async def add_record(cb: CallbackQuery, state: FSMContext, menu: MenuStateData):
    await cb.answer()
    record_index = await menu.create_new_record()
    await menu.set_selected_record_index(record_index)
    await edit_text_record_menu(cb.message, state, menu)


@record_list_router.callback_query(
    RecordListCallbackData.filter(F.action == RecordListAction.CANCEL)
)
async def cancel(cb: CallbackQuery, state: FSMContext, menu: MenuStateData):
    await cb.answer()
    await edit_text_object_menu(cb.message, state, menu)
