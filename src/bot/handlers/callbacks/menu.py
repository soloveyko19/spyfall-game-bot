import os

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.i18n import gettext as _

from database.models import User, Feedback, Game
from keyboards.inline import (
    languages_keyboard,
    buy_me_a_coffee_keyboard,
    menu_keyboard,
    back_to_menu_keyboard,
    admin_menu_keyboard,
    back_to_admin_menu_keyboard,
    cancel_keyboard,
    location_options_keyboard, statistics_keyboard,
)
from keyboards.reply import request_contact_keyboard
from utils.messages import (
    language_by_locale,
    rules_message,
    get_feedback_message,
    get_stats,
    stats_message, escape_markdown_v2,
)
from utils.states import (
    LanguageStates,
    AdminStates,
    MailingStates,
    FeedbackStates,
    LocationStates,
)

router = Router()


@router.callback_query(lambda call: call.data.startswith("menu_option="))
async def callback_menu(call: CallbackQuery, db_user: User, state: FSMContext):
    try:
        arg = call.data.split("=")[1]
    except (IndexError, ValueError):
        return
    if arg == "language":
        await state.set_state(LanguageStates.user_locale)
        await call.message.edit_text(
            text=_("*Сейчас ваш язык: {language}\nВыберите язык *").format(
                language=language_by_locale(db_user.locale)
            ),
            reply_markup=languages_keyboard(),
        )
    elif arg == "rules":
        await call.message.edit_text(
            text=rules_message(), reply_markup=back_to_menu_keyboard()
        )
    elif arg == "coffee":
        await call.message.delete()
        pic_file_path = os.path.join("static", "img", "coffee.png")
        await call.message.answer_photo(
            photo=FSInputFile(path=pic_file_path),
            caption=_(
                "Этот проект полностью лежит на плечах одного разработчика\\, который оплачивает хостинг для этого бота и уделяет большое кол\\-во времени на его поддержку\\. Так что при желании у вас есть возможность поблагодарить его угостив чашечкой кофе по ссылке ниже либо отсканировав QR\\-код :\\)"
            ),
            reply_markup=buy_me_a_coffee_keyboard(),
        )
    elif arg == "feedback":
        await state.set_state(FeedbackStates.feedback)
        await call.message.edit_text(
            text=_(
                "*Чтобы обратиться к разработчику напишите свой комментарий ниже\\. 👇*\n_Напоминаем что это не коммерческий продукт и каждый ваш отзыв помогает улучшить его\\._"
            ),
            reply_markup=cancel_keyboard(),
        )
    elif arg == "admin_menu":
        if not db_user.is_admin:
            return await call.answer(
                _("Для этой функции необходимы права администратора!"),
                show_alert=True,
            )
        await call.message.edit_text(
            _("*Меню для админов\\! 💅*"), reply_markup=admin_menu_keyboard()
        )


@router.callback_query(lambda call: call.data.startswith("admin_menu_option="))
async def callback_admin_menu_option(
    call: CallbackQuery, state: FSMContext, db_user: User
):
    if not db_user or not db_user.is_admin:
        return await call.answer(
            _("Для этой функции необходимы права администратора!"),
            show_alert=True,
        )
    try:
        arg = call.data.split("=")[1]
    except IndexError:
        return
    if arg == "get_feedback":
        feedbacks = await Feedback.get_last()
        await call.message.edit_text(
            text=get_feedback_message(feedbacks=feedbacks),
            reply_markup=back_to_admin_menu_keyboard(),
        )
    elif arg == "error":
        return 1 / 0
    elif arg == "admin":
        await state.set_state(AdminStates.message_user)
        await call.message.delete()
        await call.message.answer(
            text=_(
                "*Вы собираетесь добавить администратора для этого бота\\! 👨‍💻*\n_Пожалуйста\\, поделитесь контактом пользователя которого вы хотите назначить администратором 👇_"
            ),
            reply_markup=request_contact_keyboard(),
        )
    elif arg == "stats":
        stats = await get_stats()
        _stats_message = stats_message(stats=stats)
        try:
            await call.message.edit_text(
                text=_stats_message,
                reply_markup=statistics_keyboard(),
            )
        except TelegramBadRequest:
            return
    elif arg == "mailing":
        await state.set_state(MailingStates.message)
        await call.message.edit_text(
            text=_(
                "*Вы собираетесь сделать рассылку\\!*\nОтправьте сообщение которое вы хотите разослать\\."
            ),
            reply_markup=back_to_admin_menu_keyboard(),
        )
    elif arg == "location":
        await state.set_state(LocationStates.option)
        await call.message.edit_text(
            text=_("*Выберите опцию:*"),
            reply_markup=location_options_keyboard(),
        )


@router.callback_query(lambda call: call.data == "cancel")
async def callback_cancel(
    call: CallbackQuery, state: FSMContext, db_user: User
):
    await state.clear()
    bot = await call.bot.get_me()
    try:
        await call.message.edit_text(
            text=_("*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"),
            reply_markup=menu_keyboard(
                bot.username, for_admins=db_user.is_admin
            ),
        )
    except TelegramBadRequest:
        await call.message.delete()
        await call.message.answer(
            text=_("*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"),
            reply_markup=menu_keyboard(
                bot.username, for_admins=db_user.is_admin
            ),
        )


@router.callback_query(lambda call: call.data == "cancel_admin")
async def callback_cancel_admin(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text(
            text=_("*Меню для админов\\! 💅*"),
            reply_markup=admin_menu_keyboard(),
        )
    except TelegramBadRequest:
        await call.message.delete()
        await call.message.answer(
            text=_("*Меню для админов\\! 💅*"),
            reply_markup=admin_menu_keyboard(),
        )
