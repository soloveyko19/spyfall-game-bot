from aiogram.fsm.state import State, StatesGroup


class LocationStates(StatesGroup):
    option = State()
    location = State()


class FeedbackStates(StatesGroup):
    feedback = State()
