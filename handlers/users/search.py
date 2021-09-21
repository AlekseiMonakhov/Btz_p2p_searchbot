from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from states.chat import SetChat
import utils.db_api.commands as db
from utils.misc.throttling import rate_limit
from aiogram.dispatcher.filters import Text
from keyboards.default import main_keyboard
from keyboards.inline import chat_set_method, chat_set_method_all, chat_set, methods_, confirmation_keyboard, cancel_keyboard
from utils.cfg_parser import Cfg
from keyboards.inline.admin import google_stats

from loader import dp

def s(integer: int):
    return f'{integer:,}'.replace(',', '.')


@dp.message_handler(Text(contains='Старт', ignore_case=True), chat_type='private')
async def to_start_search(message: types.Message, user_db):
    chat = await db.get_chat_alert(message.chat.id)

    if not chat.type_search:
        await message.answer('🔔Уведомления о выгодных предложениях c Bitzlato нужно настроить!\n'
                             '⚙Выберите метод поиска.',
                             reply_markup=chat_set_method())
        return

    await db.update_chat_power(message.from_user.id, True)
    await message.answer('🔔Уведомления о выгодных предложениях c Bitzlato включены!',
                         reply_markup=main_keyboard(True, user_db.is_admin))

@dp.callback_query_handler(chat_set.filter(method='show_all'), chat_type='private')
async def to_show_all_methods(call: types.CallbackQuery):
    await call.message.edit_reply_markup(chat_set_method_all())

