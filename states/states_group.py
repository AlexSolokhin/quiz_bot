from aiogram.dispatcher.filters.state import StatesGroup, State


class GameState(StatesGroup):
    quiz = State()
    challenge = State()
