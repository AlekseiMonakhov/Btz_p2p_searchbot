from aiogram import types

def buy_keyboard(id_buy):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text='Перейти к покупке',
                    url=f'bitzlato.com/ru/p2p/exchange/{id_buy}/buy-BTC-RUB'
                )
            ]
        ]
    )
    return keyboard

def buy_keyboard_binance():
    # Хотелось бы сразу что бы по ссылке попадать на оффер, а не список офферов
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text='Перейти к покупке',
                    url=f'p2p.binance.com/ru/trade/buy/BTC'
                )
            ]
        ]
    )
    return keyboard
