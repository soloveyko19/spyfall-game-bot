from database.models import Player, Vote, Location, User
from utils.states import LocationStates, MailingStates
from keyboards.inline import (
    cancel_keyboard,
    location_options_keyboard, confirm_mailing_keyboard,
)
from utils.messages import escape_markdown_v2, mailing_everyone

from aiogram.filters import StateFilter
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.callback_query(lambda call: call.data == "cancel")
async def callback_cancel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()
    await call.message.answer(text="*Отмена\\!*")


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


@router.callback_query(StateFilter(MailingStates.button))
async def callback_mailing_add_button(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data == "true":
        await state.update_data(add_button=True)
        await state.set_state(MailingStates.button_text)
        await call.message.answer(
            text="*Напишите какой текст будет на кнопке*",
            reply_markup=cancel_keyboard()
        )
    else:
        await state.update_data(add_button=False)
        data = await state.get_data()
        await call.bot.copy_message(
            chat_id=call.from_user.id,
            from_chat_id=data.get("chat_id"),
            message_id=data.get("message_id")
        )
        await call.message.answer(
            text="*Подтвердите что хотите разослать это сообщение\\.*",
            reply_markup=confirm_mailing_keyboard()
        )
        await state.set_state(MailingStates.confirm)


@router.callback_query(StateFilter(MailingStates.confirm))
async def callback_mailing_confirm(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data == "confirm":
        data = await state.get_data()
        await mailing_everyone(
            bot=call.bot,
            admin_id=call.from_user.id,
            from_chat_id=data.get("chat_id"),
            message_id=data.get("message_id"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(url=data.get("button_url"), text=data.get("button_text"))
                    ]
                ]
            ) if data.get("add_button") else None
        )
    await state.clear()


@router.callback_query()
async def echo_callback_query(call: CallbackQuery):
    await call.message.delete()
