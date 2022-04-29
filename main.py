from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from deploy.config import TOKEN
from markup.keyboards import main_menu, cancel_menu
from models.db_api import data_api
from state.state import CreatePhrase

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(text="❌Отмена", state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await state.reset_data()
    await bot.send_message(message.chat.id, "Операция прервана", reply_markup=main_menu)


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE))
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.id > 0:
        await bot.send_message(message.chat.id, "Начинаем работать", reply_markup=main_menu)


@dp.message_handler(text="➕Добавить фразу")
async def create_phrase(message: types.Message):
    if message.chat.id > 0:
        await bot.send_message(message.chat.id, "Введите фразу которую нужно внести в базу", reply_markup=cancel_menu)
        await CreatePhrase.first()


@dp.message_handler(state=CreatePhrase.phrase)
async def create_phrase(message: types.Message, state: FSMContext):
    if message.chat.id > 0:
        await state.update_data(phrase=message.text)
        await bot.send_message(message.chat.id,
                               "Введите имя и фамилию (опционально) автора сего прекрасного изречения",
                               reply_markup=cancel_menu)
        await CreatePhrase.next()


@dp.message_handler(state=CreatePhrase.name)
async def create_phrase(message: types.Message, state: FSMContext):
    if message.chat.id > 0:
        await state.update_data(name=message.text)
        data = await state.get_data()
        data_api.set_custom_phrase(data)

        await bot.send_message(message.chat.id,
                               "Данные внесены в базу, приятного времени суток",
                               reply_markup=main_menu)
        await state.finish()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.GROUP))
async def chat_group(message: types.Message):
    text_lower = message.text.lower()
    if text_lower.find("пром") >= 0:
        await bot.send_message(message.chat.id, data_api.get_random_phrase())


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE))
async def chat_group(message: types.Message):
    try:
        user_id = data_api.set_user(telegram_id=message.forward_from.id,
                                    last_name=message.forward_from.last_name,
                                    first_name=message.forward_from.first_name)

        if data_api.set_phrase(text=message.text, user_id=user_id):
            await bot.send_message(message.chat.id, "Фраза успешно добавлена")
        else:
            await bot.send_message(message.chat.id, "Что то пошло не так, попробуйте ещё раз")

    except AttributeError:
        await bot.send_message(message.chat.id, "Нужно пересылать сообщения, чтобы я внёс их в базу или воспользоваться механизмом диалога")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
