from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat
)

from database.models import User


async def get_commands(bot: Bot):
    # Group commands
    commands_group_chats = [
        BotCommand(command="game", description="Начало новой игры"),
        BotCommand(
            command="skip",
            description="Пропустить этап игры",
        ),
        BotCommand(command="stop", description="Отмена игры"),
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Правила игры"),
    ]
    await bot.set_my_commands(
        commands_group_chats, scope=BotCommandScopeAllGroupChats()
    )
    # Private chat commands
    commands_chats = [
        BotCommand(
            command="location",
            description="Просмотр или добавление локаций",
        ),
        BotCommand(command="cancel", description="Отмена действия"),
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Правила игры"),
        BotCommand(command="feedback", description="Написать комментарий разработчику")
    ]
    await bot.set_my_commands(
        commands_chats, scope=BotCommandScopeAllPrivateChats()
    )
    commands_admins = [
        BotCommand(command="get_feedback", description="Отобразить последние фидбэки")
    ]
    commands_admins.extend(commands_chats)
    for user in await User.get_admins():
        await bot.set_my_commands(
            commands_admins,
            scope=BotCommandScopeChat(chat_id=user.tg_id)
        )
