from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUser,
)


def request_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Выбрать пользователя 👤",
                    request_user=KeyboardButtonRequestUser(
                        user_is_bot=False, request_id=0
                    ),
                ),
                KeyboardButton(
                    text="Отменить! ❌",
                ),
            ]
        ],
        resize_keyboard=True,
    )
