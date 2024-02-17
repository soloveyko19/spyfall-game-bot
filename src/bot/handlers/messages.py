from states.state import LocationStates
from database.models import Location
from keyboards.inline import cancel_keyboard

from aiogram import Router, types
from aiogram.filters import StateFilter

router = Router()


@router.message(StateFilter(LocationStates.location))
async def insert_location(message: types.Message):
    locations_deserialized = message.text.lower().split(", ")
    locations = [
        Location(name=" ".join(location.split()))
        for location in locations_deserialized
    ]
    await Location.add_many(locations)
    msg = "Локации добавлены:\n"
    for location in locations:
        msg += f"{location.name}\n"
    await message.answer(msg)
    await message.answer(
        "Добавим еще локации?", reply_markup=cancel_keyboard()
    )
