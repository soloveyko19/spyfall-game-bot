from database.models import Player

from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def join_game_keyboard(join_key: str, bot_username: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Присоединиться!",
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
                    text="Отменить! ❌",
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
                    text="➡️ Перейти к боту ⬅️",
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
                    text="Список всех локаций 📋",
                    callback_data="location_option=list",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Добавить локацию (для админов)",
                    callback_data="location_option=add",
                )
            ],
        ]
    )
