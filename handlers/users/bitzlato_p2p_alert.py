from aiogram.utils import exceptions
import concurrent.futures
import aiohttp
from loguru import logger
from utils.cfg_parser import Cfg
import utils.db_api.commands as db
from utils.db_api.models import OffersBinance, OffersBitzlato
from keyboards.inline.p2p import buy_keyboard, buy_keyboard_binance
from aiogram.utils.markdown import quote_html
from aiogram import types
from loader import dp
import asyncio
from statistics import median
import datetime
from loguru import logger as logging
import requests


def s(integer: [int, float]):
    return f'{integer:,}'.replace('.', ',').replace(',', '.', 2)

async def consider():
    """Поиск цен для бирж по параметрам занимает ~7.5 секунд"""
    # Получаем среднюю цену текущих предложений на Bitzlato (~7 секунд)
    skip, list_price = 0, []
    last_date = datetime.datetime.now()

    logging.info('Начинаю поиск средней/медианной цены всех предложений на Bitzlato')

    params = {
        # "type": "purchase",  # enum: selling <> purchase, default "purchase"
        "currency": "RUB",
        "limit": 20,
        "skip": skip,
        # "cryptocurrency": "BTC",  # default "BTC"
        # "lang": "ru"  # default "en"
    }
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get('https://bitzlato.com/api/p2p/public/exchange/dsa/', params=params) as response:
                try:
                    data = await response.json()  # Получаем данные: количество предложений и предложения)
                except Exception as err:
                    logger.info(err)

            for e in data['data']:
                list_price.append(int(e['rate']))

            # Как только предложения закончились, функция отдаёт среднюю цену всех предложений
            if not data['data']:
                # Находим сумму всех чисел в списке
                count_all = sum(e for e in list_price)

                # Высчитываем среднюю цену
                price = int(count_all / int(data['total']))
                Cfg.Bitzlato.set_average_price(price)  # Сохраняем её

                # Высчитываем медианную цену
                median_price = int(median(list_price))
                Cfg.Bitzlato.set_median_price(median_price)  # Сохраняем её

                it_time = datetime.datetime.now() - last_date
                logging.info(f'Средняя цена: {s(price)}₽ всех предложений на Bitzlato за {it_time}')
                logging.info(f'Медианная цена: {s(median_price)}₽')
                break

            skip += 20
            params.update({'skip': skip})

        logging.info('Поиск медианной/официальной/средней цены всех предложений на Binance')

        symbol = 'BTCRUB'

        async def first_the():  # Есть подозрение что данные поступаю с другого источника, не с того от кого ожидается
            async with session.get('https://api.binance.com/api/v3/trades', params={"symbol": symbol, "limit": 1000}) as response:
                try:
                    data = await response.json()  # Получаем данные: 1000 предложений
                except Exception as err:
                    logger.info(err)

            data = sorted(data, key=lambda x: x['price'])
            median_price = int((float(data[498]['price']) + float(data[499]['price'])) / 2)

            Cfg.Binance.set_median_price(median_price)
            logging.info(f'Медианная цена: {s(median_price)}₽ на Binance')

        async def second_the():  # Есть подозрение что данные поступаю с другого источника, не с того от кого ожидается
            async with session.get('https://api.binance.com/api/v3/ticker/price', params={"symbol": symbol}) as response:
                try:
                    data = await response.json()  # Получаем данные: официальную цену
                except Exception as err:
                    logger.info(err)

            official_price = int(float(data['price']))
            Cfg.Binance.set_official_price(official_price)

            logging.info(f'Официальная цена: {s(official_price)}₽ на Binance')

        async def third_the():  # Есть подозрение что данные поступаю с другого источника, не с того от кого ожидается
            async with session.get('https://api.binance.com/api/v3/avgPrice', params={"symbol": symbol}) as response:
                try:
                    data = await response.json()  # Получаем данные: среднюю цену
                except Exception as err:
                    logger.info(err)

            avg_price = int(float(data['price']))
            Cfg.Binance.set_average_price(avg_price)

            logging.info(f'Средняя цена: {s(avg_price)}₽ на Binance')

        await asyncio.gather(first_the(), second_the(), third_the())

