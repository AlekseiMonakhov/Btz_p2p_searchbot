from aiogram import types


def main_keyboard(power: bool, is_admin: bool = False):
    """Клавиатура для управления только в ЛС"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if power is True:
        keyboard.insert(types.KeyboardButton(text='🔴Стоп'))
    else:
        keyboard.insert(types.KeyboardButton(text='🟢Старт'))
    keyboard.insert(types.KeyboardButton(text='📘Помощь'))
    keyboard.row(types.KeyboardButton(text='🔎Метод поиска'))
    keyboard.insert(types.KeyboardButton(text='📊Статистика'))

    if is_admin is True:
        keyboard.row(types.KeyboardButton(text='🔮Админ панель'))
    return keyboard
