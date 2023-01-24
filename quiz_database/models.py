from peewee import Model, CharField, TextField, IntegerField, BooleanField, ForeignKeyField, DateTimeField, Check
from playhouse.sqlite_ext import JSONField
from datetime import datetime
from config import DB


class User(Model):
    """
    Модель описывает пользователя.
    """
    tg_id = IntegerField(unique=True)
    tg_username = CharField(unique=True)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DB
        db_table = 'users'


class Quiz(Model):
    """
    Модель описывает квиз.
    """
    quiz_name = CharField(max_length=50, verbose_name='quiz name')
    active = BooleanField(default=True, verbose_name='active status')

    class Meta:
        database = DB
        db_table = 'quiz'


class Question(Model):
    """
    Модель описывает вопросы квиза. Предполагается, что вопросы не повторяются в разных квизах.
    """
    question = TextField(verbose_name='question')
    quiz = ForeignKeyField(model=Quiz, backref='questions', on_delete='CASCADE', lazy_load=False, verbose_name='quiz')
    options = JSONField(default=[])
    correct_answer = IntegerField(null=True, default=None,
                                  verbose_name='correct answer')
    explanation = CharField(null=True, default=None, verbose_name='explanation')

    class Meta:
        database = DB
        db_table = 'questions'


class QuizResult(Model):
    """
    Модель описывает результаты для каждого игрока.
    """
    user = ForeignKeyField(model=User, backref='results', on_delete='CASCADE', lazy_load=False, verbose_name='user')
    quiz = ForeignKeyField(model=Quiz, backref='results', on_delete='CASCADE', lazy_load=False, verbose_name='quiz')
    answers = JSONField(default={}, verbose_name='answers')
    scores = IntegerField(null=True, default=None, verbose_name='user scores')
    finished = DateTimeField(default=datetime.now())

    class Meta:
        database = DB
        db_table = 'quiz_results'


if __name__ == '__main__':
    User.create_table()
    Quiz.create_table()
    Question.create_table()
    QuizResult.create_table()