# async def search_binance_not_work_WTF():
#     """Я не понимаю почему эта штука не работает, за то на реквестах работает..."""
#     headers = {
#         "Accept": "*/*",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
#         "Cache-Control": "no-cache",
#         "Connection": "keep-alive",
#         "Content-Length": "123",
#         "content-type": "application/json",
#         "Host": "p2p.binance.com",
#         "Origin": "https://p2p.binance.com",
#         "Pragma": "no-cache",
#         "TE": "Trailers",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
#     }
#     payload = {"page": 1, "rows": 10, "payTypes": [], "asset": "BTC", "tradeType": "BUY", "fiat": "RUB", "publisherType": 'null'}
#     async with aiohttp.ClientSession(headers=headers).post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', json=payload) as response:
#         # aiohttp.client_exceptions.ClientOSError: [WinError 64] Указанное сетевое имя более недоступно
#         # base_events.py [LINE:1707] #ERROR    [2021-06-24 13:29:38,651]  Unclosed client session
#         # client_session: <aiohttp.client.ClientSession object at 0x08850988>
#         print(await response.json())
#
#         # async with session.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', json=payload) as response:
#         #     print(await response.json())
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(gogog())
# asyncio.run(gogog())
# asyncio.run(gogog())
# loop.run_until_complete(consider())
# import requests
#
# headers = {
#     "Accept": "*/*",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
#     "Cache-Control": "no-cache",
#     "Connection": "keep-alive",
#     "Content-Length": "123",
#     "content-type": "application/json",
#     "Host": "p2p.binance.com",
#     "Origin": "https://p2p.binance.com",
#     "Pragma": "no-cache",
#     "TE": "Trailers",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
# }
#
# data = {"page":1,"rows":10,"payTypes":[],"asset":"BTC","tradeType":"BUY","fiat":"RUB","publisherType":None}
#
# r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data)
# print(r.text)

async def check_user_valid(chat):
    if chat.is_access is False:
        await db.update_chat_power(chat.id_, False)
        try:
            text = '😕Вы были заблокированы, поэтому для вас поиск выключен.'
            await dp.bot.send_message(chat_id=chat.id_, text=text,
                                      reply_markup=types.ReplyKeyboardRemove())
        except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
            pass
        return False
    if db.check_access(chat) is False:
        await db.update_chat_power(chat.id_, False)
        try:
            text = '😕У вас закончилась подписка, поэтому я отключаю поиск для вас.'
            await dp.bot.send_message(chat_id=chat.id_, text=text,
                                      reply_markup=types.ReplyKeyboardRemove())
        except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
            pass
        return False


