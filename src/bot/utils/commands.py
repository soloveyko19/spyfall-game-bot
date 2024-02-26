from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
)

from database.models import User


# Group chats
commands_group_chats = [
    BotCommand(command="game", description="Начало новой игры"),
    BotCommand(
        command="skip",
        description="Пропустить этап игры",
    ),
    BotCommand(command="stop", description="Отмена игры"),
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="help", description="Правила игры"),
    BotCommand(command="extend", description="Продлить регистрацию"),
]

# Private chats
commands_private_chats = [
    BotCommand(
        command="location",
        description="Просмотр или добавление локаций",
    ),
    BotCommand(command="cancel", description="Отмена действия"),
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="help", description="Правила игры"),
    BotCommand(
        command="feedback",
        description="Написать комментарий разработчику",
    ),
]

# Additional commands in chats only for admins
commands_admins = [
    BotCommand(
        command="get_feedback",
        description="Отобразить последние фидбэки",
    ),
    BotCommand(command="error", description="Вызвать ошибку"),
    BotCommand(
        command="admin",
        description="Дать права администратора другому пользователю",
    ),
    BotCommand(command="stats", description="Получить статистику"),
]

commands_admins.extend(commands_private_chats)


async def get_commands(bot: Bot):
    await bot.set_my_commands(
        commands_group_chats, scope=BotCommandScopeAllGroupChats()
    )
    await bot.set_my_commands(
        commands_private_chats,
        scope=BotCommandScopeAllPrivateChats(),
    )
    for user in await User.get_admins():
        await bot.set_my_commands(
            commands_admins,
            scope=BotCommandScopeChat(chat_id=user.tg_id),
        )


async def set_admin_commands(bot: Bot, user: User):
    await bot.set_my_commands(
        commands_admins,
        scope=BotCommandScopeChat(chat_id=user.tg_id),
    )
