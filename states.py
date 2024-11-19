from aiogram.fsm.state import StatesGroup, State


class PaymentState(StatesGroup):
    region = State()
    user_id = State()
    user = State()
    price = State()
    check = State()
