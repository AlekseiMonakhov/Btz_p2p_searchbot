from loguru import logger
from aiogram import types
import humanize
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from data.config import ADMINS
from keyboards.default import main_keyboard
from keyboards.inline.admin import admin_panel, admin_call, show_user, give_sub
from handlers.users.bitzlato_p2p_alert import consider
import utils.db_api.commands as db
from keyboards.inline import methods_, times
from filters import Admin
from keyboards.inline.chat import get_time
from utils.cfg_parser import Cfg
from aiogram.utils.markdown import quote_html

from loader import dp

humanize.i18n.activate("ru_RU")

def s(integer: int):
    return f'{integer:,}'.replace(',', '.')


@dp.message_handler(Admin(), Text(contains='Админ панель', ignore_case=True), chat_type='private')
async def to_show_admin_panel(message: types.Message, update_message=False):
    last_update = Cfg.last_update
    bz_av_price = Cfg.Bitzlato.get_average_price()
    bz_md_price = Cfg.Bitzlato.get_median_price()

    bn_av_price = Cfg.Binance.get_average_price()
    bn_md_price = Cfg.Binance.get_median_price()
    bn_of_price = Cfg.Binance.get_official_price()

    text = [f'📍<b>Админ панель</b>',
            f'🟠Bitzlato:',
            f'🔹Средняя: {s(bz_av_price)}₽',
            f'🔹Медианная: {s(bz_md_price)}₽',
            f'🟡Binance:',
            f'🔹Средняя: {s(bn_av_price)}₽',
            f'🔹Медианная: {s(bn_md_price)}₽',
            f'🔹Официальная: {s(bn_of_price)}₽',
            f'🕰Последнее обновление: {humanize.naturaltime(last_update)}']
    if update_message is False:
        await message.answer('\n'.join(text), reply_markup=admin_panel)
    elif update_message is True:
        await message.edit_text('\n'.join(text), reply_markup=admin_panel)


@dp.callback_query_handler(Admin(), admin_call.filter(action='call_consider'), chat_type='private')
async def to_show_consider(call: types.CallbackQuery):
    text = 'Данные обновлены!'
    try:
        logger.info(f'{call.from_user.full_name} обновил данные с Bitzlato/Binance!')
        await consider()
    except Exception as err:
        logger.info('Ошибка при получении данных c Bitzlato/Binance!')
        logger.error(err)
        text = f'Ошибка!\n{err}'
    await call.answer(text, show_alert=True, cache_time=3)
    call.message.from_user.id = call.from_user.id
    await to_show_admin_panel(call.message, update_message=True)


