from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _


router = Router()


@router.callback_query(lambda call: call.data == "cancel")
async def callback_cancel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()
    await call.message.answer(text=_("*Отмена\\!*"))


@router.callback_query()
async def echo_callback_query(call: CallbackQuery):
    await call.message.delete()
