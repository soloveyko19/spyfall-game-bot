from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUser,
)
from aiogram.utils.i18n import gettext as _


def request_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=_("Выбрать пользователя 👤"),
                    request_user=KeyboardButtonRequestUser(
                        user_is_bot=False, request_id=0
                    ),
                ),
                KeyboardButton(
                    text=_("Отменить! ❌"),
                ),
            ]
        ],
        resize_keyboard=True,
    )
