from aiogram import types
from aiogram.utils.callback_data import CallbackData

from data.config import google_table_url

admin_call = CallbackData('admin_call', 'action', 'arg')
show_user = CallbackData('show_user', 'id_', 'action', 'arg')
give_sub = CallbackData('give_sub', 'id_', 'time_index')


admin_panel = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text='Пользователи',
                callback_data=admin_call.new(action='show_users', arg='0-20')
            ),
        ],
        [
            types.InlineKeyboardButton(
                text='Обновить данные от бирж',
                callback_data=admin_call.new(action='call_consider', arg='now')
            )
        ]
    ]
)

google_stats = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text='Полная статистика',
                        url=google_table_url
                    )
                ]
            ]
        )
