# import humanize
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from utils.db_api.commands import get_user, check_access
from loader import cache


class PaidUser(BoundFilter):
    """
    Проверка на юзера у которого
    куплена или не куплена подписка.
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

        user_access = check_access(user)
        if user_access is None:
            return False
        elif user_access is False:
            pass
            # await call.message.answer('😕Извините, но я не могу ничем вам помочь.\n'
            #                          f'⌛Ваша подписка истекла {humanize.naturaltime(user.time_access)}',
            #                          reply_markup=types.ReplyKeyboardRemove())
        return user_access