async def search_bitzlato_V2():
    # prices_ = {
    #     1: Cfg.Bitzlato.get_average_price(),  # Средняя цена с Bitzlato
    #     2: Cfg.Bitzlato.get_median_price(),  # Медианная цена с Bitzlato
    #     3: None,  # Минимальная цена c Binance
    #     4: Cfg.Binance.get_average_price(),  # Средняя цена c Binance
    #     5: Cfg.Binance.get_median_price(),  # Медианная цена c Binance
    #     6: Cfg.Binance.get_official_price(),  # По курсу цена с Binance
    #     7: None,  # Значение от пользователя будет
    # }
    prices = {
        1: None,  # Минимальная цена c Bitzlato
        2: None,  # Минимальная цена c Binance
        3: Cfg.Bitzlato.get_average_price(),  # Средняя цена с Bitzlato
        4: Cfg.Binance.get_average_price(),  # Средняя цена c Binance
        5: Cfg.Bitzlato.get_median_price(),  # Медианная цена с Bitzlato
        6: Cfg.Binance.get_median_price(),  # Медианная цена c Binance
        7: None,  # Значение от пользователя
        8: Cfg.Binance.get_official_price(),  # По курсу цена с Binance
    }

    offer_1, skip, debug = True, 0, False
    params = {
        # "type": "purchase",  # selling <> purchase
        "currency": "RUB",
        "limit": 20,
        "skip": skip,
        # "lang": "ru"
    }
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get('https://bitzlato.com/api/p2p/public/exchange/dsa/', params=params) as response:
                try:
                    data = await response.json()  # Получаем данные: количество предложений и предложения
                except:
                    logging.info(response.text)
                    raise

            try:
                data = data['data']
            except ValueError:
                logger.warning(f"None data - {data}")

            for offer in data:
                offer['rate'] = int(offer['rate'])
                offer_ = await db.get_offer(offer['id'])
                use_count = 0
                for chat in await db.get_chats_alert(2, False):
                    if await check_user_valid(chat) is False:
                        continue
                    loss = None
                    if chat.type_search == 7:  # Значение от пользователя
                        price_ = chat.count
                    elif chat.type_search == 1:  # Предыдущее минимальное
                        if offer_1 is False:
                            continue
                        elif skip == 0 and offer_1 is True:
                            price_ = (float(data[1]['rate']) / 100) * (100 - chat.count)
                            loss = str(100 - (float(offer['rate']) / float(data[data.index(offer)+1]['rate'])) * 100)[:5]
                    else:
                        # Что бы было легче, вычитаем из средней/медианной/официальной цены эти проценты
                        price_ = prices[chat.type_search] - (prices[chat.type_search] * (chat.count / 100))

                    if offer['rate'] <= price_:
                        use_count += 1
                        # Проверка, есть ли в бд это предложение
                        if offer_:
                            # Если есть и цена у него так же, то пропускаем
                            if offer_.price == offer['rate']:
                                continue
                            # Если цена не та же самая была, то обновляем цену предложения в бд
                            await db.update_offer(offer['id'], offer['rate'])
                        else:
                            await db.add_offer(OffersBitzlato(offer['id'], offer['rate']))
                    else:
                        continue

                    owner = offer["owner"]
                    rate = offer["rate"]
                    currency = '₽'  # offer["currency"]
                    pay_method = offer["paymethod"]["name"]
                    limits = f'{offer["limitCurrency"]["min"]} - {offer["limitCurrency"]["max"]}'

                    text = f'<b>🔔Выгодное предложение с Bitzlato!</b>\n' \
                           f'👤Продавец <i>{quote_html(owner)}</i>\n' \
                           f'💰Цена: <code>{s(rate)}</code>{currency} ({pay_method})\n' \
                           f'⚖Лимиты: <code>{limits}</code>\n'

                    if loss is not None:
                        text += f'⚙Меньше пред. мин на {loss}%'

                    if debug is True:
                        text += f'<code>debug: {chat.type_search} {prices[chat.type_search]}\n' \
                                f'price_({price_}), chat.count({chat.count})\n' \
                                f'offer_({offer_})' \
                                f'</code>'

                    await db.log(chat.id_, offer['id'], rate, limits, chat.type_search, loss, chat.count, chat.name)

                    # Отправляем сообщение о выгодном предложении
                    try:
                        await dp.bot.send_message(chat_id=chat.id_, text=text, reply_markup=buy_keyboard(offer["id"]))
                    except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
                        logger.info(
                            f'Бот не смог отправить выгодное предложение - {chat.name}, отключаю поиск для него.')
                        await db.update_chat_power(chat.id_, False)
                    except exceptions.RetryAfter as err:
                        logger.warning(
                            f'RetryAfter! Не смогу отправлять сообщения {chat.name}({chat.id_}) {err.timeout} секунд.')
                        await asyncio.sleep(err.timeout)
                        await dp.bot.send_message(chat_id=chat.id_, text=text, reply_markup=buy_keyboard(offer["id"]))
                    finally:
                        await asyncio.sleep(1 / 10)
                else:
                    offer_1 = False
            # Как только предложения закончились, мы заканчиваем поиск
            if not data:
                return
            if use_count == 0:
                return

            skip += 20
            params.update({'skip': skip})

