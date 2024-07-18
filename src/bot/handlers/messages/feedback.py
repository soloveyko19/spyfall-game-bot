from database.models import User, Feedback
from keyboards.inline import (
    back_to_admin_menu_keyboard,
    back_to_menu_keyboard,
    confirm_keyboard,
)
from utils.messages import escape_markdown_v2
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
            "*Спасибо за фидбэк\\! ❤️*\n\nНомер вашего запроса: {feedback_id}\n\n_Ваше сообщение отправлено и будет принято во внимание разработчиками\\!_",
        ).format(feedback_id=feedback.id),
        reply_markup=back_to_menu_keyboard(),
    )


@router.message(StateFilter(FeedbackStates.feedback_number))
async def message_feedback_number(message: types.Message, state: FSMContext):
    try:
        feedback_id = int(message.text)
    except (ValueError, TypeError):
        return await message.answer(
            text=_(
                "*Пожалуста\\, введите номер фидбэка на который желаете ответить*"
            ),
            reply_markup=back_to_admin_menu_keyboard(),
        )
    feedback = await Feedback.get(feedback_id)
    if not feedback:
        return await message.answer(
            text=_(
                "*Фидбэка с таким номером нет\\! Проверьте номер\\, и попробуйте еще раз\\.*"
            ),
            reply_markup=back_to_admin_menu_keyboard(),
        )
    await state.update_data({"feedback_id": feedback_id})
    await state.set_state(FeedbackStates.answer)
    await message.answer(
        text=_(
            "*Вы хотите ответить на фидбэк:*\n\n[{user_full_name}](tg://user?id={user_tg_id}): {message}\n\nОтправьте ваш ответ на фидбэк 👇"
        ).format(
            user_full_name=escape_markdown_v2(feedback.user.full_name),
            user_tg_id=feedback.user.tg_id,
            message=escape_markdown_v2(feedback.message),
        )
    )


@router.message(StateFilter(FeedbackStates.answer))
async def message_answer_feedback(message: types.Message, state: FSMContext):
    await state.update_data({"answer": message.text})
    await state.set_state(FeedbackStates.confirm_answer)
    await message.answer(
        text=_("Подтвердите отправку ответа на фидбэк"),
        reply_markup=confirm_keyboard(),
    )
