from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from quiz_database.db_funcs import get_active_quiz


async def lets_play_keyboard(quiz_id: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура, приглашающая сыграть в квиз.
    Если в качестве quiz_id передан 0, предложит выбрать квиз из списка активных.

    :param quiz_id: id квиза, который нужно запустить
    :type quiz_id: int
    :return: объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """

    keyboard = InlineKeyboardMarkup()

    lets_play = InlineKeyboardButton(text="🎮Давай сыграем!", callback_data=str(quiz_id))
    another_time = InlineKeyboardButton(text="💔В другой раз", callback_data='-1')

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
