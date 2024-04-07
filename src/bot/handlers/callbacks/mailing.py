from utils.messages import mailing_everyone, LANGUAGES
from utils.states import MailingStates
from keyboards.inline import (
    cancel_keyboard,
    confirm_keyboard,
    languages_keyboard,
)

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _


router = Router()


@router.callback_query(StateFilter(MailingStates.button))
async def callback_mailing_add_button(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data == "true":
        await state.update_data(add_button=True)
        await state.set_state(MailingStates.button_text)
        await call.message.answer(
            text=_("*Напишите какой текст будет на кнопке*"),
            reply_markup=cancel_keyboard(),
        )
    else:
        await state.update_data(add_button=False)
        await state.set_state(MailingStates.locale)
        await call.message.answer(
            text=_("*Какой язык рассылки\?*"),
            reply_markup=languages_keyboard(),
        )


@router.callback_query(StateFilter(MailingStates.locale))
async def callback_mailing_set_locale(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(locale=call.data)
    data = await state.get_data()
    await call.bot.copy_message(
        chat_id=call.from_user.id,
        from_chat_id=data.get("chat_id"),
        message_id=data.get("message_id"),
        reply_markup=(
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            url=data.get("button_url"),
                            text=data.get("button_text"),
                        )
                    ]
                ]
            )
            if data.get("add_button")
            else None
        ),
    )
    await call.message.answer(
        text=_(
            "*Подтвердите что хотите разослать это сообщение\\.*\nЯзык рассылки: {language}"
        ).format(language=LANGUAGES.get(data.get("locale"))),
        reply_markup=confirm_keyboard(),
    )
    await state.set_state(MailingStates.confirm)


@router.callback_query(StateFilter(MailingStates.confirm))
async def callback_mailing_confirm(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data == "confirm":
        data = await state.get_data()
        await mailing_everyone(
            bot=call.bot,
            admin_id=call.from_user.id,
            locale=data.get("locale"),
            from_chat_id=data.get("chat_id"),
            message_id=data.get("message_id"),
            reply_markup=(
                InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                url=data.get("button_url"),
                                text=data.get("button_text"),
                            )
                        ]
                    ]
                )
                if data.get("add_button")
                else None
            ),
        )
    await state.clear()
