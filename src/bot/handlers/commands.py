from aiogram.fsm.storage.base import StorageKey

from filters.user import AdminFilter
from keyboards.inline import (
    join_game_keyboard,
    link_to_bot_keyboard,
    vote_players_keyboard,
    location_options_keyboard,
    cancel_keyboard,
    languages_keyboard,
)
from database.models import User, Game, Player, Feedback
from keyboards.reply import request_contact_keyboard
from utils.i18n import translate_request
from utils.messages import (
    join_message,
    delete_all_messages,
    discussion_message,
    escape_markdown_v2,
    language_by_locale,
    LANGUAGES,
)
from utils.states import (
    LocationStates,
    FeedbackStates,
    AdminStates,
    MailingStates,
    LanguageStates,
)
from filters.chat import ChatTypeFilter

import asyncio
import random
from aiogram.utils.i18n import gettext as _

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

router = Router()


@router.message(Command("start"), ChatTypeFilter("private"))
async def command_start(
    message: types.Message, command: CommandObject, db_user: User
):
    if not db_user:
        lang = message.from_user.language_code
        db_user = User(
            tg_id=message.from_user.id,
            full_name=message.from_user.full_name,
            locale=lang if lang in LANGUAGES.keys() else None,
        )
        await db_user.save()
    elif db_user.full_name != message.from_user.full_name:
        db_user.full_name = message.from_user.full_name
        await db_user.save()
    if not command.args:
        return await message.answer(
            text=_(
                "*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!"
            ),
        )
    game = await Game.get(join_key=command.args)
    if not game:
        return await message.reply(
            text=_(
                "*Ошибка ❗️*\n_Такой игры не существует либо она уже была окончена\\._"
            ),
        )
    elif game.state_id != 2:
        return await message.reply(
            text=_("*Ошибка ❗️*\nНабор в игру уже окончен\\!"),
        )
    try:
        await Player.join_to_game(game_id=game.id, user_id=db_user.id)
    except ValueError:
        return await message.answer(text=_("*Вы уже в игре\\!* ⛔️"))
    await game.refresh()
    bot = await message.bot.get_me()
    await message.bot.edit_message_text(
        message_id=game.join_message_tg_id,
        chat_id=game.group_tg_id,
        text=join_message(seconds=90, players=sorted(game.players, key=lambda player: player.id), locale=game.locale),
        reply_markup=join_game_keyboard(
            join_key=game.join_key, bot_username=bot.username
        ),
    )
    await message.answer(
        text=_("*Вы присоединились к игре в Шпиона\\! ✅*"),
    )


@router.message(Command("start"), ChatTypeFilter("supergroup", "group"))
async def command_start_group(message: types, game: Game):
    if game and game.is_allowed:
        await message.delete()
    await message.answer(
        text=_("*Чтобы начать игру введите команду /game*"),
    )


