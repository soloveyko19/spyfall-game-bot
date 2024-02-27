from database.models import Player, Vote, Location, User
from utils.states import LocationStates
from keyboards.inline import (
    cancel_keyboard,
    location_options_keyboard,
)
from utils.messages import escape_markdown_v2

from aiogram.filters import StateFilter
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.callback_query(lambda call: call.data == "cancel")
async def callback_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(text="*Отмена\\!*")
    await call.message.delete()


@router.callback_query(lambda call: call.data.startswith("voting="))
async def callback_voting(call: CallbackQuery):
    try:
        await call.message.delete()
        spy_player_id = int(call.data.split("=")[1])
    except (ValueError, IndexError, TelegramBadRequest):
        return
    player = await Player.get(user_tg_id=call.from_user.id)
    spy_player = await Player.get(_id=spy_player_id)
    if not player or not spy_player:
        return
    try:
        vote = Vote(player_id=player.id, spy_id=spy_player.id)
        await vote.save()
        await call.message.answer(
            text=f"*Вы отдали свой голос за [{escape_markdown_v2(spy_player.user.full_name)}](tg://user?id={spy_player.user.tg_id})\\!*"
        )
        await call.bot.send_message(
            chat_id=player.game.group_tg_id,
            text=f"*[{escape_markdown_v2(player.user.full_name)}](tg://user?id={player.user.tg_id}) проголосовал\\(\\-а\\)\\!*"
        )
    except ValueError:
        return


@router.callback_query(
    lambda call: call.data.startswith("location_option="),
    StateFilter(LocationStates.option),
)
async def callback_location(call: CallbackQuery, state: FSMContext, db_user: User):
    try:
        option = call.data.split("=")[1]
    except IndexError:
        return
    if option == "list":
        locations = await Location.get_list()
        await call.message.delete()
        await call.message.answer(
            text="*Все доступные локации:*\n\n"
            + escape_markdown_v2(
                "\n".join([location.name for location in locations])
            )
        )
        await call.message.answer(
            text="*Выберите опцию:*",
            reply_markup=location_options_keyboard()
        )
    elif option == "add":
        if db_user.is_admin:
            await call.message.delete()
            await call.message.answer(
                text="*Давайте добавим локацию\\!*\n_Отправьте название локации в формате перечисления через комму\\._",
                reply_markup=cancel_keyboard()
            )
            await state.set_state(LocationStates.location)
        else:
            await call.answer(
                text="У вас нет доступа к этой функции",
                show_alert=True,
            )


@router.callback_query()
async def echo_callback_query(call: CallbackQuery):
    await call.message.delete()
