from aiogram import types
from aiogram.dispatcher import FSMContext
from time import sleep
from config import bot_logger
from create_bot import bot, dp
from states.states_group import GameState
from quiz_database.db_funcs import get_user, get_all_user, get_quiz
from keyboards.quiz_keyboards import lets_play_keyboard, choose_quiz_keyboard


@dp.message_handler(commands=["mass_quiz"], state=None)
async def mass_quiz_handler(message: types.Message) -> None:
    """
    Команда массового приглашения на квиз.
    Рассылает пользователям приглашение принять участие в квизе

    :param message: объект сообщения
    :type message: types.Message
    :return: None
    """

    tg_id = message.from_user.id
    user = await get_user(tg_id)

    if user.is_admin:
        await GameState.challenge.set()
        await bot.send_message(tg_id, "👋<b>Привет!</b>\nВы хотите пригласить всех игроков пройти квиз\n"
                                      "В какой квиз вы хотите их пригласить?",
                               reply_markup=await choose_quiz_keyboard(),
                               parse_mode="HTML")
    else:
        await bot.send_message(tg_id, "Извините, но только админы могут делать массовые приглашения на квиз😔")

    @dp.callback_query_handler(state=GameState.challenge)
    async def choose_challenge_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
        """
        Инлайн хэндлер, рассылающий массовое приглашение сыграть в квиз.".

        :param callback: объект CallbackQuery
        :type callback: types.CallbackQuery
        :param state: стэйт
        :type: FSMContext
        :return: None
        """

        await callback.answer()
        try:
            quiz_id = int(callback.data)
            quiz = await get_quiz(quiz_id)
            users = await get_all_user()
            for cur_user in users:
                await bot.send_message(cur_user.tg_id,
                                       f"👋<b>Привет!</b>\nТебе бросили вызов!🐱‍👤\n"
                                       f"Хочешь сыграть в квиз '{quiz.quiz_name}'?",
                                       reply_markup=await lets_play_keyboard(quiz_id),
                                       parse_mode="HTML"
                                       )
                sleep(0.01)
        except ValueError as exc:
            bot_logger.error(f'Некорректный id квиза: {exc}')
        finally:
            await state.finish()
