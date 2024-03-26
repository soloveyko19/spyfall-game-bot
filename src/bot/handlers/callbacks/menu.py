import os

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.i18n import gettext as _

from database.models import User
from keyboards.inline import languages_keyboard, buy_me_a_coffee_keyboard, menu_keyboard, back_to_menu_keyboard
from utils.messages import language_by_locale, rules_message
from utils.states import LanguageStates

router = Router()


@router.callback_query(lambda call: call.data.startswith("menu_option="))
async def callback_menu(call: CallbackQuery, db_user: User, state: FSMContext):
    try:
        arg = call.data.split("=")[1]
    except (IndexError, ValueError):
        return
    if arg == "language":
        await state.set_state(LanguageStates.user_locale)
        await call.message.edit_text(
            text=_("*Сейчас ваш язык: {language}\nВыберите язык *").format(language=language_by_locale(db_user.locale)),
            reply_markup=languages_keyboard()
        )
    elif arg == "rules":
        await call.message.edit_text(
            text=rules_message(),
            reply_markup=back_to_menu_keyboard()
        )
    elif arg == "coffee":
        await call.message.delete()
        pic_file_path = os.path.join("static", "img", "coffee.png")
        await call.message.answer_photo(
            photo=FSInputFile(path=pic_file_path),
            caption=_(
                "Этот проект полностью лежит на плечах одного разработчика\\, который оплачивает хостинг для этого бота и уделяет большое кол\\-во времени на его поддержку\\. Так что при желании у вас есть возможность поблагодарить его угостив чашечкой кофе по ссылке ниже либо отсканировав QR\\-код :\\)"),
            reply_markup=buy_me_a_coffee_keyboard(),
        )


@router.callback_query(lambda call: call.data == "cancel")
async def callback_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    bot = await call.bot.get_me()
    try:
        await call.message.edit_text(
            text=_(
                "*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"
            ),
            reply_markup=menu_keyboard(bot.username)
        )
    except TelegramBadRequest:
        await call.message.delete()
        await call.message.answer(
            text=_(
                "*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"
            ),
            reply_markup=menu_keyboard(bot.username)
        )
