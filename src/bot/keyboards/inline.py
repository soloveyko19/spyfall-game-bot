from typing import List

from database.models import Player
from utils.messages import LANGUAGES

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.i18n import gettext as _


def join_game_keyboard(join_key: str, bot_username: str, locale: str = None):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Присоединиться!", locale=locale),
                    url=f"https://t.me/{bot_username}?start={join_key}",
                )
            ]
        ]
    )


def cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Отменить! ❌"),
                    callback_data="cancel",
                )
            ]
        ]
    )


def link_to_bot_keyboard(bot_username: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("➡️ Перейти к боту ⬅️"),
                    url=f"https://t.me/{bot_username}",
                )
            ]
        ]
    )


def vote_players_keyboard(players: List[Player]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=player.user.full_name,
                    callback_data=f"voting={player.id}",
                )
            ]
            for player in players
        ]
    )


def location_options_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Список всех локаций 📋"),
                    callback_data="location_option=list",
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("Добавить локацию 🆕"),
                    callback_data="location_option=add",
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("Меню ↩️"), callback_data="cancel_admin"
                )
            ],
        ]
    )


def add_buttons_to_mailing_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Добавить ✅"), callback_data="true"
                ),
                InlineKeyboardButton(
                    text=_("Продолжить без кнопки ❎"), callback_data="false"
                ),
            ],
        ],
    )


def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Подтвердить ✅"), callback_data="confirm"
                ),
                InlineKeyboardButton(
                    text=_("Отменить ❌"), callback_data="cancel"
                ),
            ]
        ]
    )


def languages_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=language, callback_data=locale)]
            for locale, language in LANGUAGES.items()
        ]
        + [
            [
                InlineKeyboardButton(
                    text=_("Отменить ❌"), callback_data="cancel"
                )
            ]
        ]
    )


def buy_me_a_coffee_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Купить кофе разработчику"),
                    url="https://www.buymeacoffee.com/soloveyko19",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_("Меню") + " ↩️", callback_data="cancel"
                )
            ],
        ]
    )


def menu_keyboard(
    bot_username: str, for_admins: bool = False, locale: str = None
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Начать игру в новом чате ➕", locale=locale),
                    url=f"https://t.me/{bot_username}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton(
                    text=_("Язык", locale=locale) + " / Language 🌍",
                    callback_data="menu_option=language",
                ),
                InlineKeyboardButton(
                    text=_("Правила 📋", locale=locale),
                    callback_data="menu_option=rules",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_("Купить кофе ☕️", locale=locale),
                    callback_data="menu_option=coffee",
                ),
                InlineKeyboardButton(
                    text=_("Фидбэк 💬", locale=locale),
                    callback_data="menu_option=feedback",
                ),
            ],
            (
                [
                    InlineKeyboardButton(
                        text=_("Меню для админов ➡️", locale=locale),
                        callback_data="menu_option=admin_menu",
                    )
                ]
                if for_admins
                else []
            ),
        ]
    )


def admin_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Фидбэки 💬"),
                    callback_data="admin_menu_option=get_feedback",
                ),
                InlineKeyboardButton(
                    text=_("Ошибка ❗️"),
                    callback_data="admin_menu_option=error",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_("Назначить админа 🙎‍♂️"),
                    callback_data="admin_menu_option=admin",
                ),
                InlineKeyboardButton(
                    text=_("Статистика 📈"),
                    callback_data="admin_menu_option=stats",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_("Создать рассылку 🔊"),
                    callback_data="admin_menu_option=mailing",
                ),
                InlineKeyboardButton(
                    text=_("Локации 📌"),
                    callback_data="admin_menu_option=location",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_("Обычное меню ⬅️"), callback_data="cancel"
                )
            ],
        ]
    )


def statistics_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Обновить 🔄"),
                    callback_data="admin_menu_option=stats",
                ),
                InlineKeyboardButton(
                    text=_("Меню ↩️"), callback_data="cancel_admin"
                ),
            ]
        ]
    )


def back_to_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("Меню ↩️"), callback_data="cancel")]
        ]
    )


def back_to_admin_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Меню ↩️"), callback_data="cancel_admin"
                )
            ]
        ]
    )
