from database.models import Location
from keyboards.inline import cancel_keyboard
from utils.messages import escape_markdown_v2
from utils.states import LocationStates

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.utils.i18n import gettext as _

router = Router()


@router.message(StateFilter(LocationStates.location))
async def message_location(message: types.Message):
    locations_deserialized = message.text.lower().split(", ")
    locations = [
        Location(name=" ".join(location.split()))
        for location in locations_deserialized
    ]
    await Location.add_many(locations)
    msg = _("*Локации добавлены:*\n\n")
    for location in locations:
        msg += f"{escape_markdown_v2(location.name)}\n"
    msg += _("\n\n*Добавим еще\\?*")
    await message.answer(
        text=msg,
        reply_markup=cancel_keyboard(),
    )
