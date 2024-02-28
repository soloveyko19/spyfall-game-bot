from aiogram.fsm.state import State, StatesGroup


class LocationStates(StatesGroup):
    option = State()
    location = State()


class FeedbackStates(StatesGroup):
    feedback = State()


class AdminStates(StatesGroup):
    message_user = State()


class MailingStates(StatesGroup):
    message = State()
    button = State()
    button_url = State()
    button_text = State()
    confirm = State()
