from keyboards.inline import menu_keyboard, confirm_keyboard
from utils.states import AdminStates
from database.models import User
from filters.user import AdminFilter

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.i18n import gettext as _

router = Router()


@router.message(StateFilter(AdminStates.message_user), AdminFilter())
async def message_admin_user(
    message: types.Message, state: FSMContext, db_user: User
):
    if message.text == _("Отменить! ❌"):
        await message.answer(
            text=_("Отменено\\!"), reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        bot = await message.bot.get_me()
        return await message.answer(
            text=_("*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"),
            reply_markup=menu_keyboard(
                bot_username=bot.username, for_admins=db_user.is_admin
            ),
        )
    elif message.user_shared:
        new_admin_user = await User.get(tg_id=message.user_shared.user_id)
        if not new_admin_user:
            await message.answer(
                text=_(
                    "*Такого пользователя нет в моей системе\\!*\n_Сперва ему нужно ввести команду /start\\._"
                ),
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.clear()
        elif new_admin_user.is_admin:
            await message.answer(
                text=_(
                    "*[{full_name}](tg://user?id={tg_id}) уже является администратором\\!*"
                ).format(
                    full_name=new_admin_user.full_name,
                    tg_id=new_admin_user.tg_id,
                ),
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.clear()
        else:
            await state.set_state(state=AdminStates.confirm_admin)
            await state.update_data(data={"new_admin_id": new_admin_user.id})
            await message.answer(
                text=_(
                    "*Вы уверенны что хотите сделать [{full_name}](tg://user?id={tg_id}) администратором?*"
                ).format(
                    full_name=new_admin_user.full_name,
                    tg_id=new_admin_user.tg_id,
                ),
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer(
                text=_("*Подтвердите, пожалуйста 👇*"),
                reply_markup=confirm_keyboard(),
            )
    else:
        await message.answer(
            text=_(
                "*Некоректный ввод\\(*_Пожалуйста, поделитесь пользователем через клавиатуру 👇_"
            )
        )
