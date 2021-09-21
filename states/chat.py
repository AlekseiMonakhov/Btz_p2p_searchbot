from aiogram.dispatcher.filters.state import StatesGroup, State


class SetChat(StatesGroup):
    wait_input_num = State()
    wait_confirm = State()