@dp.callback_query_handler(chat_set.filter(), chat_type='private')
async def to_start_search_method(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    method = int(callback_data.get('method'))

    await state.update_data(method=method)

    text = 'процент(ы)'
    text_2 = '1 или 1.5'
    if method == 7:
        text = 'своё значение'
        text_2 = s(Cfg.Binance.get_official_price())

    await call.answer()

    await call.message.answer(f'🧮Введите {text} для поиска по этому методу.\n'
                              f'⚙Например: {text_2}', reply_markup=cancel_keyboard)

    await SetChat.wait_input_num.set()

@dp.message_handler(state=SetChat.wait_input_num, chat_type='private')
async def to_start_search_input_num(message: types.Message, state: FSMContext):
    data = await state.get_data()

    t = 'Процент'
    n = '1 или 1.5'
    if data['method'] == 7:
        t = 'Своё значение'
        n = s(Cfg.Bitzlato.get_average_price())

    try:
        count = float(message.text)
        if data['method'] != 7:
            if count <= 0 or count > 100:
                await message.answer(f'🧐Вы не правильно ввели {t.lower()} для этого метода.\n'
                                     f'⚙Введите {t.lower()} от 0.1 до 100', reply_markup=cancel_keyboard)
                return
    except ValueError:
        await message.answer(f'🧐Вы не правильно ввели {t.lower()} для этого метода.\n'
                             f'⚙Попробуйте ещё раз, например: {n}', reply_markup=cancel_keyboard)
        return

    await state.update_data(count=count)

    await message.answer('⚙Параметры уведомлений о новых предложениях с Bitzlato.\n'
                         f'📍Метод: {methods_[data["method"]][1:]}\n'
                         f'🧮{t}: {count}', reply_markup=confirmation_keyboard)

    await SetChat.wait_confirm.set()

@dp.callback_query_handler(text='confirm_set', state=SetChat.wait_confirm, chat_type='private')
async def to_start_search_confirm(call: types.CallbackQuery, state: FSMContext, user_db):
    data = await state.get_data()
    chat_id = call.message.chat.id

    await db.update_chat(chat_id, data['method'], data['count'], True)

    await call.message.edit_reply_markup(None)
    await call.message.answer('🔔Уведомления о выгодных предложениях с Bitzlato включены!',
                              reply_markup=main_keyboard(True, user_db.is_admin))

    await state.finish()


@dp.message_handler(Text(contains='Стоп', ignore_case=True), chat_type='private')
async def to_stop_search(message: types.Message, user_db):
    await db.update_chat_power(message.chat.id, False)

    await message.answer('🔕Уведомления о выгодных предложениях c Bitzlato выключены!',
                         reply_markup=main_keyboard(False, user_db.is_admin))


@dp.message_handler(Text(contains='Метод поиска', ignore_case=True), chat_type='private')
async def to_select_search_method(message: types.Message):
    chat = await db.get_chat_alert(message.chat.id)

    if chat.type_search is None or chat.count is None:
        await to_start_search(message)
        return

    method = methods_[chat.type_search]
    text = 'Процент'
    c = '%'
    if methods_[chat.type_search] == 7:
        text = 'Своё значение'
        c = '₽'

    await message.answer(f'📍Хотите выбрать другой метод поиска?\n'
                         f'⚙Сейчас: {method[1:]}\n'
                         f'🧮{text}: {chat.count}{c}', reply_markup=chat_set_method())


@dp.message_handler(Text(contains='Помощь', ignore_case=True), chat_type='private')
async def to_show_help(message: types.Message):
    text = [
        'Бот предназначен для поиска и уведомления пользователя о "выгодных" предложениях, '
        'размещенных на бирже <a href="https://bitzlato.com/p2p?currency=RUB">Битзлато в разделе р2р</a> '
        'предложений о продаже ВТС за рубли.',
        'Для поиска предложений нажмите кнопку Метод поиска, выберите один из методов, '
        'описанных ниже, выставьте процент и нажмите Начать поиск.',
        '"Выгодность" предложений определяется пользователем для себя самостоятельно и '
        'настраивается в разделе Метод поиска.',
        'Мин.БТЗ - бот будет считать предложение выгодным, если его стоимость самая минимальная из существующих '
        'предложений на бирже Битзлато меньше на указанный процент следующего по стоимости предложения.',
        'Сред.БТЗ - бот будет считать предложение выгодным, если оно ниже на указанный процент среднего '
        'значения стоимости всех существующих предложений на бирже Битзлато.',
        'Мед.БТЗ - бот будет считать предложение выгодным, если оно ниже на указанный процент медианного '
        'значения стоимости всех существующих предложений на бирже Битзлато.',
        'Сред.БНС - бот будет считать предложение выгодным, если оно ниже на указанный процент среднего '
        'значения стоимости всех существующих предложений на бирже Бинанс.',
        'Мин.БНС бот будет считать предложение выгодным, если его стоимость самая минимальная из существующих '
        'предложений на бирже Бинанс меньше на указанный процент следующего по стоимости предложения.',
        'Мед.БНС - бот будет считать предложение выгодным, если оно ниже на указанный процент медианного '
        'значения стоимости всех существующих предложений на бирже Бинанс.',
        'Курс.БНС - бот будет считать предложение выгодным, если оно ниже на указанный процент курса '
        'BTC на момент поиска предложений.',
        'Среднее и медианное значение пересчитываются каждые 20 секунд.',
        'Своё значение - бот будет считать предложение выгодным, если оно ниже заданного пользователем значения.',
        'Поиск выгодных предложений можно остановить нажав на кнопку или написать Стоп, или если запустить Старт',
        'По кнопке статистика вы можете увидеть свою статистику пойманных выгодных предложений за 24 часа'
    ]

    await message.answer('\n'.join(text))


@rate_limit(30, 'statistika')
@dp.message_handler(Text(contains='Статистика', ignore_case=True), chat_type='private')
async def to_show_statistics(message: types.Message, user_db):
    msg = await message.answer('⏳Подождите...')

    if str(message.from_user.id) in ADMINS or user_db.is_admin is True:
        reply_markup = google_stats
    else:
        reply_markup = None

    emoji = ['🔹', '🔸']
    send_to = []
    logs = {}

    logs_bitzlato = await db.get_logs(message.from_user.id)
    logs_binance = await db.get_logs_binance(message.from_user.id)
    logs_all = list(logs_binance) + list(logs_bitzlato)

    for log_ in logs_all:
        method = log_.type_search
        count = log_.count

        z = '%'
        if method == 7:
            z = '₽'

        log = f"<b>{methods_[method][1:]}</b> при {count}{z}"
        if c := logs.get(log):
            logs.update({log: c + 1})
        else:
            logs.setdefault(log, 1)

    logs = sorted(logs.items(), key=lambda i: i[1], reverse=True)

    string_count = 0
    for e in logs:
        send_to.append(f'{emoji[string_count % 2]}Метод {e[0]} нашёл <b>{e[1]}</b> предложений')
        string_count += 1

    if string_count == 0:
        await msg.edit_text(f'<b>⏳Ваша статистика за 24 часа</b>\n'
                            '❌Не найдено', reply_markup=reply_markup)
        return

    await msg.edit_text(f'<b>⏳Ваша статистика за 24 часа</b>\n' +
                        '\n'.join(send_to), reply_markup=reply_markup)

@dp.callback_query_handler(text='cancel', state='*', chat_type='private')
async def to_cancel(call: types.CallbackQuery, state: FSMContext):
    if await state.get_state():
        await call.message.edit_text('❌Вы отменили это действие', reply_markup=None)
        await state.finish()
        return
    await call.answer()
