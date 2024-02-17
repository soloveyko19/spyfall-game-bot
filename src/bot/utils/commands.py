from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)


async def get_commands(bot: Bot):
    # Group commands
    commands_group_chats = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="game", description="Начать новую игру"),
        BotCommand(
            command="skip",
            description="Пропустить набор игроков и начать игру",
        ),
        BotCommand(command="stop", description="Отменить игру"),
    ]
    await bot.set_my_commands(
        commands_group_chats, scope=BotCommandScopeAllGroupChats()
    )
    # Private chat commands
    commands_chats = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="location", description="Добавить локации"),
        BotCommand(command="cancel", description="Снять все состояния"),
    ]
    await bot.set_my_commands(
        commands_chats, scope=BotCommandScopeAllPrivateChats()
    )
