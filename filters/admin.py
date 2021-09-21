from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from utils.db_api.commands import get_user
from loader import cache


class Admin(BoundFilter):
    """
    Проверка на Администратора.
    Message и CallbackQuery
    """

    async def check(self, obj: types.Update):
        if isinstance(obj, types.Message):
            user_id = obj.from_user.id
        elif isinstance(obj, types.CallbackQuery):
            user_id = obj.from_user.id
        else:
            return False

        if user := cache.get(user_id):
            pass
        else:
            user = await get_user(user_id)
            cache[user_id] = user

        try:
            return user.is_admin
        except AttributeError:
            return False
