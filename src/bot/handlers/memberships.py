from database.models import Game

from aiogram import Router, types
from aiogram.filters import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
    LEAVE_TRANSITION,
    MEMBER,
    ADMINISTRATOR,
)
from aiogram.utils.i18n import gettext as _


router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_joined(message: types.ChatMemberUpdated, game: Game):
    if message.new_chat_member.user.id == message.bot.id:
        if not game:
            game = Game(group_tg_id=message.chat.id, state_id=1)
        else:
            game.is_allowed = False
        await game.save()
        await message.answer(
            text=_(
                "*Привет\\! 👋*\n*Чтобы начать игру предоставьте мне следующие права администратора:*\n\\- Удалять сообщения\n\\- Блокировать пользователей\n\\- Закреплять сообщения",
            )
        )


@router.my_chat_member(
    ChatMemberUpdatedFilter((MEMBER | ADMINISTRATOR) >> ADMINISTRATOR)
)
async def check_promoted(message: types.ChatMemberUpdated, game: Game):
    if message.new_chat_member.user.id == message.bot.id:
        rights = [
            message.new_chat_member.can_delete_messages,
            message.new_chat_member.can_restrict_members,
            message.new_chat_member.can_pin_messages,
        ]
        if all(rights):
            game.is_allowed = True
            await game.save()
            await message.answer(
                text=_(
                    "*Отлично\\! ✅\nВсе права предоставлены\\!* 😎\nМожем начнать игру /game"
                )
            )
        else:
            if game.state_id != 1:
                game.state_id = 1
            game.is_allowed = False
            await game.save()
            await message.answer(
                text=_(
                    "*Предоставлены не все необходимые права администратора\\:*\n{rule_1} \\- Удалять сообщения\n{rule_2} \\- Блокировать пользователей\n{rule_3} \\- Закреплять сообщения"
                ).format(
                    rule_1="✅" if rights[0] else "❌",
                    rule_2="✅" if rights[1] else "❌",
                    rule_3="✅" if rights[2] else "❌",
                )
            )


@router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def bot_leaved(message: types.ChatMemberUpdated, game: Game):
    if message.new_chat_member.user.id != message.bot.id:
        return
    if not game:
        return
    elif game.state_id != 1:
        game.state_id = 1
    game.is_allowed = False
    await game.save()
