from database.models import User, Feedback
from keyboards.inline import back_to_menu_keyboard
from utils.states import FeedbackStates

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _


router = Router()


@router.message(StateFilter(FeedbackStates.feedback))
async def message_feedback(
    message: types.Message, state: FSMContext, db_user: User
):
    feedback = Feedback(user_id=db_user.id, message=message.text)
    await feedback.save()
    await state.clear()
    await message.answer(
        text=_(
            "*Спасибо за фидбэк\\! ❤️*\n_Ваше сообщение отправлено и будет принято во внимание разработчиками\\!_",
        ),
        reply_markup=back_to_menu_keyboard()
    )
