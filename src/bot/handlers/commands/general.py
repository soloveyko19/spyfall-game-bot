from aiogram import Router, types
from aiogram.filters import Command
from utils.messages import rules_message


router = Router()


@router.message(Command("help"))
async def command_help(message: types.Message):
    await message.answer(
        text=rules_message(),
    )
