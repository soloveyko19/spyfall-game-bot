from typing import Callable, Dict, Any, Awaitable
from datetime import datetime as dt, timedelta

from aiogram.exceptions import TelegramBadRequest
from redis.asyncio import Redis
from aiogram import BaseMiddleware
from aiogram.types import Message, ChatPermissions, TelegramObject
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.utils.i18n import gettext as _


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: Redis):
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        user_id = data.get("event_from_user")
        user = f"user_antispam_{user_id}"
        redis_count = await self.storage.get(name=user)
        if redis_count:
            count = int(redis_count.decode())
            if count == 0:
                return
            elif count == 1:
                await self.storage.incrby(
                    name=user,
                    amount=-1
                )
                if event.callback_query:
                    return await event.callback_query.answer(
                        text=_(
                            "Слишком много действий за короткое время, подождите немного, и попробуте еще раз."
                        ),
                        show_alert=True
                    )
                else:
                    try:
                        await event.bot.send_message(
                            chat_id=data.get("event_chat").id,
                            text=_(
                                "Слишком много действий за короткое время\\, подождите немного\\, и попробуте еще раз\\."
                            )
                        )
                    except TelegramBadRequest:
                        pass
                return
            await self.storage.incrby(
                name=user,
                amount=-1
            )
        else:
            await self.storage.set(
                name=user,
                value=4,
                ex=10
            )
        await handler(event, data)


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
                        value=3,
                        ex=30
                    )
        await handler(message, data)
