from sqlalchemy.future import select
from sqlalchemy import update, func, desc
from utils.db_api.db import async_session
from utils.db_api.models import Users, OffersBitzlato, OffersBinance, StatsOffers, StatsOffersBinance
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import operator


async def get_user(id_: int):
    async with async_session() as session:
        result = await session.execute(select(Users).where(Users.id_ == id_))
        result = result.scalars()
        return result.first()

async def get_users(skip: int, limit: int):
    async with async_session() as session:
        results = await session.execute(select(Users).where(Users.is_ignore == False).order_by(Users.create_at).offset(skip).limit(limit))
        return results.scalars()

async def get_admins_id():
    async with async_session() as session:
        results = await session.execute(select(Users.id_).where(Users.is_admin == True).order_by(Users.create_at))
        return results.scalars()

async def get_count_users():
    async with async_session() as session:
        result = await session.execute(select(func.count(Users.id_)))
        return result.scalar()

async def add_user(id_: int, name: str, username: str):
    user = Users(id_, name, username)
    async with async_session() as session:
        async with session.begin():
            session.add(user)

async def set_ignore(id_: int):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(is_ignore=True, is_access=False, time_access=None, is_admin=False, power=False).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def set_access(id_: int, is_access):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(is_access=is_access).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def set_time_access(id_: int, time_access):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(time_access=time_access).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def set_sub_user(id_: int, time_access):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(is_access=True, time_access=time_access, is_ignore=False).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def update_user(user: Users):
    async with async_session() as session:
        await session.add(user)
        await session.commit()

async def delete_user(user: Users):
    async with async_session() as session:
        async with session.begin():
            await session.delete(user)
            await session.commit()

async def set_admin(id_: int):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(is_admin=True, is_access=True, time_access=datetime(3000, 1, 1)).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def delete_admin(id_: int):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(is_admin=False, time_access=None).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

def g(inp, relate, cut):
    ops = {True: operator.eq,
           False: operator.ne}
    return ops[relate](inp, cut)

async def get_chats_alert(method_only: int = None, only_or_kick: bool = None, power=True):
    async with async_session() as session:
        if not power:
            if method_only:
                return (await session.execute(select(Users).where(g(Users.type_search, only_or_kick, method_only)))).scalars()
            return (await session.execute(select(Users))).scalars()
        else:
            if method_only:
                return (await session.execute(select(Users).where(g(Users.type_search, only_or_kick, method_only), Users.power == power))).scalars()
            return (await session.execute(select(Users).where(Users.power == power))).scalars()

async def get_chat_alert(id_: int):
    async with async_session() as session:
        result = await session.execute(select(Users).where(Users.id_ == id_))
        result = result.scalars()
        return result.first()

async def update_chat(id_: int, type_search: int, count: float, power: int):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(type_search=type_search, count=count, power=power).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def update_chat_power(id_: int, power: bool):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(power=power).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def update_chat_type_search(id_: int, type_search: int):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(type_search=type_search).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()

async def update_chat_count(id_: int, count: float):
    async with async_session() as session:
        stmt = update(Users).where(Users.id_ == id_).values(count=count).returning(Users.id_)
        await session.execute(stmt)
        await session.commit()


async def get_offer(id_: int):
    async with async_session() as session:
        result = await session.execute(select(OffersBitzlato).where(OffersBitzlato.id_ == id_))
        result = result.scalars()
        return result.first()

async def get_offer_binance(id_: str):
    async with async_session() as session:
        result = await session.execute(select(OffersBinance).where(OffersBinance.id_ == id_))
        result = result.scalars()
        return result.first()

async def add_offer(offer: [OffersBinance, OffersBinance]):
    async with async_session() as session:
        try:
            async with session.begin():
                session.add(offer)
        except IntegrityError:
            await session.rollback()

async def update_offer(id_: int, price: int):
    async with async_session() as session:
        stmt = update(OffersBitzlato).where(OffersBitzlato.id_ == id_).values(price=price).returning(OffersBitzlato.id_)
        await session.execute(stmt)
        await session.commit()

async def update_offer_binance(id_: str, price: float):
    async with async_session() as session:
        stmt = update(OffersBinance).where(OffersBinance.id_ == id_).values(price=price).returning(OffersBinance.id_)
        await session.execute(stmt)
        await session.commit()


async def log(user_id: int, offer_id: int, price: int, limit: str, type_search: int, loss: str, count: int, user_name: str):
    stat = StatsOffers(user_id, offer_id, price, limit, type_search, loss, count, user_name)
    async with async_session() as session:
        async with session.begin():
            session.add(stat)

async def log_binance(user_id: int, offer_id: str, price: float, limit: str, type_search: int, loss: str, count: int, user_name: str):
    stat = StatsOffersBinance(user_id, offer_id, price, limit, type_search, loss, count, user_name)
    async with async_session() as session:
        async with session.begin():
            session.add(stat)

async def get_logs(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(StatsOffers).where(StatsOffers.user_id == user_id,
                                        StatsOffers.time > datetime.now() - timedelta(hours=24))
                                       .order_by(desc(StatsOffers.time)))
        result = result.scalars()
        return result
    
async def get_logs_binance(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(StatsOffersBinance).where(StatsOffersBinance.user_id == user_id,
                                        StatsOffersBinance.time > datetime.now() - timedelta(hours=24))
                                       .order_by(desc(StatsOffersBinance.time)))
        result = result.scalars()
        return result

async def get_all_logs_bitzlato():
    async with async_session() as session:
        result = await session.execute(select(StatsOffers).order_by(desc(StatsOffers.time)))
        result = result.scalars()
        return result

async def get_all_logs_binance():
    async with async_session() as session:
        result = await session.execute(select(StatsOffersBinance).order_by(desc(StatsOffersBinance.time)))
        result = result.scalars()
        return result

def check_access(user: Users):
    try:
        if user.time_access >= datetime.now():
            if user.is_access is True:
                return True
            else:
                return None
        return False
    except (AttributeError, TypeError):
        return None