@router.message(Command("game"), ChatTypeFilter("supergroup", "group"))
async def command_game(message: types.Message, game: Game):
    if not game:
        game = Game(group_id=message.chat.id, state_id=1)
        await game.save()
        return await message.answer(
            text=_(
                "*Пожалуйста\\, обновите мне права администратора*\n_Извините за неудобства\\(_",
            ),
        )
    elif game.state_id != 1:
        return await message.answer(text=_("*Игра уже запущена\\!* ⛔️"))
    elif not game.is_allowed:
        return await message.answer(
            text=_("*Вы не предоставили необходимые права администратора\\!*")
        )
    await message.delete()
    async with game:
        bot = await message.bot.get_me()
        reg_messages = [
            await message.answer(
                text=join_message(seconds=90),
                reply_markup=join_game_keyboard(
                    join_key=game.join_key, bot_username=bot.username
                ),
            )
        ]
        game.join_message_tg_id = reg_messages[0].message_id
        await game.save()
        sec = 89
        while sec != 0:
            await asyncio.gather(asyncio.sleep(1), game.refresh())
            if game.state_id == 1:
                return
            elif game.state_id == 3:
                break
            elif game.extend != 0:
                sec += 30 * game.extend
                game.extend = 0
                await game.save()
                reg_messages.append(
                    await message.answer(
                        text=_(
                            "*\\+30 секунд к регистрации\\!*\n_Оставшееся время \\- {sec} секунд\\._"
                        ).format(sec=sec)
                    )
                )
            elif sec % 30 == 0:
                reg_messages.append(
                    await message.answer(
                        text=join_message(seconds=sec, locale=game.locale),
                        reply_markup=join_game_keyboard(
                            join_key=game.join_key,
                            bot_username=bot.username,
                        ),
                    )
                )
            sec -= 1
        await asyncio.gather(
            delete_all_messages(reg_messages), game.refresh()
        )
        if len(game.players) < 4:
            await message.answer(
                text=_(
                    "*Игра не запущена\\! ❌*\n_Нужно как минимум 4 участника для игры\\._"
                )
            )
            return
        elif len(game.players) > 10:
            await message.answer(
                text=_(
                    "*Игра не запущена\\! ❌*\n_Максимум 10 игроков в игре\\._"
                )
            )
            return
        spies_count = 1
        game.state_id = 3
        await game.save()

        if game.locale != "ru":
            translated_location = await translate_request(
                text=game.location.name,
                source_lang="ru",
                target_lang="en"
            )
        else:
            translated_location = game.location.name

        await message.answer(
            text=discussion_message(game.players),
            reply_markup=link_to_bot_keyboard(bot_username=bot.username),
        )
        spies = random.sample(population=game.players, k=spies_count)
        tasks = []
        for player in game.players:
            if player in spies:
                player.role_id = 1
                tasks.extend(
                    [
                        message.bot.send_message(
                            chat_id=player.user.tg_id,
                            text=_(
                                "*Вы Шпион\\! 🦸*\n_Не дайте остальным участникам вычислить вашу роль\\!_"
                            ),
                        ),
                        player.save(),
                    ]
                )
                real_spy = player
            else:
                player.role_id = 2
                tasks.append(
                    message.bot.send_message(
                        chat_id=player.user.tg_id,
                        text=_(
                            "*Вы НЕ Шпион\\! 👨*\nЛокация: *{location}*\n_Вычислите шпиона\\!_"
                        ).format(
                            location=escape_markdown_v2(
                                translated_location
                            )
                        ),
                    )
                )
            await player.save()
        await asyncio.gather(*tasks)
        for sec in range(len(game.players) * 60, 0, -1):
            await asyncio.gather(game.refresh(), asyncio.sleep(1))
            if game.state_id == 1:
                return
            elif game.state_id == 4:
                break
            elif sec == 60:
                await message.answer(
                    text=_("*Осталась 1 минута до голосования\\! ⏳*")
                )
        await message.answer(
            text=_(
                "*Время на обсуждение вышло\\! ⌛️*\nДавайте проголосуем за шпиона\\!"
            ),
            reply_markup=link_to_bot_keyboard(bot_username=bot.username),
        )
        game.state_id = 4
        await game.save()
        await asyncio.gather(
            *[
                message.bot.send_message(
                    chat_id=player.user.tg_id,
                    text=_("*Кто шпион? 🦸*", locale=player.user.locale),
                    reply_markup=vote_players_keyboard(
                        players=[
                            _player
                            for _player in game.players
                            if _player != player
                        ]
                    ),
                )
                for player in game.players
            ]
        )
        for sec in range(60, 0, -1):
            await asyncio.gather(
                asyncio.sleep(1), game.refresh(attrs=["state_id"])
            )
            if game.state_id == 1:
                return
            elif await game.all_players_voted():
                break

        max_player_voted = 0
        spy_player = None
        for player in await game.get_players():
            if len(player.spy_voted) > max_player_voted:
                spy_player = player
                max_player_voted = len(player.spy_voted)
            elif len(player.spy_voted) == max_player_voted:
                spy_player = None

        if not spy_player:
            await message.answer(
                text=_(
                    "*Мнения разошлись\\, а значит победа Шпиона\\! 💁‍♂️*\nШпионом был\\(\\-a\\) [{name}](tg://user?id={tg_id})"
                ).format(
                    name=escape_markdown_v2(real_spy.user.full_name),
                    tg_id=real_spy.user.tg_id,
                ),
            )
            return

        await message.answer(
            text=_(
                "*Большинство проголосовало за [{name}](tg://user?id={tg_id})*"
            ).format(
                name=escape_markdown_v2(spy_player.user.full_name),
                tg_id=spy_player.user.tg_id,
            ),
        )

        await asyncio.sleep(5)
        if real_spy.id == spy_player.id:
            res_msg = _(
                "*Победа мирных игроков\\!*\n_Личность шпиона раскрыта\\!_"
            )
        else:
            res_msg = _(
                "*Победа Шпиона\\!*\n_Его личность не раскрыта\\!_\nШпионом был\\(\\-a\\) [{name}](tg://user?id={tg_id})"
            ).format(
                name=escape_markdown_v2(real_spy.user.full_name),
                tg_id=real_spy.user.tg_id,
            )
        await message.answer(text=res_msg)


