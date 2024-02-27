from typing import Callable, Dict, Any, Awaitable
import traceback

from database.models import Game, User
from utils.messages import escape_markdown_v2

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message


class DatabaseContextMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ):
        tg_user = data.get("event_from_user")
        db_user = await User.get(tg_user.id)
        data["db_user"] = db_user

        game = await Game.get(group_tg_id=data.get("event_chat").id)
        data["game"] = game
        await handler(event, data)


class ManageGameChatMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ):
        if isinstance(event.message, Message):
            message = event.message

            game = data.get("game")
            if (
                    game
                    and game.state_id in (3, 4)
                    and message.from_user.id not in game.player_ids
            ):
                bot = data.get("bot")
                await bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
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
            user = data.get("db_user")
            await bot.send_message(
                chat_id=546994614,
                text=f"*Снова ошибка 😭*\n\n`{escape_markdown_v2(traceback.format_exc())}`\n\nПользователь: [{escape_markdown_v2(user.full_name)}](tg://user?id={user.tg_id})"
            )
            raise exc
