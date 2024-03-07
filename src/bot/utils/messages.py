from database.models import Player, User

import asyncio
from typing import List

from aiogram import types, Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.utils.i18n import gettext as _


LANGUAGES = {"en": "English 🇬🇧", "uk": "Українська 🇺🇦", "ru": "Русский"}


def join_message(players: List[Player] = None, seconds: int = None, locale: str = None) -> str:
    msg = _("*Набор в игру\\!* 🔊\n", locale=locale)
    if seconds:
        msg += _(f"Осталось _{seconds}_ секунд\\!⏳", locale=locale)
    if players:
        msg += _("\n\n*Присоединившиеся участники:* ", locale=locale)
        players_links = []
        for player in players:
            players_links.append(
                f"[{escape_markdown_v2(player.user.full_name)}](tg://user?id={player.user.tg_id})"
            )
        msg += ", ".join(players_links)
        msg += _(
            "\n\n_Всего {players_count} участник\\(\\-ов\\)\\. 👤_", locale=locale
        ).format(players_count=len(players))
    return msg


def discussion_message(players: List[Player]) -> str:
    return (
        _(
            "*Начинается обсуждение\\! 🗣*\n_Игра будет длиться: {min} минут\\(\\-ы\\) ⏳_\n\n*Игроки:*\n"
        ).format(min=len(players))
        + ",\n".join(
            [
                f"[{escape_markdown_v2(player.user.full_name)}](tg://user?id={player.user.tg_id})"
                for player in players
            ]
        )
        + _("\n\n_Всего {players_count} участников\\. 👤_").format(
            players_count=len(players)
        )
    )


async def delete_message(message: types.Message):
    await message.delete()


async def delete_all_messages(messages: List[types.Message]):
    tasks = [delete_message(message) for message in messages]
    await asyncio.gather(*tasks)


async def copy_message_mailing(
    bot: Bot,
    chat_id: int | str,
    from_chat_id: int | str,
    message_id: int | str,
    reply_markup=None,
):
    try:
        await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )
        return True
    except TelegramRetryAfter as exc:
        await asyncio.sleep(exc.retry_after)
        await copy_message_mailing(
            bot=bot,
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )
    except Exception:
        return False


async def mailing_everyone(
    bot: Bot,
    from_chat_id: int,
    message_id: int,
    admin_id: int,
    reply_markup=None,
):
    users = await User.get_all()
    await bot.send_message(chat_id=admin_id, text=_("*Рассылка начата\\!*"))
    count = 0
    for user in users:
        sent = await copy_message_mailing(
            bot=bot,
            chat_id=user.tg_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )
        if sent:
            count += 1
    await bot.send_message(
        chat_id=admin_id,
        text=_(
            "*Рассылка закончена\\!*\nВсего разослано для _{count}_ пользователей\."
        ).format(count=count),
    )


def escape_markdown_v2(text: str) -> str:
    escape_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in escape_chars:
        text = text.replace(char, "\\" + char)
    return text


def language_by_locale(locale: str) -> str:
    return LANGUAGES.get(locale)
