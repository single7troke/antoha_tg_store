from aiogram.fsm.state import State, StatesGroup


class Email(StatesGroup):
    email = State()


class UserId(StatesGroup):
    user_id = State()


class PaymentId(StatesGroup):
    payment_id = State()


class GrantAccessToUser(StatesGroup):
    user_id = State()


class ExtendAccessToUser(StatesGroup):
    user_id = State()
