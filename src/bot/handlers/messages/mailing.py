from utils.states import MailingStates
from keyboards.inline import add_buttons_to_mailing_keyboard, cancel_keyboard, confirm_mailing_keyboard, \
    languages_keyboard

from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.i18n import gettext as _


router = Router()


@router.message(StateFilter(MailingStates.message))
async def message_mailing_message(message: types.Message, state: FSMContext):
    await state.update_data(
        message_id=message.message_id, chat_id=message.chat.id
    )
    await message.answer(
        text=_("*Принято\\!*\nДобавим кнопку со ссылкой?"),
        reply_markup=add_buttons_to_mailing_keyboard(),
    )
    await state.set_state(MailingStates.button)


@router.message(StateFilter(MailingStates.button_text))
async def message_mailing_button_url(
    message: types.Message, state: FSMContext
):
    await state.update_data(button_text=message.text)
    await message.answer(
        text=_("*Отправьте ссылку которую хотите поместить в кнопку\\.*"),
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(MailingStates.button_url)


@router.message(StateFilter(MailingStates.button_url))
async def message_mailing_button_text(
    message: types.Message, state: FSMContext
):
    if not message.text.startswith(
        "https://"
    ) and not message.text.startswith("http://"):
        return await message.answer(
            text=_("*Некоректный формат ссылки\\, попробуйте еще раз*")
        )
    await state.update_data(button_url=message.text)
    await state.set_state(MailingStates.locale)
    await message.answer(
        text=_("*Какой язык рассылки\?*"),
        reply_markup=languages_keyboard()
    )