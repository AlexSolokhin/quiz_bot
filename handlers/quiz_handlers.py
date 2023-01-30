from aiogram import types
from aiogram.dispatcher import FSMContext
from asyncio import sleep
from config import bot_logger
from create_bot import bot, dp
from states.states_group import GameState
from quiz_database.db_funcs import create_user_if_not_exist
from keyboards.quiz_keyboards import lets_play_keyboard, choose_quiz_keyboard
from utils.quiz_functions import start_quiz, next_poll, save_answer
from utils.custom_filters import PollStateFilter


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message) -> None:
    """
    Команда старт. Регистрирует пользователя, если он не пользовался ботом раньше и предлагает сыграть в квиз.

    :param message: объект сообщения
    :type message: types.Message
    :return: None
    """

    tg_id = message.from_user.id
    tg_username = message.from_user.username
    await create_user_if_not_exist(tg_id, tg_username)
    await GameState.invitation.set()
    await bot.send_message(tg_id, "👋<b>Привет!</b>\nСо мной ты можешь проверить свои знания в различных сферах🔬\n"
                                  "Хочешь сыграть? 🎮",
                           reply_markup=await lets_play_keyboard(),
                           parse_mode="HTML")


@dp.message_handler(commands=["help"])
async def help_handler(message: types.Message) -> None:
    """
    Команда help. Рассказывает о том, что делает бот.

    :param message: объект сообщения
    :type message: types.Message
    :return: None
    """

    tg_id = message.from_user.id
    await bot.send_message(tg_id, "👋<b>Привет!</b>\nЯ квиз-бот. Если хочешь сыграть, введи команду <b>/start</b>\n"
                                  "Хочешь сыграть? 🎮",
                           parse_mode="HTML")


@dp.callback_query_handler(lambda callback: callback.data == 'start_new_game', state=GameState.invitation)
async def choose_quiz_handler(callback: types.CallbackQuery) -> None:
    """
    Инлайн хэндлер, запускает выбор квиза для игры".

    :param callback: объект CallbackQuery
    :type callback: types.CallbackQuery
    :return: None
    """

    tg_id = callback.from_user.id
    await callback.answer()
    await GameState.choose_quiz.set()
    await bot.send_message(tg_id, "🎲Выбери квиз, в который ты хочешь сыграть:",
                           reply_markup=await choose_quiz_keyboard())


@dp.callback_query_handler(lambda callback: callback.data == 'cancel_game',
                           state=[GameState.invitation, GameState.challenged])
async def cancel_game_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Инлайн хэндлер, отменяющий игру".

    :param callback: объект CallbackQuery
    :type callback: types.CallbackQuery
    :param state: стэйт
    :type: FSMContext
    :return: None
    """

    tg_id = callback.from_user.id
    await callback.answer()
    await state.finish()
    await bot.send_message(tg_id, "😔Очень жаль!\n Если захочешь сыграть просто введи <b>/start</b>",
                           parse_mode="HTML")


@dp.callback_query_handler(lambda callback: callback.data.isdigit(),
                           state=[GameState.choose_quiz, GameState.challenged])
async def launch_quiz_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Инлайн хэндлер, запускающий выбранный или предложенный квиз".

    :param callback: объект CallbackQuery
    :type callback: types.CallbackQuery
    :param state: стэйт
    :type: FSMContext
    :return: None
    """

    tg_id = callback.from_user.id
    await callback.answer()
    try:
        quiz_id = int(callback.data)
        await GameState.quiz_in_progress.set()
        await start_quiz(quiz_id, tg_id, state)
        await next_poll(tg_id, state)
    except ValueError as exc:
        bot_logger.error(f'Некорректный id квиза: {exc}')
        await state.finish()


@dp.poll_answer_handler(PollStateFilter())
async def answer_handler(poll_answer: types.PollAnswer) -> None:
    """
    Обработчик ответа на вопрос квиза

    :param poll_answer: объект PollAnswer с информацией о голосующем
    :type poll_answer: types.PollAnswer
    :return None
    """

    tg_id = poll_answer.user.id
    option_ids = poll_answer.option_ids
    state = dp.get_current().current_state()

    async with state.proxy() as data:
        stop_message_id = data.get('stop_message_id')

    await save_answer(option_ids, state)
    await sleep(0.1)
    await bot.delete_message(tg_id, stop_message_id)
    await next_poll(tg_id, state)


@dp.callback_query_handler(lambda callback: callback.data == 'stop_game',
                           state=GameState.quiz_in_progress)
async def stop_game_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Инлайн хэндлер, останавливающий запущенный квиз.

    :param callback: объект CallbackQuery
    :type callback: types.CallbackQuery
    :param state: стэйт
    :type: FSMContext
    :return: None
    """

    tg_id = callback.from_user.id
    await callback.answer()
    await state.finish()
    await bot.send_message(tg_id, "🛑Игра остановлена. Возвращайся в любое время!\n"
                                  "Для этого введи <b>/start</b>",
                           parse_mode='HTML')


@dp.message_handler(state=GameState.quiz_in_progress)
async def you_are_in_game_handler(message: types.Message) -> None:
    """
    Хэндлер, напоминающий пользователю, что он в игре, в ответ на сообщение во время квиза.

    :param message: объект сообщения
    :type message: types.Message
    :return: None
    """

    tg_id = message.from_user.id
    await bot.send_message(tg_id, "🎮Ты ещё в игре! Если хочешь прервать квиз, нажми на кнопку☝️")
