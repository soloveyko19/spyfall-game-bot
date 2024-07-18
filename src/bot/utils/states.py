from aiogram.fsm.state import State, StatesGroup


class LocationStates(StatesGroup):
    option = State()
    location = State()


class FeedbackStates(StatesGroup):
    # for user feedback
    feedback = State()
    # for admin feedback
    feedback_option = State()
    feedback_number = State()
    answer = State()
    confirm_answer = State()


class AdminStates(StatesGroup):
    message_user = State()
    confirm_admin = State()


class MailingStates(StatesGroup):
    message = State()
    button = State()
    button_url = State()
    button_text = State()
    locale = State()
    confirm = State()


class LanguageStates(StatesGroup):
    user_locale = State()
    group_locale = State()
