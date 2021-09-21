from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default import main_keyboard
import utils.db_api.commands as db
from keyboards.inline.chat import request_sub
from aiogram.types import ChatType
from aiogram import types
from loguru import logger
import humanize

from data.config import ADMINS
from loader import dp

humanize.i18n.activate("ru_RU")


@dp.message_handler(CommandStart(), chat_type=ChatType.PRIVATE)
async def bot_start(msg: types.Message, user_db):
    if not user_db:
        await db.add_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username)
        if str(msg.from_user.id) in ADMINS:
            await db.set_admin(msg.from_user.id)

            await msg.answer(f'🙂Здравствуйте, новый владелец {msg.from_user.get_mention()}!\n'
                             f'🌟У вас есть доступ к админ панели, а так же можете выдавать права Администратора и забирать их.',
                             reply_markup=main_keyboard(user_db.power, True))
            return

        for admin in await db.get_admins_id():
            await dp.bot.send_message(text=f'❓Новый неизвестный пользователь: {msg.from_user.get_mention()}\n'
                                           f'💡Вы можете выдать ему подписку.',
                                      chat_id=admin, reply_markup=request_sub(msg.from_user.id))
        logger.info(f'Новый неизвестный пользователь: {msg.from_user.full_name}({msg.from_user.id})')
        return
    if str(msg.from_user.id) in ADMINS:
        await msg.answer(f'🙂Здравствуйте, владелец {msg.from_user.get_mention()}!\n'
                         f'🌟У вас есть доступ к админ панели, а так же можете выдавать права Администратора и забирать их.',
                         reply_markup=main_keyboard(user_db.power, True))
        return
    elif user_db.is_admin is True:
        await msg.answer(f'🙂Здравствуйте, администратор {msg.from_user.get_mention()}!\n'
                         f'🌟У вас есть доступ к админ панели.', reply_markup=main_keyboard(user_db.power, True))
        return
    if db.check_access(user_db) is True:
        await msg.answer('😎Привет! Я помогу найти тебе выгодные предложения на Bitzlato!\n'
                         f'⏳Ваша подписка закончится {humanize.naturaltime(user_db.time_access)}',
                         reply_markup=main_keyboard(user_db.power, user_db.is_admin))
    elif db.check_access(user_db) is False:
        await msg.answer('😎Привет! Я помогу найти тебе выгодные предложения на Bitzlato!\n'
                         f'⌛Ваша подписка закончилась {humanize.naturaltime(user_db.time_access)}',
                         reply_markup=types.ReplyKeyboardRemove())
