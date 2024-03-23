import os

import aiofiles

from filters.chat import ChatTypeFilter
from database.models import User, Player, Game
from utils.messages import LANGUAGES, join_message, language_by_locale
from utils.states import LanguageStates, FeedbackStates
from keyboards.inline import join_game_keyboard, cancel_keyboard, languages_keyboard, buy_me_a_coffee_keyboard

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.types.input_file import FSInputFile


router = Router()


@router.message(Command("start"), ChatTypeFilter("private"))
async def command_start(
    message: types.Message, command: CommandObject, db_user: User
):
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
            text=_(
                "*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"
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
    bot = await message.bot.get_me()
    await message.bot.edit_message_text(
        message_id=game.join_message_tg_id,
        chat_id=game.group_tg_id,
        text=join_message(seconds=90, players=sorted(game.players, key=lambda player: player.id), locale=game.locale),
        reply_markup=join_game_keyboard(
            join_key=game.join_key, bot_username=bot.username
        ),
    )
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


@router.message(Command("feedback"), ChatTypeFilter("private"))
async def command_feedback(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=_(
            "*Чтобы обратиться к разработчику напишите свой комментарий ниже\\. 👇*\n_Напоминаем что это не коммерческий продукт и каждый ваш отзыв помогает улучшить его\\._"
        ),
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(FeedbackStates.feedback)


@router.message(Command("language"), ChatTypeFilter("private"))
async def command_language(
    message: types.Message, state: FSMContext, db_user: User
):
    await message.delete()
    await state.set_state(LanguageStates.user_locale)
    await message.answer(
        text=_("*Сейчас ваш язык: {language}\nВыберите язык *").format(
            language=language_by_locale(db_user.locale)
        ),
        reply_markup=languages_keyboard(),
    )


@router.message(Command("coffee"), ChatTypeFilter("private"))
async def command_coffee(message: types.Message):
    await message.delete()
    pic_file_path = os.path.join("static", "img", "coffee.png")
    await message.answer_photo(
        photo=FSInputFile(path=pic_file_path),
        caption=_("Этот проект полностью лежит на плечах одного разработчика\\, который оплачивает хостинг для этого бота и уделяет большое кол\\-во времени на его поддержку\\. Так что при желании у вас есть возможность поблагодарить его угостив чашечкой кофе по ссылке ниже либо отсканировав QR\\-код :\\)"),
        reply_markup=buy_me_a_coffee_keyboard(),
    )
