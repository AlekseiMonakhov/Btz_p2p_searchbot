import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
import utils.db_api.commands as db
from data.config import ADMINS
import humanize


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_pre_process_callback_query(self, call: types.CallbackQuery, data: dict):
        user = await db.get_user(call.from_user.id)
        data['user_db'] = user

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        user = await db.get_user(message.from_user.id)
        data['user_db'] = user

        try:
            if user.name != message.from_user.full_name:
                user.name = message.from_user.full_name
                await db.update_user(user)
            if user.username != message.from_user.username:
                user.name = message.from_user.username
                await db.update_user(user)

            # От владельцев сообщения не проверяются на блокировку/срок подписки
            if str(message.from_user.id) in ADMINS:
                return

            if user.is_access is False:
                raise CancelHandler()

            check = db.check_access(user)
            if check is None and user is not None:
                raise CancelHandler()
            elif check is False:
                await message.answer('😕Извините, но я не могу ничем вам помочь.\n'
                                     f'⌛Ваша подписка истекла {humanize.naturaltime(user.time_access)}',
                                     reply_markup=types.ReplyKeyboardRemove())
                raise CancelHandler()
        except AttributeError:
            if 'start' != key:
                raise CancelHandler()

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        if throttled.exceeded_count <= 2:
            await message.reply("❌Не так быстро!")
