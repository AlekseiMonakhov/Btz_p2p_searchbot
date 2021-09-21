from utils.google_sheets.api import update
from keyboards.inline.chat import methods_
from loguru import logger
from utils.db_api.commands import get_all_logs_bitzlato, get_all_logs_binance
import asyncio
import concurrent.futures
from datetime import datetime

def statistics(logs_bitzlato, logs_binance):
    logger.info('Начинается выгрузка данных в таблицу Google Sheets')

    titles = [['Дата/Время (МСК)', 'Offer id', 'Цена ₽', 'Лимиты', '%/Кол.во', 'Пред. мин %', 'Метод поиска', 'Ник', 'Юзер id']]

    def log_filter(log):
        return [log.time.strftime("%Y-%m-%d %X"), log.offer_id, f'{log.price:,}'.replace(',', '.'), log.limit,
                log.count, log.loss if log.loss is not None else '', methods_[log.type_search][1:], log.user_name, log.user_id]

    logs = sorted(list(map(log_filter, logs_binance)) + list(map(log_filter, logs_bitzlato)),
                  key=lambda d: datetime.strptime(d[0], "%Y-%m-%d %X"), reverse=True)

    logger.info('Данные отправлены в таблицу Google Sheets')
    update('A1', titles + logs, 0)
    logger.info('Данные выгружены в таблицу Google Sheets')

async def statistics_gs():
    loop = asyncio.get_running_loop()
    logs_bitzlato = await get_all_logs_bitzlato()
    logs_binance = await get_all_logs_binance()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(
            pool, statistics, logs_bitzlato, logs_binance
        )
