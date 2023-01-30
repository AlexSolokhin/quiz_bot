from create_bot import bot
from aiogram.dispatcher import FSMContext
from states.states_group import GameState
from quiz_database.db_funcs import get_user, get_quiz_questions, save_results
from keyboards.quiz_keyboards import lets_play_keyboard, stop_game_keyboard


async def start_quiz(quiz_id: int, tg_id: int, state: FSMContext) -> None:
    """
    Запуск квиза с указанным id

    :param quiz_id: id квиза
    :type quiz_id: int
    :param tg_id: telegram id пользователя
    :type tg_id: int
    :param state: стэйт
    :type: FSMContext
    :return: None
    """

    user = await get_user(tg_id)
    user_id = user.id
    questions = await get_quiz_questions(quiz_id)

    async with state.proxy() as data:
        data['quiz'] = quiz_id
        data['user'] = user_id
        data['questions'] = questions
        data['cur_question'] = 0
        data['answers'] = {}
        data['scores'] = 0


async def next_poll(tg_id: int, state: FSMContext) -> None:
    """
    Отправляет следующий вопрос квиза пользователю

    :param tg_id: telegram id пользователя
    :type tg_id: int
    :param state: стэйт
    :type: FSMContext
    :return: None
    """

    async with state.proxy() as data:
        questions = data.get('questions')
        curr_question = data.get('cur_question')
    try:
        question = questions[curr_question]
        cur_poll = await bot.send_poll(chat_id=tg_id,
                                       question=question.question,
                                       options=question.options,
                                       correct_option_id=question.correct_answer,
                                       explanation=question.explanation,
                                       is_anonymous=False,
                                       type='quiz'
                                       )
        stop_message = await bot.send_message(tg_id, 'Чтобы прервать игру, нажми кнопку ☟',
                                              reply_markup=await stop_game_keyboard())
        async with state.proxy() as data:
            data['next_question'] = question
            data['cur_question'] += 1
            data['stop_message_id'] = stop_message.message_id
            data['poll_id'] = cur_poll.poll.id
    except IndexError:
        await finish_quiz(tg_id, state)


async def save_answer(option_ids: list, state: FSMContext):
    """
    Проверяет и сохраняет ответ

    :param option_ids: список ответов пользователя
    :type option_ids: list
    :param state: стэйт
    :type: FSMContext
    :return: None
    """

    async with state.proxy() as data:
        question = data.get('next_question')
        answer_id = option_ids[0]
        data['answers'][question.id] = answer_id
        if question.correct_answer == answer_id:
            data['scores'] += 1


async def finish_quiz(tg_id: int, state: FSMContext):
    """
    Завершает квиз: сохраняет результат и отправляет результаты пользователю

    :param tg_id: telegram id пользователя
    :type tg_id: int
    :param state: стэйт
    :type: FSMContext
    :return: None
    """
    async with state.proxy() as data:
        quiz_id = data.get('quiz')
        user_id = data.get('user')
        answers = data.get('answers')
        scores = data.get('scores')
        q_num = data.get('cur_question')

    await save_results(quiz_id, user_id, answers, scores)
    await bot.send_message(tg_id, f"🎉<b>Поздравляю!</b>\n"
                                  f"Ты успешно прошёл квиз и правильно ответил на <b>{scores} из {q_num}</b> вопросов",
                           parse_mode="HTML")
    await GameState.invitation.set()
    await bot.send_message(tg_id, "Хочешь сыграть ещё?",
                           reply_markup=await lets_play_keyboard(),
                           parse_mode="HTML")
