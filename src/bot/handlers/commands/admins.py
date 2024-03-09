from database.models import Feedback, User, Game
from filters.user import AdminFilter
from filters.chat import ChatTypeFilter
from utils.messages import escape_markdown_v2
from utils.states import AdminStates, MailingStates, LocationStates
from keyboards.reply import request_contact_keyboard
from keyboards.inline import cancel_keyboard, location_options_keyboard

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
async def command_get_feedback(
    message: types.Message, command: CommandObject
):
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
    await message.answer(
        text=_("Вот последние отзывы:\n\n")
        + "\n\n".join(
            [
                f"\\[\\#{feedback.id}\\] [{escape_markdown_v2(feedback.user.full_name)}](tg://user?id={feedback.user.tg_id}): {escape_markdown_v2(feedback.message)}"
                for feedback in feedbacks
            ]
        ),
    )


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
    users_count = await User.get_count()
    games_count = await Game.get_count()
    active_games_count = await Game.get_active_count()
    await message.answer(
        text=_(
            "*Статистика 📈*\n\nКол\\-во пользователей: {users_count}\nОбщее кол\\-во игр: {games_count}\nКол\\-во активных игр: {active_games_count}"
        ).format(
            users_count=users_count,
            games_count=games_count,
            active_games_count=active_games_count,
        ),
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
