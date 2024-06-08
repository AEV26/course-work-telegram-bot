from aiogram.fsm.state import StatesGroup, State


class ObjectMenuState(StatesGroup):
    menu = State()
    change_name = State()
    change_description = State()
    change_area = State()
    record_list = State()

    delete_confirm = State()
