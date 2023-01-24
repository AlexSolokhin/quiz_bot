from create_bot import bot
from aiogram.dispatcher import FSMContext
from quiz_database.db_funcs import get_user, get_quiz_questions, save_results
from keyboards.quiz_keyboards import lets_play_keyboard


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
        questions = data['questions']
        curr_question = data['cur_question']
    try:
        question = questions[curr_question]
        async with state.proxy() as data:
            data['next_question'] = question
            data['cur_question'] += 1

        await bot.send_poll(chat_id=tg_id,
                            question=question.question,
                            options=question.options,
                            correct_option_id=question.correct_answer,
                            explanation=question.explanation,
                            is_anonymous=False,
                            type='quiz'
                            )
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
        question = data['next_question']
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
        quiz_id = data['quiz']
        user_id = data['user']
        answers = data['answers']
        scores = data['scores']
        q_num = data['cur_question']

    await save_results(quiz_id, user_id, answers, scores)
    await bot.send_message(tg_id, f"🎉<b>Поздравляю!</b>\n"
                                  f"Ты успешно прошёл квиз и правильно ответил на <b>{scores} из {q_num}</b> вопросов",
                           parse_mode="HTML")
    await state.finish()
    await bot.send_message(tg_id, "Хочешь сыграть ещё?",
                           reply_markup=await lets_play_keyboard(),
                           parse_mode="HTML")


