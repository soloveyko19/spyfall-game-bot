from aiogram import Router
from aiogram.types import CallbackQuery


router = Router()


@router.callback_query()
async def echo_callback_query(call: CallbackQuery):
    await call.message.delete()
