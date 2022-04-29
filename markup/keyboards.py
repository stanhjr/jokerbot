from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

create_phrase_button = KeyboardButton("➕Добавить фразу")
cancel_button = KeyboardButton("❌Отмена")

main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(create_phrase_button)
cancel_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)
