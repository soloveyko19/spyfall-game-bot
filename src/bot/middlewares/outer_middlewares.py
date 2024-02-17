from typing import Callable, Dict, Any, Awaitable

from database.models import Game

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message


class ManageGameChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        if isinstance(event.message, Message):
            message = event.message

            game = await Game.get(group_tg_id=message.chat.id)
            if (
                game
                and game.state_id in (3, 4)
                and message.from_user.id not in game.player_ids
            ):
                bot = data.get("bot")
                await bot.delete_message(
                    chat_id=message.chat.id, message_id=message.message_id
                )
                return
        await handler(event, data)


class SendErrorInfoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        try:
            await handler(event, data)
        except Exception as exc:
            bot: Bot = data.get("bot")
            await bot.send_message(
                chat_id=546994614,
                text="Снова ошибка 😭\n\n" + str(exc)
            )
            raise exc
