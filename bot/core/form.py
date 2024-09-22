from aiogram.fsm.state import State, StatesGroup


class Email(StatesGroup):
    email = State()
