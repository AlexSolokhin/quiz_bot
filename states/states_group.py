from aiogram.dispatcher.filters.state import StatesGroup, State


class GameState(StatesGroup):
    invitation = State()
    challenged = State()
    choose_quiz = State()
    quiz_in_progress = State()


class AdminState(StatesGroup):
    mass_quiz = State()
