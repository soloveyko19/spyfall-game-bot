from typing import Callable, Dict, Any, Awaitable

from database.models import Game

from aiogram import BaseMiddleware
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