@router.message(Command("location"), ChatTypeFilter("private"), AdminFilter())
async def command_location(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=_("*Выберите опцию:*"), reply_markup=location_options_keyboard()
    )
    await state.set_state(LocationStates.option)


@router.message(Command("skip"), ChatTypeFilter("supergroup", "group"))
async def command_skip(message: types.Message, game: Game):
    if not game or not game.is_allowed:
        return
    await message.delete()
    if game.state_id in (2, 3):
        game.state_id += 1
        await game.save()


@router.message(Command("stop"), ChatTypeFilter("supergroup", "group"))
async def command_stop(message: types.Message, game: Game):
    if not game or not game.is_allowed:
        return
    await message.delete()
    if game.state_id != 1:
        game.state_id = 1
        await game.save()
        await message.answer(text=_("*Игра была отменена\\. ❌*"))


@router.message(Command("extend"), ChatTypeFilter("supergroup", "group"))
async def command_extend(message: types.Message, game: Game):
    if not game or game.state_id != 2 or not game.is_allowed:
        return
    await message.delete()
    game.extend += 1
    await game.save()


@router.message(Command("cancel"), ChatTypeFilter("private"))
async def command_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()
    await message.answer(
        text=_("*Отмена\\! ❌*\nВсе состояния сняты\\!"),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("help"))
async def command_help(message: types.Message):
    await message.answer(
        text=_(
            '*Вас приветствует бот для игры в Шпиона\\! 👋*\n\n*Правила игры следующие:*\nЧтобы начать играть\\, вам нужно написать команду /game непосредственно в группе где планируется игра\\. Минимальное кол\\-во человек для игры \\- 4\\, максимальное \\- 10\\.\nПосле завершения набора игроков\\, бот вышлет вам вашу роль на эту игру\\. В игре есть две роли:\n*Шпион* \\- задача которого не выдать свою роль до конца игры\\.\n*Не Шпион* \\- задача которого постараться вычислить шпиона\\.\n\nЕсли ваша роль \\- "Не Шпион"\\, то бот скажет локацию для этой игры\\. Задача всех игроков на протяжении игры \\- задавать вопросы по локации\\, чтобы вычислить шпиона\\. После завершения игры проводится голосование\\, все участники игры голосуют за возможного шпиона\\. Если большинство игроков выбирают неправильного игрока\\, то Шпион побеждает\\. Если же шпиона вычислили\\, и большинство игроков проголосовало за него\\, то у него еще есть шанс победить\\, назвав локацию игры которое он понял исходя из заданных ранее вопросов\\.\n\n*Удачной игры\\!*'
        ),
    )


@router.message(Command("language"), ChatTypeFilter("group", "supergroup"))
async def command_language_group(message: types.Message, game: Game, state: FSMContext):
    if not game or game.state_id != 1 or not game.is_allowed:
        return
    await message.delete()
    storage_key = StorageKey(bot_id=message.bot.id, chat_id=message.from_user.id, user_id=message.from_user.id)
    new_state = FSMContext(storage=state.storage, key=storage_key)
    await new_state.set_state(LanguageStates.group_locale)
    await new_state.update_data(game=game)
    await message.bot.send_message(
        chat_id=message.from_user.id,
        text=_("*Сейчас язык группы: {language}\nВыберите язык*")
        .format(language=language_by_locale(game.locale)),
        reply_markup=languages_keyboard()
    )


@router.message(Command("feedback"), ChatTypeFilter("private"))
async def command_feedback(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=_(
            "*Чтобы обратиться к разработчику напишите свой комментарий ниже\\. 👇*\n_Напоминаем что это не коммерческий продукт и каждый ваш отзыв помогает улучшить его\\._"
        ),
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(FeedbackStates.feedback)


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


@router.message(Command("error"), AdminFilter())
async def command_error(message: types.Message):
    return 1 / 0


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


@router.message(Command("language"), ChatTypeFilter("private"))
async def command_language(
    message: types.Message, state: FSMContext, db_user: User
):
    await message.delete()
    await state.set_state(LanguageStates.user_locale)
    await message.answer(
        text=_("*Сейчас ваш язык: {language}\nВыберите язык *").format(
            language=language_by_locale(db_user.locale)
        ),
        reply_markup=languages_keyboard(),
    )
