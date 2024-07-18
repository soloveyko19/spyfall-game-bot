from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats
)


# Group chats
commands_group_chats = [
    BotCommand(command="game", description="Start the game"),
    BotCommand(
        command="skip",
        description="Skip part of the game",
    ),
    BotCommand(command="stop", description="Cancel game"),
    BotCommand(command="help", description="Rules of the game"),
    BotCommand(command="extend", description="Extend registration time"),
    BotCommand(command="language", description="Change the group language"),
]

# Private chats
commands_private_chats = [
    BotCommand(command="cancel", description="Cancel action"),
    BotCommand(command="start", description="Start the bot"),
    BotCommand(command="help", description="Rules of the game")
]

async def get_commands(bot: Bot):
    await bot.set_my_commands(
        commands_group_chats, scope=BotCommandScopeAllGroupChats()
    )
    await bot.set_my_commands(
        commands_private_chats,
        scope=BotCommandScopeAllPrivateChats(),
    )
