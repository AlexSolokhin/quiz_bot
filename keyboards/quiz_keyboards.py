from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from quiz_database.db_funcs import get_active_quiz


async def lets_play_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура, приглашающая сыграть в квиз.

    :return: объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """

    keyboard = InlineKeyboardMarkup()

    lets_play = InlineKeyboardButton(text="🎮Давай сыграем!", callback_data='start_new_game')
    another_time = InlineKeyboardButton(text="💔В другой раз", callback_data='cancel_game')

    keyboard.add(lets_play, another_time)

    return keyboard


async def choose_quiz_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора квиза из списка активных.

    :return: объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """

    keyboard = InlineKeyboardMarkup()
    active_quiz = await get_active_quiz()

    for quiz in active_quiz:
        quiz_button = InlineKeyboardButton(text=quiz.quiz_name, callback_data=str(quiz.id))
        keyboard.add(quiz_button)

    return keyboard


async def stop_game_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для остановки запущенной игры.

    :return: объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """

    keyboard = InlineKeyboardMarkup()

    stop_game = InlineKeyboardButton(text="🛑", callback_data='stop_game')
    keyboard.add(stop_game)

    return keyboard


async def quiz_challenge_keyboard(quiz_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для использования в массовых рассылках, предлагающая в квиз с id == quiz_id.

    :param quiz_id: id_квиза
    :type quiz_id: int
    :return: объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """

    keyboard = InlineKeyboardMarkup()

    lets_play = InlineKeyboardButton(text="⚔️Принимаю вызов!", callback_data=str(quiz_id))
    another_time = InlineKeyboardButton(text="💔В другой раз", callback_data='cancel_game')

    keyboard.add(lets_play, another_time)

    return keyboard