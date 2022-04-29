from aiogram.dispatcher.filters.state import StatesGroup, State


class CreatePhrase(StatesGroup):
    phrase = State()
    name = State()