async def get_offers_binance():
    loop = asyncio.get_running_loop()

    def main():
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "123",
            "content-type": "application/json",
            "Host": "p2p.binance.com",
            "Origin": "https://p2p.binance.com",
            "Pragma": "no-cache",
            "TE": "Trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
        }

        data = {"page": 1, "rows": 10, "payTypes": [], "asset": "BTC",
                "tradeType": "BUY", "fiat": "RUB", "publisherType": None}

        r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data)
        data = r.json()
        if data['code'] == '000000':
            return data
        else:
            raise_text = f'После получения данных вернулся код {data["code"]}, ожидалось "000000": {data}'
            raise raise_text

    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, main
        )
    return result

async def search_binance():
    data = (await get_offers_binance())['data']

    debug = False

    def tradeMethods_filter(_trade_methods: dict):
        return _trade_methods["payType"]

    offer_id = str(data[0]['adv']['advNo'])
    offer_price = float(data[0]['adv']['price'])
    offer_price_next = float(data[1]['adv']['price'])

    offer_ = await db.get_offer_binance(offer_id)
    for chat in await db.get_chats_alert(2, True):
        if await check_user_valid(chat) is False:
            continue
        price_ = (offer_price_next / 100) * (100 - chat.count)
        loss = str(100 - (offer_price / offer_price_next) * 100)[:5]
        if offer_price <= price_:
            # Проверка, есть ли в бд это предложение
            if offer_:
                # Если есть и цена у него так же, то пропускаем
                if offer_.price == offer_price:
                    continue
                # Если цена не та же самая была, то обновляем цену предложения в бд
                await db.update_offer_binance(offer_id, offer_price)
            else:
                await db.add_offer(OffersBinance(offer_id, offer_price))
        else:
            continue

        nickname = data[0]["advertiser"]["nickName"]
        currency = '₽'  # data[0]["adv"]["fiatSymbol"]
        trade_methods = ", ".join(list(map(tradeMethods_filter, data[0]["adv"]["tradeMethods"])))

        limits = f'{int(float(data[0]["adv"]["minSingleTransAmount"]))} - {int(float(data[0]["adv"]["maxSingleTransAmount"]))}'

        text = f'<b>🔔Выгодное предложение с Binance!</b>\n' \
               f'👤Продавец <i>{quote_html(nickname)}</i>\n' \
               f'💰Цена: <code>{s(offer_price)}</code>{currency} ({trade_methods})\n' \
               f'⚖Лимиты: <code>{limits}</code>\n' \
               f'⚙Меньше пред. мин на {loss}%'

        if debug is True:
            text += f'<code>debug: {chat.type_search} {offer_price_next}\n' \
                    f'price_({price_}), chat.count({chat.count})\n' \
                    f'offer_({offer_})' \
                    f'</code>'

        await db.log_binance(chat.id_, offer_id, offer_price, limits, chat.type_search, loss, chat.count, chat.name)

        # Отправляем сообщение о выгодном предложении
        try:
            await dp.bot.send_message(chat_id=chat.id_, text=text, reply_markup=buy_keyboard_binance())
        except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
            logger.info(
                f'Бот не смог отправить выгодное предложение - {chat.name}, отключаю поиск для него.')
            await db.update_chat_power(chat.id_, False)
        except exceptions.RetryAfter as err:
            logger.warning(
                f'RetryAfter! Не смогу отправлять сообщения {chat.name}({chat.id_}) {err.timeout} секунд.')
            await asyncio.sleep(err.timeout)
            await dp.bot.send_message(chat_id=chat.id_, text=text, reply_markup=buy_keyboard_binance())
        finally:
            await asyncio.sleep(1 / 10)


async def start_search():
    await asyncio.gather(search_bitzlato_V2(), search_binance())


async def search_count_methods():
    await consider()
