from keyboards.inline import (
    join_game_keyboard,
    link_to_bot_keyboard,
    vote_players_keyboard,
    location_options_keyboard,
)
from database.models import User, Game, Player, Feedback
from keyboards.reply import request_contact_keyboard
from utils.messages import (
    update_message,
    join_message,
    send_message,
    delete_all_messages,
    discussion_message,
    escape_markdown_v2,
)
from states.state import LocationStates, FeedbackStates, AdminStates
from filters.chat import ChatTypeFilter

import asyncio
import random

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

router = Router()


@router.message(Command("start"), ChatTypeFilter("private"))
async def command_start(message: types.Message):
    user = await User.get_or_create(
        tg_id=message.from_user.id,
        full_name=message.from_user.full_name,
    )
    try:
        join_key = message.text.split()[1]
    except IndexError:
        await message.answer(
            text="*Привет\\!* 👋\nДобавь меня в группу где будем играть\\!",
            parse_mode="MarkdownV2",
        )
        return
    game = await Game.get(join_key=join_key)
    if not game:
        return await message.reply(
            text="*Ошибка ❗️*\n_Такой игры не существует либо она уже была окончена\\._",
            parse_mode="MarkdownV2",
        )
    elif game.state_id != 2:
        await message.reply(
            text="*Ошибка ❗️*\nНабор в игру уже окончен\\!",
            parse_mode="MarkdownV2",
        )
    try:
        await Player.join_to_game(game_id=game.id, user_id=user.id)
    except ValueError:
        await message.answer(
            text="*Вы уже в игре\\!* ⛔️", parse_mode="MarkdownV2"
        )
        return
    await game.refresh()
    bot = await message.bot.get_me()
    await update_message(
        message_id=game.join_message_tg_id,
        message_chat_id=game.group_tg_id,
        new_message=join_message(seconds=90, players=game.players),
        reply_markup=join_game_keyboard(
            join_key=game.join_key, bot_username=bot.username
        ),
    )
    await message.answer(
        text="*Вы присоединились к игре в Шпиона\\! ✅*",
        parse_mode="MarkdownV2",
    )


@router.message(
    Command("start"), ChatTypeFilter("supergroup", "group")
)
async def command_start_group(message: types):
    await message.answer(
        text="*Чтобы начать игру введите команду /game*",
        parse_mode="MarkdownV2",
    )


