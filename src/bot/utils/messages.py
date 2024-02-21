from database.models import Player

import asyncio
from typing import List

from aiogram import types


def join_message(players: List[Player] = None, seconds: int = None):
    msg = "*Набор в игру\\!* 🔊\n"
    if seconds:
        msg += f"Осталось _{seconds}_ секунд\\!⏳"
    if players:
        msg += "\n\n*Присоединившиеся участники:* "
        players_links = []
        for player in players:
            players_links.append(
                f"[{escape_markdown_v2(player.user.full_name)}](tg://user?id={player.user.tg_id})"
            )
        msg += ", ".join(players_links)
        msg += (
            f"\n\n_Всего {len(players)} участник\\(\\-ов\\)\\. 👤_"
        )
    return msg


def discussion_message(players: List[Player]) -> str:
    return (
            f"*Начинается обсуждение\\! 🗣*\n_Игра будет длиться: {len(players)} минут\\(\\-ы\\) ⏳_\n\n*Игроки:*\n"
            + ",\n".join(
        [
            f"[{escape_markdown_v2(player.user.full_name)}](tg://user?id={player.user.tg_id})"
            for player in players
        ]
    )
            + f"\n\n_Всего {len(players)} участников\\. 👤_"
    )


async def update_message(
        message_id, message_chat_id, new_message, reply_markup=None
):
    from main import bot

    message = await bot.edit_message_text(
        text=new_message,
        chat_id=message_chat_id,
        message_id=message_id,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )
    return message


async def send_message(
        chat_id: int, text: str, reply_markup=None, parse_mode=None
):
    from main import bot

    message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )
    return message


async def delete_message(message: types.Message):
    await message.delete()


async def delete_all_messages(messages: List[types.Message]):
    tasks = [delete_message(message) for message in messages]
    await asyncio.gather(*tasks)


def escape_markdown_v2(text: str) -> str:
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, '\\' + char)
    return text
