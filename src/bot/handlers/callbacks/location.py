from database.models import Location
from utils.states import LocationStates
from utils.messages import escape_markdown_v2
from keyboards.inline import cancel_keyboard, location_options_keyboard

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _


router = Router()


@router.callback_query(
    lambda call: call.data.startswith("location_option="),
    StateFilter(LocationStates.option),
)
async def callback_location(call: CallbackQuery, state: FSMContext):
    try:
        option = call.data.split("=")[1]
    except IndexError:
        return
    if option == "list":
        locations = await Location.get_list()
        await call.message.delete()
        await call.message.answer(
            text=_("*Все доступные локации:*\n\n")
            + escape_markdown_v2(
                "\n".join([location.name for location in locations])
            )
        )
        await call.message.answer(
            text=_("*Выберите опцию:*"),
            reply_markup=location_options_keyboard(),
        )
    elif option == "add":
        await call.message.delete()
        await call.message.answer(
            text=_(
                "*Давайте добавим локацию\\!*\n_Отправьте название локации в формате перечисления через комму\\._"
            ),
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(LocationStates.location)
    else:
        await call.answer(
            text=_("У вас нет доступа к этой функции"),
            show_alert=True,
        )