@router.message(
    Command("game"), ChatTypeFilter("supergroup", "group")
)
async def command_game(message: types.Message):
    game = await Game.get(group_tg_id=message.chat.id)
    if not game:
        game = Game(group_id=message.chat.id, state_id=1)
        await game.save()
        await message.answer(
            text="*Пожалуйста\\, обновите мне права администратора*\n_Извините за неудобства\\(_",
            parse_mode="MarkdownV2"
        )
        return
    elif game.state_id != 1:
        await message.answer(
            text="*Игра уже запущена\\!* ⛔️", parse_mode="MarkdownV2"
        )
        return
    elif not game.is_allowed:
        await message.answer(
            text="*Вы не предоставили необходимые права администратора\\!*",
            parse_mode="MarkdownV2",
        )
        return
    await message.delete()
    async with game:
        bot = await message.bot.get_me()
        reg_messages = [
            await message.answer(
                text=join_message(seconds=90),
                reply_markup=join_game_keyboard(
                    join_key=game.join_key, bot_username=bot.username
                ),
                parse_mode="MarkdownV2",
            )
        ]
        game.join_message_tg_id = reg_messages[0].message_id
        await game.save()
        for sec in range(89, 0, -1):
            await asyncio.gather(asyncio.sleep(1), game.refresh())
            if game.state_id == 1:
                return
            elif game.state_id == 3:
                break
            elif sec % 30 == 0:
                reg_messages.append(
                    await message.answer(
                        text=join_message(seconds=sec),
                        reply_markup=join_game_keyboard(
                            join_key=game.join_key,
                            bot_username=bot.username,
                        ),
                        parse_mode="MarkdownV2",
                    )
                )
        await asyncio.gather(
            delete_all_messages(reg_messages), game.refresh()
        )
        if len(game.players) < 4:
            await message.answer(
                text="*Игра не запущена\\! ❌*\n_Нужно как минимум 4 участника для игры\\._",
                parse_mode="MarkdownV2",
            )
            return
        elif len(game.players) > 10:
            await message.answer(
                text="*Игра не запущена\\! ❌*\n_Максимум 10 игроков в игре\\._",
                parse_mode="MarkdownV2",
            )
            return
        spies_count = 1
        game.state_id = 3
        await game.save()
        await message.answer(
            text=discussion_message(game.players),
            reply_markup=link_to_bot_keyboard(
                bot_username=bot.username
            ),
            parse_mode="MarkdownV2",
        )
        spies = random.sample(population=game.players, k=spies_count)
        tasks = []
        for player in game.players:
            if player in spies:
                player.role_id = 1
                tasks.extend(
                    [
                        send_message(
                            chat_id=player.user.tg_id,
                            text="*Вы Шпион\\! 🦸*\n_Не дайте остальным участникам вычислить вашу роль\\!_",
                            parse_mode="MarkdownV2",
                        ),
                        player.save(),
                    ]
                )
                real_spy = player
            else:
                player.role_id = 2
                tasks.append(
                    send_message(
                        chat_id=player.user.tg_id,
                        text=f"*Вы НЕ Шпион\\! 👨*\nЛокация: *{escape_markdown_v2(game.location.name.capitalize())}*\n_Вычислите шпиона\\!_",
                        parse_mode="MarkdownV2",
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
                    text="*Осталась 1 минута до голосования\\! ⏳*",
                    parse_mode="MarkdownV2",
                )
        await message.answer(
            text="*Время на обсуждение вышло\\! ⌛️*\nДавайте проголосуем за шпиона\\!",
            reply_markup=link_to_bot_keyboard(
                bot_username=bot.username
            ),
            parse_mode="MarkdownV2",
        )
        game.state_id = 4
        await game.save()
        await asyncio.gather(
            *[
                send_message(
                    chat_id=player.user.tg_id,
                    text="*Кто шпион? 🦸*",
                    reply_markup=vote_players_keyboard(
                        players=[
                            _player
                            for _player in game.players
                            if _player != player
                        ]
                    ),
                    parse_mode="MarkdownV2",
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
                text=f"*Мнения разошлись\\, а значит победа Шпиона\\! 💁‍♂️*\nШпионом был\\(\\-a\\) [{escape_markdown_v2(real_spy.user.full_name)}](tg://user?id={real_spy.user.tg_id})",
                parse_mode="MarkdownV2",
            )
            return

        await message.answer(
            text=f"*Большинство проголосовало за* [{escape_markdown_v2(spy_player.user.full_name)}](tg://user?id={spy_player.user.tg_id})",
            parse_mode="MarkdownV2",
        )

        await asyncio.sleep(5)
        if real_spy.id == spy_player.id:
            res_msg = "*Победа мирных игроков\\!*\n_Личность шпиона раскрыта\\!_"
        else:
            res_msg = f"*Победа Шпиона\\!*\n_Его личность не раскрыта\\!_\nШпионом был\\(\\-a\\) [{escape_markdown_v2(real_spy.user.full_name)}](tg://user?id={real_spy.user.tg_id})"
        await message.answer(text=res_msg, parse_mode="MarkdownV2")


@router.message(Command("location"), ChatTypeFilter("private"))
async def command_location(
        message: types.Message, state: FSMContext
):
    await message.delete()
    await message.answer(
        text="*Выберите опцию:*",
        reply_markup=location_options_keyboard(),
        parse_mode="MarkdownV2",
    )
    await state.set_state(LocationStates.option)


@router.message(
    Command("skip"), ChatTypeFilter("supergroup", "group")
)
async def command_skip(message: types.Message):
    game = await Game.get(group_tg_id=message.chat.id)
    if not game.is_allowed:
        return
    await message.delete()
    if game and game.state_id in (2, 3):
        game.state_id += 1
        await game.save()


@router.message(
    Command("stop"), ChatTypeFilter("supergroup", "group")
)
async def command_stop(message: types.Message):
    game = await Game.get(group_tg_id=message.chat.id)
    if not game.is_allowed:
        return
    await message.delete()
    if game and game.state_id != 1:
        game.state_id = 1
        await game.save()
        await message.answer(
            text="*Игра была отменена\\. ❌*",
            parse_mode="MarkdownV2",
        )


@router.message(Command("cancel"), ChatTypeFilter("private"))
async def command_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()
    await message.answer(
        text="*Отмена\\! ❌*\nВсе состояния сняты\\!",
        parse_mode="MarkdownV2",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("help"))
async def command_help(message: types.Message):
    await message.answer(
        text='*Вас приветствует бот для игры в Шпиона\\! 👋*\n\n*Правила игры следующие:*\nЧтобы начать играть\\, вам нужно написать команду /game непосредственно в группе где планируется игра\\. Минимальное кол\\-во человек для игры \\- 4\\, максимальное \\- 10\\.\nПосле завершения набора игроков\\, бот вышлет вам вашу роль на эту игру\\. В игре есть две роли:\n*Шпион* \\- задача которого не выдать свою роль до конца игры\\.\n*Не Шпион* \\- задача которого постараться вычислить шпиона\\.\n\nЕсли ваша роль \\- "Не Шпион"\\, то бот скажет локацию для этой игры\\. Задача всех игроков на протяжении игры \\- задавать вопросы по локации\\, чтобы вычислить шпиона\\. После завершения игры проводится голосование\\, все участники игры голосуют за возможного шпиона\\. Если большинство игроков выбирают неправильного игрока\\, то Шпион побеждает\\. Если же шпиона вычислили\\, и большинство игроков проголосовало за него\\, то у него еще есть шанс победить\\, назвав локацию игры которое он понял исходя из заданных ранее вопросов\\.\n\n*Удачной игры\\!*',
        parse_mode="MarkdownV2",
    )


@router.message(Command("feedback"), ChatTypeFilter("private"))
async def command_feedback(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text="*Чтобы обратиться к разработчику напишите свой комментарий ниже\\. 👇*\n_Напоминаем что это не коммерческий продукт и каждый ваш отзыв помогает улучшить его\\._",
        parse_mode="MarkdownV2"
    )
    await state.set_state(FeedbackStates.feedback)


@router.message(Command("get_feedback"), ChatTypeFilter("private"))
async def command_get_feedback(message: types.Message):
    await message.delete()
    user = await User.get(tg_id=message.from_user.id)
    if user.is_admin:
        try:
            limit = int(message.text.split()[1])
        except (IndexError, ValueError):
            limit = 10
        feedbacks = await Feedback.get_last(limit)
        await message.answer(
            text="Вот последние отзывы:\n\n" + "\n\n".join([f"\\[\\#{feedback.id}\\] [{feedback.user.full_name}](tg://user?id={feedback.user.tg_id}) пишет: {escape_markdown_v2(feedback.message)}" for feedback in feedbacks]),
            parse_mode="MarkdownV2"
        )
    else:
        await message.answer(
            text="*У Вас нет права на выполнение этой команды\\.*",
            parse_mode="MarkdownV2"
        )


@router.message(Command("error"))
async def command_error(message: types.Message):
    await message.delete()
    user = await User.get(tg_id=message.from_user.id)
    if user.is_admin:
        return 1 / 0
    else:
        await message.answer(
            text="*У вас нет права на выполнение этой команды\\!*",
            parse_mode="MarkdownV2"
        )


@router.message(Command("admin"), ChatTypeFilter("private"))
async def command_admin(message: types.Message, state: FSMContext):
    await message.delete()
    user = await User.get(tg_id=message.from_user.id)
    if user.is_admin:
        await message.answer(
            text="*Вы собираетесь добавить администратора для этого бота\\! 👨‍💻*\n_Пожалуйста\\, поделитесь контактом пользователя которого вы хотите назначить администратором 👇_",
            parse_mode="MarkdownV2",
            reply_markup=request_contact_keyboard()
        )
        await state.set_state(AdminStates.message_user)
    else:
        await message.answer(
            text="*У вас нет права на выполнение этой команды\\!*",
            parse_mode="MarkdownV2"
        )

