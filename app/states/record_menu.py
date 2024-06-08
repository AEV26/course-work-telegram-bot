from aiogram.fsm.state import State, StatesGroup


class RecordMenuState(StatesGroup):
    menu = State()
    change_date = State()
    change_rent = State()
    change_heat = State()
    change_exploitation = State()
    change_mop = State()
    change_renovation = State()
    change_tbo = State()
    change_electricity = State()
    change_earthrent = State()
    change_other = State()
    change_security = State()

    delete_confirm = State()
