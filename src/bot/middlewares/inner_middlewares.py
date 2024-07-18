from typing import Dict, Any

from database.models import User
from utils.messages import LANGUAGES

from aiogram.types import TelegramObject
from aiogram.utils.i18n import gettext as _, I18nMiddleware


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
