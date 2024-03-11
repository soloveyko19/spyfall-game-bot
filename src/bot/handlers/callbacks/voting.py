from database.models import Player, Vote
from utils.messages import escape_markdown_v2

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext as _


router = Router()


@router.callback_query(lambda call: call.data.startswith("voting="))
async def callback_voting(call: CallbackQuery):
    try:
        await call.message.delete()
        spy_player_id = int(call.data.split("=")[1])
    except (ValueError, IndexError, TelegramBadRequest):
        return
    player = await Player.get(user_tg_id=call.from_user.id)
    spy_player = await Player.get(_id=spy_player_id)
    if not player or not spy_player:
        return
    try:
        vote = Vote(player_id=player.id, spy_id=spy_player.id)
        await vote.save()
        await call.message.answer(
            text=_(
                "*Вы отдали свой голос за [{name}](tg://user?id={tg_id})\\!*"
            ).format(
                name=escape_markdown_v2(spy_player.user.full_name),
                tg_id=spy_player.user.tg_id,
            )
        )
        await call.bot.send_message(
            chat_id=player.game.group_tg_id,
            text=_(
                "*[{name}](tg://user?id={tg_id}) проголосовал\\(\\-а\\)\\!*"
            ).format(
                name=escape_markdown_v2(player.user.full_name),
                tg_id=player.user.tg_id,
            ),
        )
    except ValueError:
        return
