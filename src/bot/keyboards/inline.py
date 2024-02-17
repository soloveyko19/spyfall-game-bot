from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import Player


def join_game_keyboard(join_key: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Присоединиться!",
                    url=f"https://t.me/my_spyfall_game_bot?start={join_key}",
                )
            ]
        ]
    )


def cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить! ❌", callback_data="cancel")]
        ]
    )


def link_to_bot_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️ Перейти к боту ⬅️",
                    url="https://t.me/my_spyfall_game_bot",
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
                    text="Список всех локаций",
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
