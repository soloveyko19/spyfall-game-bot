import logging
import asyncio

from config import conf
from handlers.commands import router as command_router
from handlers.messages import router as message_router
from handlers.callbacks import router as callback_router
from handlers.memberships import router as membership_router
from utils.commands import get_commands
from utils.database import load_fixtures
from middlewares.outer_middlewares import (
    ManageGameChatMiddleware,
    SendErrorInfoMiddleware,
)

from aiogram import Bot, Dispatcher


def register_handlers(dp: Dispatcher):
    dp.include_routers(
        command_router,
        callback_router,
        message_router,
        membership_router,
    )


def set_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(ManageGameChatMiddleware())
    dp.update.outer_middleware(SendErrorInfoMiddleware())


async def aiogram_on_startup(bot: Bot):
    await get_commands(bot)
    await load_fixtures()


def set_bot_options(dp: Dispatcher):
    set_middlewares(dp)
    register_handlers(dp)
    dp.startup.register(aiogram_on_startup)


def main() -> None:
    logging.basicConfig(level=conf.LOG_LEVEL)

    bot = Bot(token=conf.TELEGRAM_BOT_TOKEN, parse_mode="MarkdownV2")
    dp = Dispatcher()

    set_bot_options(dp)
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
