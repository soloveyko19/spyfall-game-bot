from typing import Callable, Dict, Any, Awaitable

from database.models import User
from utils.messages import LANGUAGES

from aiogram.exceptions import TelegramBadRequest
from redis.asyncio import Redis
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.utils.i18n import gettext as _, I18nMiddleware


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: Redis):
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        user_id = data.get("event_from_user").id
        chat_id = data.get("event_chat").id
        if (user_id == chat_id or event.message and event.message.text and event.message.text.startswith("/")):
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
                        await event.callback_query.answer(
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
                    value=5,
                    ex=10
                )
        await handler(event, data)


class DatabaseI18nMiddleware(I18nMiddleware):
    async def get_locale(
            self, event: TelegramObject, data: Dict[str, Any]
    ) -> str:
        user: User = data.get("db_user")
        lang = data.get("event_from_user").language_code
        chat = data.get("event_chat")
        game = data.get("game")
        if chat.type in ("group", "supergroup") and game:
            return game.locale
        elif user:
            return user.locale
        elif lang in LANGUAGES.keys():
            return lang
        else:
            return "en"

