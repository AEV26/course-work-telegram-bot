from aiogram import Router
from .object_list import object_list_router
from .object_menu import object_menu_router
from .record_menu import record_menu_router
from .record_list import record_list_router

main_router = Router()
main_router.include_routers(
    object_list_router,
    object_menu_router,
    record_menu_router,
    record_list_router,
)
