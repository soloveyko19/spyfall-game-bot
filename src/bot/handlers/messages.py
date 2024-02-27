from aiogram.types import ReplyKeyboardRemove

from utils.states import LocationStates, FeedbackStates, AdminStates
from database.models import Location, User, Feedback
from keyboards.inline import cancel_keyboard
from utils.messages import escape_markdown_v2
from utils.commands import set_admin_commands

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

router = Router()


@router.message(StateFilter(LocationStates.location))
async def message_location(message: types.Message):
    locations_deserialized = message.text.lower().split(", ")
    locations = [
        Location(name=" ".join(location.split()))
        for location in locations_deserialized
    ]
    await Location.add_many(locations)
    msg = "*Локации добавлены:*\n\n"
    for location in locations:
        msg += f"{escape_markdown_v2(location.name)}\n"
    msg += "\n\n*Добавим еще\\?*"
    await message.answer(
        text=msg,
        parse_mode="MarkdownV2",
        reply_markup=cancel_keyboard(),
    )


@router.message(StateFilter(FeedbackStates.feedback))
async def message_feedback(message: types.Message, state: FSMContext):
    user = await User.get(tg_id=message.from_user.id)
    feedback = Feedback(user_id=user.id, message=message.text)
    await feedback.save()
    await state.clear()
    await message.answer(
        text="*Спасибо за фидбэк\\! ❤️*\n_Ваше сообщение отправлено и будет принято во внимание разработчиками\\!_",
        parse_mode="MarkdownV2",
    )


@router.message(StateFilter(AdminStates.message_user))
async def message_admin_user(message: types.Message, state: FSMContext):
    if message.text == "Отменить! ❌":
        await state.clear()
        await message.answer(
            text="Отменено\\!",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="MarkdownV2",
        )
        return
    elif message.user_shared:
        user = await User.get(tg_id=message.user_shared.user_id)
        if user:
            user.is_admin = True
            await user.save()
            await message.answer(
                text=f"*Вы успешно сделали [{escape_markdown_v2(user.full_name)}](tg://user?id={user.tg_id}) администратором\\!*",
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.clear()
            await message.bot.send_message(
                chat_id=user.tg_id,
                text=f"*[{escape_markdown_v2(message.from_user.full_name)}](tg://user?id={message.from_user.id}) назначил Вас моим администратором\\!*",
                parse_mode="MarkdownV2",
            )
            await set_admin_commands(bot=message.bot, user=user)
        else:
            await message.answer(
                text="*Такого пользователя нет в моей системе\\!*\n_Сперва ему нужно ввести команду /start\\._",
                parse_mode="MarkdownV2",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.clear()
    else:
        await message.answer(
            text="*Некоректный ввод\\(*_Пожалйста, поделитесь пользователем через клавиатуру 👇_",
            parse_mode="MarkdownV2",
        )
