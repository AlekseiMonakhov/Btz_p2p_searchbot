from aiogram import types
from aiogram.utils.callback_data import CallbackData
from keyboards.inline.admin import admin_call, give_sub
from datetime import datetime, timedelta

chat_set = CallbackData('chat_set', 'method')

methods__ = {
     1: '🔴Сред.БТЗ', 2: '🟠Мед.БТЗ',
     3: '🟡Мин.БТЗ',
     4: '🟢Сред.БНС', 5: '🟣Мед.БНС',
     6: '🟤Курс.БНС',
     7: '🔵Своё значение'
     }

methods_ = {
     1: '🟡Мин.БТЗ', 2: '⚪Мин.БНС',
     3: '🔴Сред.БТЗ', 4: '🟢Сред.БНС',
     5: '🟠Мед.БТЗ', 6: '🟣Мед.БНС',
     7: '🔵Своё значение', 8: '🟤Курс.БНС',
     }

def times():
    # Как добавить больше вариантов выбора времени подписки?
    # Всё просто! '15 мин.' это название кнопки
    # datetime.now() + timedelta(minutes=15, seconds=1)
    # Это время до какого будет действовать подписка
    # Проще говоря мы настраиваем timedelta(...)
    # Это метод который как бы добавляет к сейчас времени ещё
    # Если написать + timedelta(minutes=60) к настоящему времени
    # То получаем будущее время т.е. к примеру было 16:50
    # Мы добавляем timedelta(minutes=60) 60 минут
    # Получаем 17:50, этот мини гайд не для программиста
    # https://pythonworld.ru/moduli/modul-datetime.html возможно это поможет
    return {
        '15 мин.': datetime.now() + timedelta(minutes=15, seconds=1),
        '30 мин.': datetime.now() + timedelta(minutes=30, seconds=1),
        '1 час': datetime.now() + timedelta(hours=1, seconds=1),
        '3 часа': datetime.now() + timedelta(hours=3, seconds=1),
        '6 часов': datetime.now() + timedelta(hours=6, seconds=1),
        '12 часов': datetime.now() + timedelta(hours=12, seconds=1),
        '1 день': datetime.now() + timedelta(days=1, seconds=1),
        '3 дня': datetime.now() + timedelta(days=3, seconds=1),
        '6 дней': datetime.now() + timedelta(days=6, seconds=1),
        '15 дней': datetime.now() + timedelta(days=15, seconds=1),
        '30 дней': datetime.now() + timedelta(days=30, seconds=1),
        '60 дней': datetime.now() + timedelta(days=60, seconds=1),
        '90 дней': datetime.now() + timedelta(days=90, seconds=1),
        '180 дней': datetime.now() + timedelta(days=180, seconds=1),
        '365 дней': datetime.now() + timedelta(days=365, seconds=1),
    }


def chat_set_method1():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for i in methods_:
        keyboard.insert(
            types.InlineKeyboardButton(
                text=methods_[i],
                callback_data=chat_set.new(method=i)
            )
        )
    return keyboard

def chat_set_method():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for i in range(1, 3):
        keyboard.insert(
            types.InlineKeyboardButton(
                text=methods_[i],
                callback_data=chat_set.new(method=i)
            )
        )
    keyboard.row(types.InlineKeyboardButton(text='⬇Другое', callback_data=chat_set.new(method='show_all')))
    return keyboard

def chat_set_method_all():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for i in methods_:
        keyboard.insert(
            types.InlineKeyboardButton(
                text=methods_[i],
                callback_data=chat_set.new(method=i)
            )
        )
    return keyboard



confirmation_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text='Применить',
                callback_data='confirm_set'
            ),
            types.InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel'
            )
        ]
    ]
)

cancel_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text='Отменить',
                callback_data='cancel'
            )
        ]
    ]
)

def request_sub(id_: int):
    return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text='♦Выдать подписку',
                        callback_data=admin_call.new(action='give_sub', arg=id_)
                    ),
                    types.InlineKeyboardButton(
                        text='🤐Игнорировать',
                        callback_data=admin_call.new(action='ignore_user', arg=str(id_) + '-')
                    )
                ]
            ]
    )


def get_time(id_: int):
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    times_ = times()
    for time in times_:
        keyboard.insert(types.InlineKeyboardButton(
                    text=time,
                    callback_data=give_sub.new(id_=id_, time_index=list(times_.keys()).index(time))
        ))
    return keyboard


