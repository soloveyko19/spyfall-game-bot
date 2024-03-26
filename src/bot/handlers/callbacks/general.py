from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from keyboards.inline import menu_keyboard

router = Router()


@router.callback_query()
async def echo_callback_query(call: CallbackQuery):
    await call.message.delete()
