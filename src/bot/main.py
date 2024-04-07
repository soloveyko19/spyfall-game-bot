import logging
import asyncio

from config import conf
from utils.commands import get_commands
from utils.database import load_fixtures
from middlewares.outer_middlewares import (
    SendErrorInfoMiddleware,
    DatabaseContextMiddleware,
    ManageGameChatMiddleware,
)
from middlewares.inner_middlewares import (
    ThrottlingMiddleware,
    DatabaseI18nMiddleware,
)
from database.redis import storage, storage_antispam, storage_restrict

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n


def register_handlers(dp: Dispatcher):
    from handlers import commands, callbacks, messages, memberships

    dp.include_routers(
        # Command handlers
        commands.admins.router,
        commands.groups.router,
        commands.private_chats.router,
        commands.general.router,
        # Callback handlers
        callbacks.menu.router,
        callbacks.mailing.router,
        callbacks.voting.router,
        callbacks.location.router,
        callbacks.language.router,
        callbacks.admin.router,
        callbacks.general.router,
        # Message handlers
        messages.feedback.router,
        messages.mailing.router,
        messages.admin.router,
        messages.location.router,
        # Membership handlers
        memberships.bot.router,
    )


def set_middlewares(dp: Dispatcher):
    # Outer middlewares
    dp.update.outer_middleware(DatabaseContextMiddleware())
    dp.update.outer_middleware(SendErrorInfoMiddleware())
    dp.message.outer_middleware(
        ManageGameChatMiddleware(storage=storage_restrict)
    )
    # Inner middlewares
    dp.update.middleware(DatabaseI18nMiddleware(i18n=dp.get("i18n")))
    dp.update.middleware(ThrottlingMiddleware(storage=storage_antispam))


async def aiogram_on_startup(bot: Bot):
    await get_commands(bot)
    await load_fixtures()


def set_bot_options(dp: Dispatcher):
    set_middlewares(dp)
    register_handlers(dp)
    dp.startup.register(aiogram_on_startup)


def main() -> None:
    logging.basicConfig(level=conf.LOG_LEVEL)

    i18n = I18n(
        path=conf.WORKDIR / "locales", default_locale="ru", domain="messages"
    )
    bot = Bot(token=conf.TELEGRAM_BOT_TOKEN, parse_mode="MarkdownV2")
    dp = Dispatcher(storage=storage)

    dp["i18n"] = i18n

    set_bot_options(dp)
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
