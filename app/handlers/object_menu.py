import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext
from app.keyboards.delete_confirm import (
    DeleteCofirmResult,
    DeleteConfirmCallbackData,
    get_delete_confirm_keyboard,
)
from app.keyboards.object_menu import edit_text_object_menu, send_object_menu

from app.keyboards.object_list import (
    edit_text_object_list,
    send_object_list,
)

from app.keyboards.object_menu import (
    ObjectMenuAction,
    ObjectMenuCallbackData,
)
from app.keyboards.record_list import edit_text_record_list
from app.keyboards.record_menu import edit_text_record_menu
from app.middlewares.menu_middleware import MenuStateData
from app.service.create_xlsx_document import (
    RentObjectXLSXWriter,
)
from app.service.models.rent_object import UpdateRentObjectInput
from app.service.rent_object_service import RentObjectService
from app.states.object_menu import ObjectMenuState


object_menu_router = Router()


@object_menu_router.callback_query(
    ObjectMenuCallbackData.filter(
        F.action.in_(
            [
                ObjectMenuAction.CHANGE_NAME,
                ObjectMenuAction.CHANGE_DESCRIPTION,
                ObjectMenuAction.CHANGE_AREA,
            ]
        )
    )
)
async def change_name(
    cb: CallbackQuery, callback_data: ObjectMenuCallbackData, state: FSMContext
):
    await cb.answer()
    match callback_data.action:
        case ObjectMenuAction.CHANGE_NAME:
            change_state = ObjectMenuState.change_name
            message = "Введите название объекта"
        case ObjectMenuAction.CHANGE_DESCRIPTION:
            change_state = ObjectMenuState.change_description
            message = "Введите описание объекта"
        case ObjectMenuAction.CHANGE_AREA:
            change_state = ObjectMenuState.change_area
            message = "Введите площадь объекта"
        case _:
            raise Exception()

    await state.set_state(change_state)
    await cb.message.answer(message)


@object_menu_router.message(ObjectMenuState.change_name, F.text)
async def set_name(
    message: Message,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    name = message.text or ""
    if name == "":
        await message.answer("Имя объекта не может быть пустым")
        return
    if len(name) > 40:
        await message.answer("Имя объекта слишком длинное")
        return

    is_new = await menu.is_new_object()
    obj = await menu.get_object()

    await menu.set_object_name(name)

    if not is_new:
        last_name = obj.name
        await rent_object_service.update_object(
            message.chat.id, last_name, UpdateRentObjectInput(name=name)
        )

    await send_object_menu(message, state, menu)


@object_menu_router.message(ObjectMenuState.change_description, F.text)
async def set_description(
    message: Message,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    description = message.text or ""
    await menu.set_object_description(description)

    is_new = await menu.is_new_object()
    obj = await menu.get_object()
    if not is_new:
        await rent_object_service.update_object(
            message.chat.id, obj.name, UpdateRentObjectInput(description=description)
        )

    await send_object_menu(message, state, menu)


@object_menu_router.message(ObjectMenuState.change_area, F.text)
async def set_area(
    message: Message,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    area = message.text or ""

    try:
        area = float(area)
    except Exception:
        await message.answer("Введите число!")
        return
    await menu.set_object_area(area)

    is_new = await menu.is_new_object()
    obj = await menu.get_object()
    if not is_new:
        await rent_object_service.update_object(
            message.chat.id, obj.name, UpdateRentObjectInput(area=area)
        )

    await send_object_menu(message, state, menu)


@object_menu_router.callback_query(
    ObjectMenuCallbackData.filter(F.action == ObjectMenuAction.RECORD_LIST)
)
async def record_list(
    cb: CallbackQuery,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    await state.set_state(ObjectMenuState.record_list)
    await menu.set_current_page(0)
    await edit_text_record_list(cb.message, state, menu, rent_object_service)


@object_menu_router.callback_query(
    ObjectMenuCallbackData.filter(F.action == ObjectMenuAction.DELETE_OBJECT)
)
async def delete_object(
    cb: CallbackQuery,
    state: FSMContext,
):
    await cb.answer()

    await cb.answer()
    await state.set_state(ObjectMenuState.delete_confirm)
    await cb.message.edit_text(
        "Вы точно хотите удалить объект?", reply_markup=get_delete_confirm_keyboard()
    )


@object_menu_router.callback_query(
    ObjectMenuState.delete_confirm,
    DeleteConfirmCallbackData.filter(F.result == DeleteCofirmResult.NO),
)
async def delete_no(
    cb: CallbackQuery,
    state: FSMContext,
    menu: MenuStateData,
):
    await cb.answer()
    await state.set_state(ObjectMenuState.menu)
    await edit_text_object_menu(cb.message, state, menu)


@object_menu_router.callback_query(
    ObjectMenuState.delete_confirm,
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
    await rent_object_service.delete_object(cb.from_user.id, obj.name)
    await edit_text_object_list(cb.message, state, rent_object_service)


@object_menu_router.callback_query(
    ObjectMenuCallbackData.filter(F.action == ObjectMenuAction.ADD_RECORD)
)
async def add_record(cb: CallbackQuery, state: FSMContext, menu: MenuStateData):
    await cb.answer()
    record_index = await menu.create_new_record()
    await menu.set_selected_record_index(record_index)
    await edit_text_record_menu(cb.message, state, menu)


@object_menu_router.callback_query(
    ObjectMenuCallbackData.filter(F.action == ObjectMenuAction.GET_DOCUMENT)
)
async def get_document(
    cb: CallbackQuery,
    state: FSMContext,
    menu: MenuStateData,
    rent_object_service: RentObjectService,
):
    await cb.answer()
    obj = await menu.get_object()
    object_info = await rent_object_service.get_object_info(cb.from_user.id, obj.name)
    object_path = RentObjectXLSXWriter().create(object_info)

    await cb.message.answer_document(FSInputFile(object_path))
    await send_object_list(cb.message, state, rent_object_service)
    os.remove(object_path)


@object_menu_router.callback_query(
    ObjectMenuCallbackData.filter(F.action == ObjectMenuAction.CANCEL)
)
async def cancel_object(
    cb: CallbackQuery, state: FSMContext, rent_object_service: RentObjectService
):
    await cb.answer()

    await edit_text_object_list(cb.message, state, rent_object_service)


@object_menu_router.callback_query(
    ObjectMenuCallbackData.filter(F.action == ObjectMenuAction.ENTER)
)
async def enter_object(
    cb: CallbackQuery,
    state: FSMContext,
    rent_object_service: RentObjectService,
    menu: MenuStateData,
):
    await cb.answer()

    obj = await menu.get_object()
    name = await menu.get_object_field("new_name") or obj.name

    if name == "":
        await cb.message.answer("Имя объекта не может быть пустым")
        return

    is_new = await menu.is_new_object()
    if is_new:
        await rent_object_service.add_object(cb.from_user.id, obj)

    await edit_text_object_list(cb.message, state, rent_object_service)
