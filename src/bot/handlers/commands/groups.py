from filters.chat import ChatTypeFilter
from database.models import Game, User
from keyboards.inline import (
    join_game_keyboard,
    link_to_bot_keyboard,
    vote_players_keyboard,
    languages_keyboard,
)
from utils.messages import (
    join_message,
    discussion_message,
    escape_markdown_v2,
    language_by_locale,
)
from utils.i18n import translate_request
from utils.states import LanguageStates

import asyncio
import random

from aiogram import Router, types
from aiogram.exceptions import TelegramForbiddenError
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandObject
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import StorageKey

router = Router()


@router.message(Command("game"), ChatTypeFilter("supergroup", "group"))
async def command_game(message: types.Message, game: Game):
    if not game:
        game = Game(group_id=message.chat.id, state_id=1)
        await game.save()
    elif not game.is_allowed:
        bot_member = await message.bot.get_chat_member(
            chat_id=message.chat.id, user_id=message.bot.id
        )
        if (
            bot_member.status != ChatMemberStatus.RESTRICTED
            or bot_member.can_send_messages
        ):
            await message.answer(
                _(
                    "*Для начала игры предоставьте мне необходимые права администратора\\!*"
                )
            )
        return
    elif game.state_id != 1:
        return await message.answer(text=_("*Игра уже запущена\\!* ⛔️"))
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
                return await message.bot.delete_messages(
                    chat_id=game.group_tg_id,
                    message_ids=[
                        _message.message_id for _message in reg_messages
                    ],
                )
            elif game.state_id == 3:
                break
            elif game.extend != 0:
                extend_time = game.extend
                sec += extend_time
                game.extend = 0
                await game.save()
                reg_messages.append(
                    await message.answer(
                        text=_(
                            "*\\+{extend_time}с к регистрации\\!*\n_Оставшееся время \\- {sec}с\\._"
                        ).format(sec=sec, extend_time=extend_time)
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
        await message.bot.delete_messages(
            chat_id=game.group_tg_id,
            message_ids=[_message.message_id for _message in reg_messages],
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
                target_lang=game.locale,
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
                            ).capitalize()
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
async def command_extend(
    message: types.Message, game: Game, command: CommandObject
):
    if not game or game.state_id != 2 or not game.is_allowed:
        return
    await message.delete()
    extend_time = 30
    if command.args:
        try:
            extend_time = int(command.args)
        except ValueError:
            return
    if extend_time > 300:
        return await message.answer(
            text=_("Нельзя увеличить время более чем на 300с за раз\\.")
        )
    elif extend_time < 10:
        return await message.answer(
            text=_("Нельзя увеличить время менее чем на 10с\\.")
        )
    game.extend += extend_time
    await game.save()


@router.message(Command("language"), ChatTypeFilter("group", "supergroup"))
async def command_language_group(
    message: types.Message, game: Game, state: FSMContext, db_user: User
):
    if not game or game.state_id != 1 or not game.is_allowed:
        return
    await message.delete()
    try:
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=_(
                "*Сейчас язык группы: {language}\nВыберите язык*",
                locale=db_user.locale,
            ).format(language=language_by_locale(game.locale)),
            reply_markup=languages_keyboard(),
        )
    except TelegramForbiddenError:
        bot_user = await message.bot.get_me()
        return await message.answer(
            text=_(
                "*Чтобы поменять язык в группе, вам сначала нужно инициализировать беседу с ботом\\!*"
            ),
            reply_markup=link_to_bot_keyboard(bot_username=bot_user.username),
        )
    storage_key = StorageKey(
        bot_id=message.bot.id,
        chat_id=message.from_user.id,
        user_id=message.from_user.id,
    )
    new_state = FSMContext(storage=state.storage, key=storage_key)
    await new_state.set_state(LanguageStates.group_locale)
    await new_state.update_data(group_tg_id=message.chat.id)
