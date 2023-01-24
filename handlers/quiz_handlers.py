from aiogram import types
from aiogram.dispatcher import FSMContext
from time import sleep
from config import bot_logger
from create_bot import bot, dp
from states.states_group import GameState
from quiz_database.db_funcs import create_user_if_not_exist
from keyboards.quiz_keyboards import lets_play_keyboard, choose_quiz_keyboard
from utils.quiz_functions import start_quiz, next_poll, save_answer


@dp.message_handler(commands=["start"], state=None)
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

    await bot.send_message(tg_id, "👋<b>Привет!</b>\nСо мной ты можешь проверить свои знания в различных сферах🔬\n"
                                  "Хочешь сыграть? 🎮",
                           reply_markup=await lets_play_keyboard(),
                           parse_mode="HTML")


@dp.message_handler(commands=["help"], state=None)
async def help_handler(message: types.Message) -> None:
    """
    Команда help. Рассказывает о том, что делает бот.

    :param message: объект сообщения
    :type message: types.Message
    :return: None
    """

    tg_id = message.from_user.id
    await bot.send_message(tg_id, "👋<b>Привет!</b>\nЯ квиз-бот. Если хочешь сыграть, введи команду <b>start</b>\n"
                                  "Хочешь сыграть? 🎮",
                           parse_mode="HTML")


@dp.callback_query_handler(state=None)
async def lets_play_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Инлайн хэндлер, запускающий игру".

    :param callback: объект CallbackQuery
    :type callback: types.CallbackQuery
    :param state: стэйт
    :type: FSMContext
    :return: None
    """

    await callback.answer()
    tg_id = callback.from_user.id

    if callback.data == '-1':
        await bot.send_message(tg_id, "😔Очень жаль!\n Если захочешь сыграть просто введи <b>/start</b>",
                               parse_mode="HTML")
    elif callback.data == '0':
        await GameState.quiz.set()
        await bot.send_message(tg_id, "🎲Выбери квиз, в который ты хочешь сыграть:",
                               reply_markup=await choose_quiz_keyboard())
    else:
        await GameState.quiz.set()
        try:
            quiz_id = int(callback.data)
            await start_quiz(quiz_id, tg_id, state)
            await next_poll(tg_id, state)
        except ValueError as exc:
            bot_logger.error(f'Некорректный id квиза: {exc}')


@dp.poll_answer_handler()
async def answer_handler(quiz_answer: types.PollAnswer) -> None:
    """
    Обработчик ответа на вопрос квиза

    :param quiz_answer: объект PollAnswer с информацией о голосующем
    :type quiz_answer: types.PollAnswer
    :return None
    """

    tg_id = quiz_answer.user.id
    option_ids = quiz_answer.option_ids
    state = dp.get_current().current_state()

    await save_answer(option_ids, state)
    sleep(0.1)
    await next_poll(tg_id, state)
