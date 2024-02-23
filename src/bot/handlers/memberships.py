from aiogram import Router, types
from aiogram.filters import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
    LEAVE_TRANSITION,
    MEMBER,
    ADMINISTRATOR,
)

from database.models import Game

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_joined(message: types.ChatMemberUpdated):
    if message.new_chat_member.user.id == message.bot.id:
        game = await Game.get(group_tg_id=message.chat.id)
        if not game:
            game = Game(group_tg_id=message.chat.id, state_id=1)
        else:
            game.is_allowed = False
        await game.save()
        await message.answer(
            text="*Привет\\! 👋*\n*Чтобы начать игру предоставьте мне следующие права администратора:*\n\\- Удалять сообщения\n\\- Блокировать пользователей\n\\- Закреплять сообщения",
            parse_mode="MarkdownV2",
        )


@router.my_chat_member(
    ChatMemberUpdatedFilter((MEMBER | ADMINISTRATOR) >> ADMINISTRATOR)
)
async def check_promoted(message: types.ChatMemberUpdated):
    if message.new_chat_member.user.id == message.bot.id:
        game = await Game.get(group_tg_id=message.chat.id)
        rights = [
            message.new_chat_member.can_delete_messages,
            message.new_chat_member.can_restrict_members,
            message.new_chat_member.can_pin_messages,
        ]
        if all(rights):
            game.is_allowed = True
            await game.save()
            await message.answer(
                text="*Отлично\\! ✅\nВсе права предоставлены\\!* 😎\nМожем начнать игру /game",
                parse_mode="MarkdownV2",
            )
        else:
            if game.state_id != 1:
                game.state_id = 1
            game.is_allowed = False
            await game.save()
            await message.answer(
                text=f"*Предоставлены не все необходимые права администратора\\:*\n{'✅' if rights[0] else '❌'} \\- Удалять сообщения\n{'✅' if rights[1] else '❌'} \\- Блокировать пользователей\n{'✅' if rights[2] else '❌'} \\- Закреплять сообщения",
                parse_mode="MarkdownV2",
            )


@router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def bot_leaved(message: types.ChatMemberUpdated):
    if message.new_chat_member.user.id != message.bot.id:
        return
    game = await Game.get(group_tg_id=message.chat.id)
    if not game:
        return
    elif game.state_id != 1:
        game.state_id = 1
    game.is_allowed = False
    await game.save()
