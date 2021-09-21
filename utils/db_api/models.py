import sqlalchemy as sa
import sqlalchemy.ext.declarative


Base: sa.ext.declarative.DeclarativeMeta = sa.ext.declarative.declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id_ = sa.Column(sa.BigInteger, primary_key=True)  # Айди юзера
    name = sa.Column(sa.Text, nullable=True)  # Полное имя юзера
    username = sa.Column(sa.Text, default=None)  # Юзернейм
    is_ignore = sa.Column(sa.Boolean, default=True, nullable=True)  # Игнорировать ли юзера
    is_admin = sa.Column(sa.Boolean, default=False, nullable=True)  # Админ или нет
    is_access = sa.Column(sa.Boolean, default=False, nullable=True)  # Доступ к боту
    time_access = sa.Column(sa.DateTime, default=None)  # Дата до какого будет действовать подписка
    power = sa.Column(sa.Boolean, default=False, nullable=True)  # Включен или выключен поиск
    type_search = sa.Column(sa.Integer, default=None)  # Тип поиска предложений (по средней/медианной/минимальной цене Bitzlato, своё значение, курсу/средней/медианной цены Binance)
    count = sa.Column(sa.Float, default=None)  # Значение/Процент для поиска предложений
    create_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(),
        default=sa.func.now(),
        onupdate=sa.func.now(),
        server_default=sa.func.now()
    )

    def __init__(self, id_: int, name: str, username: str = None):
        self.id_ = id_
        self.name = name
        self.username = username

    def __repr__(self):
        return f"id_({self.id_}), name({self.name}), username({self.username}), " \
               f"is_admin({self.is_admin}), is_access({self.is_access}), time_access({self.time_access}), " \
               f"power({self.power}), type_search({self.type_search}), count({self.count}), " \
               f"create_at({self.create_at}), updated_at({self.updated_at}),"

# Возможно когда нибудь в будущем перепишу под каналы и чаты, а эта таблица подойдёт вполне. Но потом
# class ChatsAlert(Base):
#     __tablename__ = 'chats_alert'
#
#     id_ = sa.Column(sa.BigInteger, primary_key=True)  # Айди юзера/чата/канала ^ предполагается что в будущем предложения будут приходить не только в лс
#     chat_title = sa.Column(sa.Text, nullable=True)  # Название чата
#     chat_type = sa.Column(sa.Text, nullable=True)  # Тип чата (лс, чат, канал) ^
#     hunter_id = sa.Column(sa.BigInteger, nullable=True)  # Айди юзера кого кто привязал чат к уведомлениям ^
#     power = sa.Column(sa.Boolean, default=False, nullable=True)  # Включен или выключен поиск
#     type_search = sa.Column(sa.Integer, default=None)  # Тип поиска предложений (по средней/медианной/минимальной цене Bitzlato, своё значение, курсу/средней/медианной цены Binance)
#     count = sa.Column(sa.BigInteger, default=None)  # Значение/Процент для поиска предложений
#     create_at = sa.Column(sa.DateTime, server_default=sa.func.now())
#     updated_at = sa.Column(
#         sa.DateTime(),
#         default=sa.func.now(),
#         onupdate=sa.func.now(),
#         server_default=sa.func.now()
#     )
#
#     def __init__(self, id_: int, chat_title: str, chat_type: str,
#                  hunter_id: int, type_search: int, count: int, power: int):
#         self.id_ = id_
#         self.chat_title = chat_title
#         self.chat_type = chat_type
#         self.hunter_id = hunter_id
#         self.type_search = type_search
#         self.count = count
#         self.power = power

class OffersBitzlato(Base):
    __tablename__ = 'offers_bitzlato'

    id_ = sa.Column(sa.BigInteger, primary_key=True)  # Айди предложения
    price = sa.Column(sa.BigInteger, nullable=True)  # Цена предложения
    create_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(),
        default=sa.func.now(),
        onupdate=sa.func.now(),
        server_default=sa.func.now()
    )

    def __init__(self, id_: int, price: int):
        self.id_ = id_
        self.price = price

    def __repr__(self):
        return f"id_({self.id_}), price({self.price}), " \
               f"create_at({self.create_at}), updated_at({self.updated_at})"


class StatsOffers(Base):
    __tablename__ = 'stats_caught_offers'

    i = sa.Column(sa.BigInteger, autoincrement=True, primary_key=True)
    time = sa.Column(sa.DateTime, server_default=sa.func.now())
    user_id = sa.Column(sa.BigInteger)
    offer_id = sa.Column(sa.Integer)
    price = sa.Column(sa.BigInteger)
    limit = sa.Column(sa.Text)
    count = sa.Column(sa.Float)
    type_search = sa.Column(sa.SmallInteger)
    loss = sa.Column(sa.Text)
    user_name = sa.Column(sa.Text)

    def __init__(self, user_id: int, offer_id: int, price: int, limit: str,
                 type_search: int, loss: str, count: int, user_name: str):
        self.user_id = user_id
        self.offer_id = offer_id
        self.price = price
        self.limit = limit
        self.count = count
        self.type_search = type_search
        self.loss = loss
        self.user_id = user_id
        self.user_name = user_name

    def __repr__(self):
        return f"time: {self.time}, user_id: {self.user_id}, offer_id: {self.offer_id}, " \
               f"price: {self.price}, limit: {self.limit}, type_search: {self.type_search}, " \
               f"loss: {self.loss}, count: {self.count}, user_name: {self.user_name}"


class StatsOffersBinance(Base):
    __tablename__ = 'stats_caught_offers_binance'

    i = sa.Column(sa.BigInteger, autoincrement=True, primary_key=True)
    time = sa.Column(sa.DateTime, server_default=sa.func.now())
    user_id = sa.Column(sa.BigInteger)
    offer_id = sa.Column(sa.Text)
    price = sa.Column(sa.Float)
    limit = sa.Column(sa.Text)
    count = sa.Column(sa.Float)
    type_search = sa.Column(sa.SmallInteger)
    loss = sa.Column(sa.Text)
    user_name = sa.Column(sa.Text)

    def __init__(self, user_id: int, offer_id: str, price: float, limit: str,
                 type_search: int, loss: str, count: int, user_name: str):
        self.user_id = user_id
        self.offer_id = offer_id
        self.price = price
        self.limit = limit
        self.count = count
        self.type_search = type_search
        self.loss = loss
        self.user_id = user_id
        self.user_name = user_name

    def __repr__(self):
        return f"time: {self.time}, user_id: {self.user_id}, offer_id: {self.offer_id}, " \
               f"price: {self.price}, limit: {self.limit}, type_search: {self.type_search}, " \
               f"loss: {self.loss}, count: {self.count}, user_name: {self.user_name}"


class OffersBinance(Base):
    __tablename__ = 'offers_binance'

    id_ = sa.Column(sa.Text, primary_key=True)  # Айди предложения
    price = sa.Column(sa.Float, nullable=True)  # Цена предложения
    create_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(),
        default=sa.func.now(),
        onupdate=sa.func.now(),
        server_default=sa.func.now()
    )

    def __init__(self, id_: str, price: float):
        self.id_ = id_
        self.price = price

    def __repr__(self):
        return f"id_({self.id_}), price({self.price}), " \
               f"create_at({self.create_at}), updated_at({self.updated_at})"
