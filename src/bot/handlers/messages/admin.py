from keyboards.inline import menu_keyboard
from utils.commands import set_admin_commands
from utils.messages import escape_markdown_v2
from utils.states import AdminStates
from database.models import User

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.i18n import gettext as _

router = Router()


@router.message(StateFilter(AdminStates.message_user))
async def message_admin_user(
    message: types.Message, state: FSMContext, db_user: User
):
    if message.text == _("Отменить! ❌"):
        await state.clear()
        await message.answer(
            text=_("Отменено\\!"), reply_markup=ReplyKeyboardRemove()
        )
        bot = await message.bot.get_me()
        return await message.answer(
            text=_("*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"),
            reply_markup=menu_keyboard(
                bot_username=bot.username, for_admins=db_user.is_admin
            ),
        )
    elif message.user_shared:
        if db_user:
            db_user.is_admin = True
            await db_user.save()
            await message.answer(
                text=_(
                    "*Вы успешно сделали [{name}](tg://user?id={tg_id}) администратором\\!*"
                ).format(
                    name=escape_markdown_v2(db_user.full_name),
                    tg_id=db_user.tg_id,
                ),
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.clear()
            await message.bot.send_message(
                chat_id=db_user.tg_id,
                text=_(
                    "*[{name}](tg://user?id={tg_id}) назначил Вас моим администратором\\!*"
                ).format(
                    name=escape_markdown_v2(message.from_user.full_name),
                    tg_id=message.from_user.id,
                ),
            )
            await set_admin_commands(bot=message.bot, user=db_user)
        else:
            await message.answer(
                text=_(
                    "*Такого пользователя нет в моей системе\\!*\n_Сперва ему нужно ввести команду /start\\._"
                ),
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.clear()
    else:
        await message.answer(
            text=_(
                "*Некоректный ввод\\(*_Пожалуйста, поделитесь пользователем через клавиатуру 👇_"
            )
        )
