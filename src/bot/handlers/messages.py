from aiogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.states import (
    LocationStates,
    FeedbackStates,
    AdminStates,
    MailingStates,
)
from database.models import Location, User, Feedback
from keyboards.inline import (
    cancel_keyboard,
    add_buttons_to_mailing_keyboard,
    confirm_mailing_keyboard,
)
from utils.messages import escape_markdown_v2
from utils.commands import set_admin_commands

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.i18n import gettext as _

router = Router()


@router.message(StateFilter(LocationStates.location))
async def message_location(message: types.Message):
    locations_deserialized = message.text.lower().split(", ")
    locations = [
        Location(name=" ".join(location.split()))
        for location in locations_deserialized
    ]
    await Location.add_many(locations)
    msg = _("*Локации добавлены:*\n\n")
    for location in locations:
        msg += f"{escape_markdown_v2(location.name)}\n"
    msg += _("\n\n*Добавим еще\\?*")
    await message.answer(
        text=msg,
        reply_markup=cancel_keyboard(),
    )


@router.message(StateFilter(FeedbackStates.feedback))
async def message_feedback(
    message: types.Message, state: FSMContext, db_user: User
):
    feedback = Feedback(user_id=db_user.id, message=message.text)
    await feedback.save()
    await state.clear()
    await message.answer(
        text=_(
            "*Спасибо за фидбэк\\! ❤️*\n_Ваше сообщение отправлено и будет принято во внимание разработчиками\\!_"
        )
    )


@router.message(StateFilter(AdminStates.message_user))
async def message_admin_user(
    message: types.Message, state: FSMContext, db_user: User
):
    if message.text == _("Отменить! ❌"):
        await state.clear()
        await message.answer(
            text=_("Отменено\\!"), reply_markup=ReplyKeyboardRemove()
        )
        return
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


@router.message(StateFilter(MailingStates.message))
async def message_mailing_message(message: types.Message, state: FSMContext):
    await state.update_data(
        message_id=message.message_id, chat_id=message.chat.id
    )
    await message.answer(
        text=_("*Принято\\!*\nДобавим кнопку со ссылкой?"),
        reply_markup=add_buttons_to_mailing_keyboard(),
    )
    await state.set_state(MailingStates.button)


@router.message(StateFilter(MailingStates.button_text))
async def message_mailing_button_url(
    message: types.Message, state: FSMContext
):
    await state.update_data(button_text=message.text)
    await message.answer(
        text=_("*Отправьте ссылку которую хотите поместить в кнопку\\.*"),
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(MailingStates.button_url)


@router.message(StateFilter(MailingStates.button_url))
async def message_mailing_button_text(
    message: types.Message, state: FSMContext
):
    if not message.text.startswith(
        "https://"
    ) and not message.text.startswith("http://"):
        return await message.answer(
            text=_("*Некоректный формат ссылки\\, попробуйте еще раз*")
        )
    await state.update_data(button_url=message.text)
    data = await state.get_data()
    await message.bot.copy_message(
        chat_id=message.from_user.id,
        from_chat_id=data.get("chat_id"),
        message_id=data.get("message_id"),
        reply_markup=(
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            url=data.get("button_url"),
                            text=data.get("button_text"),
                        )
                    ]
                ]
            )
            if data.get("add_button")
            else None
        ),
    )
    await state.set_state(MailingStates.confirm)
    await message.answer(
        text=_("*Подтвердите что хотите разослать это сообщение\\.*"),
        reply_markup=confirm_mailing_keyboard(),
    )
