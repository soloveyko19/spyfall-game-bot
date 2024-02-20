from aiogram.fsm.context import FSMContext

from states.state import LocationStates, FeedbackStates
from database.models import Location, User, Feedback
from keyboards.inline import cancel_keyboard

from aiogram import Router, types
from aiogram.filters import StateFilter

router = Router()


@router.message(StateFilter(LocationStates.location))
async def message_location(message: types.Message):
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


@router.message(StateFilter(FeedbackStates.feedback))
async def message_feedback(message: types.Message, state: FSMContext):
    user = await User.get(tg_id=message.from_user.id)
    feedback = Feedback(user_id=user.id, message=message.text)
    await feedback.save()
    await state.clear()
    await message.answer(
        text="*Спасибо за фидбэк\\! ❤️*\n_Ваше сообщение отправлено и будет принято во внимание разработчиками\\!_",
        parse_mode="MarkdownV2"
    )
