from aiogram.enums import ChatMemberStatus

from database.models import Game
from utils.messages import LANGUAGES

from aiogram import Router, types
from aiogram.filters import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
    LEAVE_TRANSITION,
    MEMBER,
    ADMINISTRATOR,
    RESTRICTED
)
from aiogram.utils.i18n import gettext as _


router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_joined(message: types.ChatMemberUpdated, game: Game):
    if message.new_chat_member.user.id == message.bot.id:
        if not game:
            locale = message.from_user.language_code
            game = Game(
                group_tg_id=message.chat.id,
                state_id=1,
                locale=locale if locale in LANGUAGES.keys() else "en"
            )
        else:
            game.is_allowed = False
        await game.save()
        await message.answer(
            text=_(
                "*Привет\\! 👋*\n*Чтобы начать игру предоставьте мне следующие права администратора:*\n\\- Удалять сообщения\n\\- Блокировать пользователей\n\\- Закреплять сообщения",
                locale=game.locale
            )
        )


@router.my_chat_member(
    ChatMemberUpdatedFilter((MEMBER | ADMINISTRATOR | RESTRICTED) >> (MEMBER | ADMINISTRATOR | RESTRICTED))
)
async def check_promoted(message: types.ChatMemberUpdated, game: Game):
    if message.new_chat_member.user.id == message.bot.id:
        bot_member = message.new_chat_member
        if bot_member.status == ChatMemberStatus.RESTRICTED:
            if bot_member.can_send_messages:
                await message.answer(
                    _("*Вы ограничили права бота\\!*\n_Для начала игры предоставьте мне необходимые права администратора_")
                )
            if game:
                game.state_id = 1
                game.is_allowed = False
                await game.save()
            return
        rights = [
            message.new_chat_member.can_delete_messages,
            message.new_chat_member.can_restrict_members,
            message.new_chat_member.can_pin_messages
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
    if message.new_chat_member.user.id != message.bot.id or not game:
        return
    game.state_id = 1
    game.is_allowed = False
    await game.save()