@dp.callback_query_handler(Admin(), admin_call.filter(action='show_users'), chat_type='private')
async def to_show_users(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    users = types.InlineKeyboardMarkup(row_width=2)
    arg = callback_data.get('arg')
    skip, limit = (int(e) for e in arg.split('-'))
    await state.update_data(show_users_arg=arg)

    i = 0
    for user in await db.get_users(skip, limit + 1):
        is_access = db.check_access(user)
        if is_access is None:
            is_access = '◼'
        elif is_access is False:
            is_access = '❌'
        else:
            is_access = '✅'
        if user.is_admin is True:
            is_access = '👮'
            if str(user.id_) in ADMINS:
                is_access = '🎩'
        i += 1
        if i != 21:
            users.insert(
                types.InlineKeyboardButton(
                    text=is_access + user.name,
                    callback_data=show_user.new(id_=user.id_, action='show', arg='show')
                )
            )

    if skip != 0:
        users.row(
            types.InlineKeyboardButton(
                text='⬅',
                callback_data=admin_call.new(action='show_users', arg=f'{skip - 20}-{limit - 20}')
            )
        )
        if i == 21:
            users.insert(
                types.InlineKeyboardButton(
                    text='➡',
                    callback_data=admin_call.new(action='show_users', arg=f'{skip + 20}-{limit + 20}')
                )
            )
    else:
        if i == 21:
            users.row(
                types.InlineKeyboardButton(
                    text='➡',
                    callback_data=admin_call.new(action='show_users', arg=f'{skip + 20}-{limit + 20}')
                )
            )

    count_users = await db.get_count_users()
    await call.answer()
    await call.message.edit_text(f'📍<b>Админ панель</b>\n'
                                 f'✏<i>Пользователи</i>\n'
                                 f'👤Всего: {count_users} пользователей\n\n'
                                 f'✅ - Есть подписка\n'
                                 f'❌ - Подписка истекла\n'
                                 f'◼ - Совершенно новый юзер\n'
                                 f'👮‍️- Админ\n'
                                 f'🎩 - Владелец', reply_markup=users)


@dp.callback_query_handler(Admin(), show_user.filter(action='show'), chat_type='private')
async def to_show_user(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    id_ = int(callback_data.get('id_'))
    user = await db.get_user(id_)
    chat = await db.get_chat_alert(id_)
    data = await state.get_data()
    try:
        show_users_arg = data['show_users_arg']
    except KeyError:
        show_users_arg = '0-20'

    username = 'Отсутствует'
    if user.username:
        username = '@' + user.username

    is_admin = 'Нету'
    if user.is_admin is True:
        is_admin = 'Администратор'
        if str(user.id_) in ADMINS:
            is_admin = 'Владелец'

    is_access = 'Есть'
    if user.is_access is False:
        is_access = 'Нет'

    sub = 'Не было'
    sub_time = ''
    if user.time_access:
        if db.check_access(user) is False:
            sub = f'Закончилась\n'
            sub_time = f'🕐До: {user.time_access.strftime("%Y-%m-%d %X")}\n' \
                       f'⏳Закончилась {humanize.naturaltime(user.time_access)}'
        elif db.check_access(user) is True:
            sub = f'Активна\n'
            sub_time = f'🕐До: {user.time_access.strftime("%Y-%m-%d %X")}\n' \
                       f'⏳Закончится {humanize.naturaltime(user.time_access)}'

    create_at = f'Создана: {user.create_at.strftime("%Y-%m-%d %X")} ({humanize.naturaltime(user.create_at)})'
    updated_at = f'Обновлена: {user.updated_at.strftime("%Y-%m-%d %X")} ({humanize.naturaltime(user.updated_at)})'

    power = 'Выключено'
    if chat.power is True:
        power = 'Включено\n' \
                f'🧮Метод: {methods_[chat.type_search][1:]}\n' \
                f'⚖Процент/значение: {chat.count}'

    actions = types.InlineKeyboardMarkup(row_width=2)
    if str(id_) not in ADMINS and user.id_ != call.from_user.id:
        actions.insert(types.InlineKeyboardButton(
            text='💳Подписка',
            callback_data=admin_call.new(action='main_sub', arg=user.id_)))

    if str(id_) not in ADMINS and user.id_ != call.from_user.id:
        actions.insert(types.InlineKeyboardButton(
            text='❌Удалить',
            callback_data=admin_call.new(action='set_access', arg=user.id_)))
        actions.insert(types.InlineKeyboardButton(
            text='🤐Игнорировать',
            callback_data=admin_call.new(action='ignore_user', arg=user.id_)
        ))

    if str(call.from_user.id) in ADMINS:
        if is_admin == 'Нету':
            actions.insert(types.InlineKeyboardButton(
                text='👮Выдать админа',
                callback_data=admin_call.new(action='set_admin', arg=user.id_)))
        elif is_admin == 'Администратор':
            actions.insert(types.InlineKeyboardButton(
                text='👮Снять админа',
                callback_data=admin_call.new(action='set_admin', arg=user.id_)))

    actions.insert(
        types.InlineKeyboardButton(
            text='⬅Назад',
            callback_data=admin_call.new(action='show_users', arg=show_users_arg)
        )
    )
    await call.answer()
    await call.message.edit_text(f'📍<b>Админ панель</b>\n'
                                 f'✏<i>Пользователь:</i> <a tg://user?id={user.id_}>{quote_html(user.name)}</a>\n'
                                 f'🆔Айди: <code>{user.id_}</code>\n'
                                 f'🏷Юзернейм: {username}\n'
                                 f'⚙Права: {is_admin}\n'
                                 f'🔑Доступ: {is_access}\n\n'
                                 f'💳Подписка: {sub}{sub_time}\n\n'
                                 f'🔔Поиск выгодных предложений: {power}\n\n'
                                 f'🔖Запись в базе:\n'
                                 f'🔎{create_at}\n'
                                 f'🔎{updated_at}\n',
                                 reply_markup=actions)


@dp.callback_query_handler(Admin(), admin_call.filter(action='main_sub'), chat_type='private')
async def to_show_sub(call: types.CallbackQuery, callback_data: dict):
    user_id = int(callback_data.get('arg'))
    user = await db.get_user(user_id)

    sub = 'Не было'
    sub_time = ''
    if user.time_access:
        if db.check_access(user) is False:
            sub = f'Закончилась\n'
            sub_time = f'🕐До: {user.time_access.strftime("%Y-%m-%d %X")}\n' \
                       f'⏳Закончилась {humanize.naturaltime(user.time_access)}'
        elif db.check_access(user) is True:
            sub = f'Активна\n'
            sub_time = f'🕐До: {user.time_access.strftime("%Y-%m-%d %X")}\n' \
                       f'⏳Закончится {humanize.naturaltime(user.time_access)}'

    actions = types.InlineKeyboardMarkup(row_width=2)
    if db.check_access(user) in (False, None):
        actions.insert(types.InlineKeyboardButton(
            text='🔸Выдать подписку',
            callback_data=admin_call.new(action='give_sub', arg=user.id_)
        ))
    else:
        actions.insert(types.InlineKeyboardButton(
            text='🔸Забрать подписку',
            callback_data=admin_call.new(action='pick_up_sub', arg=user.id_)
        ))
    actions.insert(types.InlineKeyboardButton(
        text='⬅Назад',
        callback_data=show_user.new(id_=user.id_, action='show', arg='show')
    ))
    await call.answer()
    await call.message.edit_text(f'📍<b>Админ панель</b>\n'
                                 f'✏<i>Пользователь:</i> {user.name}\n'
                                 f'💳Подписка: {sub} {sub_time}\n'
                                 f'✏Выберите действие.', reply_markup=actions)


@dp.callback_query_handler(Admin(), admin_call.filter(action='pick_up_sub'), chat_type='private')
async def to_pick_up_sub(call: types.CallbackQuery, callback_data: dict):
    user_id = int(callback_data.get('arg'))

    await db.set_sub_user(user_id, None)
    await db.update_chat_power(user_id, False)

    await call.answer(f'💡Вы успешно забрали подписку у пользователя', cache_time=3)
    await to_show_sub(call, {'arg': user_id})

    logger.info(f'👮Администратор {call.from_user.full_name} забрал подписку пользователя id-{user_id}')

    await dp.bot.send_message(chat_id=user_id, text=f'👮Администратор забрал у вас подписку.',
                              reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(Admin(), admin_call.filter(action='give_sub'), chat_type='private')
async def to_show_time_give_sub(call: types.CallbackQuery, callback_data: dict):
    user = int(callback_data.get('arg'))
    user = await db.get_user(user)

    msg_text = call.message.html_text.split('\n')
    msg_text.pop()
    msg_text = '\n'.join(msg_text)

    await call.message.edit_text(f'{msg_text}\n'
                                 f'⏳На какое время выдать подписку?\n',
                                 reply_markup=get_time(user.id_))


@dp.callback_query_handler(Admin(), give_sub.filter(), chat_type='private')
async def to_give_sub(call: types.CallbackQuery, callback_data: dict):
    user_id = int(callback_data.get('id_'))
    time = int(callback_data.get('time_index'))
    time = list(times().values())[time]

    await db.set_sub_user(user_id, time)

    await call.answer(f'💡Вы успешно выдали подписку пользователю!', cache_time=3)
    await to_show_sub(call, {'arg': user_id})

    logger.info(f'👮Администратор {call.from_user.full_name} выдал подписку до {time} пользователю id-{user_id}')

    await dp.bot.send_message(chat_id=user_id, text=f'👮Администратор выдал вам подписку до {time.strftime("%Y-%m-%d %X")}!',
                              reply_markup=main_keyboard(True))


@dp.callback_query_handler(Admin(), admin_call.filter(action='set_access'), chat_type='private')
async def to_set_access_ban(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = int(callback_data.get('arg'))
    user = await db.get_user(user_id)

    await db.delete_user(user)

    await call.answer(f'Пользователь успешно удалён!')
    await to_show_users(call, callback_data={'arg': '0-20'}, state=state)

    logger.info(f'👮Администратор {call.from_user.full_name} удалил пользователя {user.name} ({user_id})')


@dp.callback_query_handler(Admin(), admin_call.filter(action='set_admin'), chat_type='private')
async def to_give_admin(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = int(callback_data.get('arg'))
    user = await db.get_user(user_id)

    if user.is_admin is True:
        await db.delete_admin(user_id)
        await call.answer('Вы забрали у пользователя права Администратора.')
        z = 'забрал у вас'
    else:
        await db.set_admin(user_id)
        await call.answer('Вы выдали пользователю права Администратора.')
        z = 'выдал вам'
    await to_show_user(call, {'id_': user_id}, state)

    logger.info(f'👮Администратор {call.from_user.full_name} {z.split(" ")[0]} права Администратора пользователю {user.name}({user_id})')

    await dp.bot.send_message(chat_id=user_id,
                              text=f'👮Администратор {z} права Администратора.',
                              reply_markup=main_keyboard(user.power, True))

@dp.callback_query_handler(Admin(), admin_call.filter(action='ignore_user'), chat_type='private')
async def to_ignore_user(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        user_id = int(callback_data.get('arg'))
    except ValueError:
        user_id = int(callback_data.get('arg')[:-1])

    await db.set_ignore(user_id)
    await call.answer(f'❌Пользователь теперь игнорируется!')
    logger.info(f'👮Администратор {call.from_user.full_name} выдал статус игнорирования пользователю id-{user_id}')
    if callback_data.get('arg')[-1:] == '-':
        msg_text = call.message.html_text.split('\n')
        msg_text.pop()
        msg_text = '\n'.join(msg_text)

        await call.message.edit_text(f'{msg_text}\n'
                                     f'❌Пользователь теперь игнорируется.')
    else:
        data = await state.get_data()
        if 'show_users_arg' in data:
            await to_show_users(call, {'arg': data['show_users_arg']}, state)
        else:
            await to_show_users(call, {'arg': '0-20'}, state)
