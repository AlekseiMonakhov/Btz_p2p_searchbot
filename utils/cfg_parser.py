import configparser, os, datetime
from loguru import logger


class Cfg:
    config = configparser.ConfigParser()  # создаём объекта парсера конфига
    path = 'data/p2p_alert_settings.ini'
    last_update = None

    @staticmethod
    def create_config():
        Cfg.config.add_section("Bitzlato")
        Cfg.config.set("Bitzlato", "average_price", "0")
        Cfg.config.set("Bitzlato", "median_price", "0")

        Cfg.config.add_section("Binance")
        Cfg.config.set("Binance", "average_price", "0")
        Cfg.config.set("Binance", "median_price", "0")
        Cfg.config.set("Binance", "official_price", "0")

        with open(Cfg.path, "w") as config_file:
            Cfg.config.write(config_file)

    @staticmethod
    def read_config():
        if not os.path.exists(Cfg.path):
            logger.warning(f'Конфиг {Cfg.path} не найден! Создаю новый.')
            Cfg.create_config()
        Cfg.config.read(Cfg.path)  # читаем конфиг

    class Bitzlato:
        @staticmethod
        def get_average_price():
            Cfg.read_config()
            return int(Cfg.config["Bitzlato"]["average_price"])

        @staticmethod
        def get_median_price():
            Cfg.read_config()
            return int(Cfg.config["Bitzlato"]["median_price"])

        @staticmethod
        def set_average_price(price):
            Cfg.read_config()
            Cfg.config.set("Bitzlato", 'average_price', str(price))

            with open(Cfg.path, "w") as config_file:
                Cfg.config.write(config_file)
            Cfg.last_update = datetime.datetime.now()

        @staticmethod
        def set_median_price(price):
            Cfg.read_config()
            Cfg.config.set("Bitzlato", 'median_price', str(price))

            with open(Cfg.path, "w") as config_file:
                Cfg.config.write(config_file)
            Cfg.last_update = datetime.datetime.now()

    class Binance:
        @staticmethod
        def get_average_price():
            Cfg.read_config()
            return int(Cfg.config["Binance"]["average_price"])

        @staticmethod
        def get_median_price():
            Cfg.read_config()
            return int(Cfg.config["Binance"]["median_price"])

        @staticmethod
        def get_official_price():
            Cfg.read_config()
            return int(Cfg.config["Binance"]["official_price"])

        @staticmethod
        def set_average_price(price):
            Cfg.read_config()
            Cfg.config.set("Binance", 'average_price', str(price))

            with open(Cfg.path, "w") as config_file:
                Cfg.config.write(config_file)
            Cfg.last_update = datetime.datetime.now()

        @staticmethod
        def set_median_price(price):
            Cfg.read_config()
            Cfg.config.set("Binance", 'median_price', str(price))

            with open(Cfg.path, "w") as config_file:
                Cfg.config.write(config_file)
            Cfg.last_update = datetime.datetime.now()

        @staticmethod
        def set_official_price(price):
            Cfg.read_config()
            Cfg.config.set("Binance", 'official_price', str(price))

            with open(Cfg.path, "w") as config_file:
                Cfg.config.write(config_file)
            Cfg.last_update = datetime.datetime.now()
