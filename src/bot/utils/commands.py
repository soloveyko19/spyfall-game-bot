import asyncio

from database.models import User

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
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
    BotCommand(command="extend", description="Add 30 seconds to the "),
    BotCommand(command="language", description="Change the group language")
]

# Private chats
commands_private_chats = [
    BotCommand(command="cancel", description="Cancel action"),
    BotCommand(command="start", description="Start the bot"),
    BotCommand(command="help", description="Rules of the game"),
    BotCommand(
        command="feedback",
        description="Write feedback for developers",
    ),
    BotCommand(command="language", description="Change the language"),
    BotCommand(command="coffee", description="Buy a coffee for developer")
]

# Additional commands in chats only for admins
commands_admins = [
    BotCommand(
        command="get_feedback",
        description="Show last feedbacks",
    ),
    BotCommand(command="error", description="Raise error"),
    BotCommand(
        command="admin",
        description="Provide the administrator rights for another user",
    ),
    BotCommand(command="stats", description="Show statistics"),
    BotCommand(command="mailing", description="Make mailing"),
    BotCommand(
        command="location",
        description="See or add new locations",
    ),
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
        await asyncio.sleep(0.05)


async def set_admin_commands(bot: Bot, user: User):
    await bot.set_my_commands(
        commands_admins,
        scope=BotCommandScopeChat(chat_id=user.tg_id),
    )
