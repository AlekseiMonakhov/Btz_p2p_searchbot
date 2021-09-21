from aiogram import executor
from loguru import logger

from loader import dp, scheduler
import middlewares, filters, handlers
from utils.db_api.db import engine
from utils.db_api.models import Base
# from utils.notify_admins import on_startup_notify
from handlers.users.bitzlato_p2p_alert import search_count_methods, start_search
from utils.google_sheets.statistics import statistics_gs


def scheduler_jobs():
    scheduler.add_job(start_search, "interval", seconds=3)
    scheduler.add_job(search_count_methods, "interval", seconds=20)
    scheduler.add_job(statistics_gs, "interval", seconds=60)

async def on_startup(dispatcher):
    logger.info('Подключение к базе данных')
    async with engine.begin() as conn:
        # Создаем таблицы если их нету
        await conn.run_sync(Base.metadata.create_all)

    logger.info('Сразу запускаем поиск значений для методов')
    await search_count_methods()
    logger.info('Планирование задач')
    scheduler_jobs()

    # Уведомляет про запуск
    # await on_startup_notify(dispatcher)


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
