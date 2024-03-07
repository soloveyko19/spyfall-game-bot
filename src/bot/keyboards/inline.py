from database.models import Player

from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from utils.messages import LANGUAGES


def join_game_keyboard(join_key: str, bot_username: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Присоединиться!"),
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
                    text=_("Добавить локацию (для админов)"),
                    callback_data="location_option=add",
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


def confirm_mailing_keyboard():
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
