from database.models import User
from filters.user import AdminFilter
from utils.messages import escape_markdown_v2
from utils.states import AdminStates

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _


router = Router()


@router.callback_query(StateFilter(AdminStates.confirm_admin), AdminFilter())
async def callback_admin_confirm(
    call: CallbackQuery, state: FSMContext, db_user: User
):
    await call.message.delete()
    if call.data == "confirm":
        data = await state.get_data()
        new_admin_id = data.get("new_admin_id")
        new_admin_user = await User.get(id=new_admin_id)
        if new_admin_user:
            new_admin_user.is_admin = True
            await new_admin_user.save()
            await call.message.answer(
                text=_(
                    "*Вы успешно сделали [{name}](tg://user?id={tg_id}) администратором\\!*"
                ).format(
                    name=escape_markdown_v2(new_admin_user.full_name),
                    tg_id=new_admin_user.tg_id,
                )
            )
            await state.clear()
            await call.bot.send_message(
                chat_id=new_admin_user.tg_id,
                text=_(
                    "*[{name}](tg://user?id={tg_id}) назначил Вас моим администратором\\!*"
                ).format(
                    name=escape_markdown_v2(db_user.full_name),
                    tg_id=db_user.tg_id,
                ),
            )
