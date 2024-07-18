from filters.chat import ChatTypeFilter
from database.models import User, Player, Game
from utils.messages import LANGUAGES, join_message
from keyboards.inline import (
    join_game_keyboard,
    menu_keyboard,
)

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove


router = Router()


@router.message(Command("start"), ChatTypeFilter("private"))
async def command_start(
    message: types.Message, command: CommandObject, db_user: User
):
    bot = await message.bot.get_me()
    if not db_user:
        lang = message.from_user.language_code
        db_user = User(
            tg_id=message.from_user.id,
            full_name=message.from_user.full_name,
            locale=lang if lang in LANGUAGES.keys() else None,
        )
        await db_user.save()
    elif db_user.full_name != message.from_user.full_name:
        db_user.full_name = message.from_user.full_name
        await db_user.save()
    if not command.args:
        return await message.answer(
            text=_("*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"),
            reply_markup=menu_keyboard(
                bot_username=bot.username, for_admins=db_user.is_admin
            ),
        )
    game = await Game.get(join_key=command.args)
    if not game:
        return await message.reply(
            text=_(
                "*Ошибка ❗️*\n_Такой игры не существует либо она уже была окончена\\._"
            ),
        )
    elif game.state_id != 2:
        return await message.reply(
            text=_("*Ошибка ❗️*\nНабор в игру уже окончен\\!"),
        )
    try:
        await Player.join_to_game(game_id=game.id, user_id=db_user.id)
    except ValueError:
        return await message.answer(text=_("*Вы уже в игре\\!* ⛔️"))
    await game.refresh()
    await message.bot.edit_message_text(
        message_id=game.join_message_tg_id,
        chat_id=game.group_tg_id,
        text=join_message(
            seconds=90,
            players=sorted(game.players, key=lambda player: player.id),
            locale=game.locale,
        ),
        reply_markup=join_game_keyboard(
            join_key=game.join_key,
            bot_username=bot.username,
            locale=game.locale,
        ),
    )
    if len(game.players) == 10:
        game.state_id += 1
        await game.save()
    await message.answer(
        text=_("*Вы присоединились к игре в Шпиона\\! ✅*"),
    )


@router.message(Command("cancel"), ChatTypeFilter("private"))
async def command_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()
    await message.answer(
        text=_("*Отмена\\! ❌*\nВсе состояния сняты\\!"),
        reply_markup=ReplyKeyboardRemove(),
    )
