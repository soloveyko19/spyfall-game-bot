import sys
import logging
import asyncio

from config import conf
from handlers.commands import router as command_router
from handlers.messages import router as message_router
from handlers.callbacks import router as callback_router
from utils.commands import get_commands
from utils.database import load_fixtures
from middlewares.outer_middlewares import ManageGameChatMiddleware, SendErrorInfoMiddleware

from aiogram import Bot, Dispatcher


bot = Bot(token=conf.TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher()


async def register_handlers(dp: Dispatcher):
    dp.include_routers(
        command_router,
        callback_router,
        message_router,
    )


async def set_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(ManageGameChatMiddleware())
    dp.update.outer_middleware(SendErrorInfoMiddleware())


async def main() -> None:
    await asyncio.gather(
        load_fixtures(),
        get_commands(bot),
        register_handlers(dispatcher),
        set_middlewares(dispatcher),
    )
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
