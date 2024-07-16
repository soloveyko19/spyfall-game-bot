from aiogram.types import CallbackQuery
from aiogram import Router
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from database.models import Feedback
from keyboards.inline import back_to_admin_menu_keyboard
from utils.messages import escape_markdown_v2, get_feedback_message
from utils.states import FeedbackStates


router = Router()


@router.callback_query(FeedbackStates.feedback_option)
async def callback_choose_feedback_option(call: CallbackQuery, state: FSMContext):
    feedback_option = call.data
    if feedback_option == "list":
        feedbacks = await Feedback.get_last()
        await call.message.edit_text(
            text=get_feedback_message(feedbacks=feedbacks),
            reply_markup=back_to_admin_menu_keyboard(),
        )
        await state.clear()
    elif feedback_option == "answer":
        await state.set_state(FeedbackStates.feedback_number)
        await call.message.edit_text(
            text=_("*Введите номер фидбэка на который желаете ответить 👇*")
        )


@router.callback_query(StateFilter(FeedbackStates.confirm_answer))
async def callback_confirm_answer(call: CallbackQuery, state: FSMContext):
    if call.data == "confirm":
        data = await state.get_data()
        feedback = await Feedback.get(data.get("feedback_id"))
        await call.bot.send_message(
            chat_id=feedback.user.tg_id,
            text=_("*Ответ от разработчика на ваш фидбэк №{feedback_id}:*\n\n{feedback_message}",
                    locale=feedback.user.locale
                ).format(
                feedback_id=feedback.id,
                feedback_message=escape_markdown_v2(data.get("answer"))
            )
        )
        await call.message.edit_text(
            text=_("Отправлено\\!"),
            reply_markup=back_to_admin_menu_keyboard()
        )
        await state.clear()