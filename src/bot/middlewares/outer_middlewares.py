import asyncio
from typing import Callable, Dict, Any, Awaitable
import traceback
from datetime import datetime as dt, timedelta

from database.models import Game, User
from utils.messages import escape_markdown_v2

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, ChatPermissions
from aiogram.enums import ChatMemberStatus
from redis.asyncio import Redis


class DatabaseContextMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ):
        tg_user = data.get("event_from_user")

        db_user, game = await asyncio.gather(
            User.get(tg_user.id),
            Game.get(group_tg_id=data.get("event_chat").id),
        )
        data["db_user"] = db_user
        data["game"] = game
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
            user = data.get("event_from_user")
            admin_id = 546994614
            await bot.send_message(
                chat_id=admin_id,
                text=f"*Снова ошибка 😭*\n\n`{escape_markdown_v2(traceback.format_exc())}`\n\nПользователь: [{escape_markdown_v2(user.full_name)}](tg://user?id={user.id})",
            )


class ManageGameChatMiddleware(BaseMiddleware):
    def __init__(self, storage: Redis):
        self.storage = storage

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any],
    ):
        game = data.get("game")
        if (
                game
                and game.state_id in (3, 4)
                and message.from_user.id not in game.player_ids
        ):
            await message.delete()
            user_member = await message.chat.get_member(user_id=message.from_user.id)
            if user_member.status != ChatMemberStatus.CREATOR:
                user = f"user_restrict_{message.from_user.id}"
                redis_count = await self.storage.get(name=user)
                if redis_count:
                    count = int(redis_count.decode())
                    if count == 0:
                        return await message.bot.restrict_chat_member(
                            chat_id=message.chat.id,
                            user_id=message.from_user.id,
                            permissions=ChatPermissions(
                                can_send_messages=False
                            ),
                            until_date=dt.now() + timedelta(seconds=35),
                            request_timeout=5
                        )
                    await self.storage.incrby(
                        name=user,
                        amount=-1
                    )
                else:
                    await self.storage.set(
                        name=user,
                        value=5,
                        ex=30
                    )
        await handler(message, data)
