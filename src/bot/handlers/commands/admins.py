from database.models import Feedback
from filters.user import AdminFilter
from filters.chat import ChatTypeFilter
from utils.messages import get_feedback_message, stats_message, get_stats
from utils.states import AdminStates, MailingStates, LocationStates
from keyboards.reply import request_contact_keyboard
from keyboards.inline import (
    cancel_keyboard,
    location_options_keyboard,
    back_to_admin_menu_keyboard,
)

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Command("error"), AdminFilter())
async def command_error(message: types.Message):
    return 1 / 0


@router.message(
    Command("get_feedback"), ChatTypeFilter("private"), AdminFilter()
)
async def command_get_feedback(message: types.Message, command: CommandObject):
    await message.delete()
    if not command.args:
        limit = 10
    else:
        try:
            limit = int(command.args)
        except ValueError:
            return await message.answer(
                text=_(
                    "*Ошибка значения\\, лимит должен быть указан в числовом значении\\!*"
                )
            )
    feedbacks = await Feedback.get_last(limit)
    await message.answer(text=get_feedback_message(feedbacks=feedbacks))


@router.message(Command("admin"), ChatTypeFilter("private"), AdminFilter())
async def command_admin(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=_(
            "*Вы собираетесь добавить администратора для этого бота\\! 👨‍💻*\n_Пожалуйста\\, поделитесь контактом пользователя которого вы хотите назначить администратором 👇_"
        ),
        reply_markup=request_contact_keyboard(),
    )
    await state.set_state(AdminStates.message_user)


@router.message(Command("stats"), ChatTypeFilter("private"), AdminFilter())
async def command_statistics(message: types.Message):
    await message.delete()
    stats = await get_stats()
    await message.answer(
        text=stats_message(stats=stats),
        reply_markup=back_to_admin_menu_keyboard(),
    )


@router.message(Command("mailing"), ChatTypeFilter("private"), AdminFilter())
async def command_mailing(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=_(
            "*Вы собираетесь сделать рассылку\\!*\nОтправьте сообщение которое вы хотите разослать\\."
        ),
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(MailingStates.message)


@router.message(Command("location"), ChatTypeFilter("private"), AdminFilter())
async def command_location(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=_("*Выберите опцию:*"), reply_markup=location_options_keyboard()
    )
    await state.set_state(LocationStates.option)
