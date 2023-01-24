from config import DB, db_logger
from quiz_database.models import User, Quiz, QuizResult
from peewee import InternalError


async def create_user_if_not_exist(tg_id: int, tg_username: str) -> None:
    """
    Создаёт пользователя, если он не был создан ранее

    :param tg_id: id юзера в Telegram
    :type tg_id: int
    :param tg_username: имя пользователя в Tg
    :type tg_username: str
    :return: None
    """

    try:
        with DB:
            User.get_or_create(tg_id=tg_id, tg_username=tg_username)
    except InternalError as exc:
        db_logger.error(f'Error while checking user existence: {exc}')


async def get_user(tg_id: int) -> User:
    """
    Возвращает юзера по telegram ID

    :param tg_id: id юзера в Telegram
    :type tg_id: int
    :return: None
    """

    try:
        with DB:
            user = User.get(tg_id=tg_id)
            return user
    except InternalError as exc:
        db_logger.error(f'Error while checking user existence: {exc}')


async def get_all_user() -> list:
    """
    Возвращает всех пользователей

    :return: Список всех пользователей
    :rtype: list
    """

    try:
        with DB:
            return [user for user in User.select()]
    except InternalError as exc:
        db_logger.error(f'Error while checking user existence: {exc}')


async def get_quiz(quiz_id: int) -> Quiz:
    """
    Возвращает квиз по id

    :param quiz_id: id юзера в Telegram
    :type quiz_id: int
    :return: None
    """

    try:
        with DB:
            quiz = Quiz.get(id=quiz_id)
            return quiz
    except InternalError as exc:
        db_logger.error(f'Error while checking user existence: {exc}')


async def get_active_quiz() -> list:
    """
    Возвращает список активных квизов

    :return: список активных квизов
    :rtype: list
    """

    try:
        with DB:
            query = Quiz.select().where(Quiz.active)
            return [quiz for quiz in query]
    except InternalError as exc:
        db_logger.error(f'Error while checking user existence: {exc}')


async def get_quiz_questions(quiz_id: int) -> list:
    """
    Возвращает список вопросов для выбранного квиза

    :param quiz_id: id квиза
    :type quiz_id: int
    :return: список вопросов квиза
    :rtype: list
    """

    try:
        with DB:
            quiz = Quiz.get(Quiz.id == quiz_id)
            return [question for question in quiz.questions]
    except InternalError as exc:
        db_logger.error(f'Error while checking user existence: {exc}')


async def save_results(quiz_id: int, user_id: int, answers: dict, scores: int) -> None:
    """
    Создание записи о результатах пользователя.

    :param quiz_id: id квиза
    :param user_id: id пользователя
    :param answers: словарь с ответами пользователя
    :param scores: набранные очки
    :return: None
    """
    try:
        with DB:
            results = QuizResult(quiz_id=quiz_id, user_id=user_id, answers=answers, scores=scores)
            results.save()
    except InternalError as exc:
        db_logger.error(f'Error while checking user existence: {exc}')