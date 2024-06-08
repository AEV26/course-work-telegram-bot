from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.object_list import (
    ObjectListCallbackData,
    ObjectListAction,
    send_object_list,
)
from app.keyboards.object_menu import edit_text_object_menu

from app.middlewares.menu_middleware import MenuStateData
from app.service.rent_object_service import RentObjectService


object_list_router = Router()


@object_list_router.message(CommandStart())
async def start_bot(
    message: Message, state: FSMContext, rent_object_service: RentObjectService
):
    await send_object_list(message, state, rent_object_service)


@object_list_router.callback_query(
    ObjectListCallbackData.filter(F.action == ObjectListAction.CREATE_OBJECT)
)
async def create_object(cb: CallbackQuery, state: FSMContext, menu: MenuStateData):
    await cb.answer()

    await menu.create_new_object()

    await edit_text_object_menu(cb.message, state, menu)


@object_list_router.callback_query(
    ObjectListCallbackData.filter(F.action == ObjectListAction.OPEN_OBJECT)
)
async def open_object(
    cb: CallbackQuery,
    callback_data: ObjectListCallbackData,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    rent_object = await rent_object_service.get_by_name(
        cb.from_user.id, callback_data.object_name
    )

    await menu.set_object(rent_object, False)

    await edit_text_object_menu(cb.message, state, menu)
