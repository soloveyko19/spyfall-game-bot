from database.models import User
from keyboards.inline import menu_keyboard
from utils.messages import language_by_locale
from utils.states import LanguageStates

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _


router = Router()


@router.callback_query(StateFilter(LanguageStates.user_locale))
async def callback_user_locale(
        call: CallbackQuery, db_user: User, state: FSMContext
):
    await call.message.delete()
    if call.data:
        db_user.locale = call.data
        await db_user.save()
        await state.clear()
        await call.message.answer(
            text=_(
                "*Ваш язык изменен на: {language}*", locale=db_user.locale
            ).format(language=language_by_locale(db_user.locale))
        )
        bot = await call.bot.get_me()
        await call.message.answer(
            text=_("*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"),
            reply_markup=menu_keyboard(bot.username)
        )


@router.callback_query(StateFilter(LanguageStates.group_locale))
async def callback_group_locale(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data:
        data = await state.get_data()
        game = data.get("game")
        game.locale = call.data
        await game.save()
        await state.clear()
        await call.message.answer(
            text=_("*Язык группы изменен на: {language}*").format(
                language=language_by_locale(game.locale)
            )
        )
