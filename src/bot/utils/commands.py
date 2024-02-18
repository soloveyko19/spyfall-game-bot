from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeDefault,
)


async def get_commands(bot: Bot):
    # Group commands
    commands_group_chats = [
        BotCommand(command="game", description="Начало новой игры"),
        BotCommand(
            command="skip",
            description="Пропустить этап игры",
        ),
        BotCommand(command="stop", description="Отмена игры"),
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
    ]
    await bot.set_my_commands(
        commands_chats, scope=BotCommandScopeAllPrivateChats()
    )
    # Global commands
    global_commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Правила игры"),
    ]
    await bot.set_my_commands(
        global_commands, scope=BotCommandScopeDefault()
    )
