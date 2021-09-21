from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
HOST = env.str("HOST")  # Тоже str, но для айпи адреса хоста

USER = str(env.str("USER"))  # Берём юзера для входа в бд
PASS = str(env.str("PASS"))  # Берём пароль для входа
BASE = str(env.str("BASE"))  # Берём название базы для входа

URL = f'postgresql+asyncpg://{USER}:{PASS}@{HOST}/{BASE}'

google_table_url = str(env.str("google_table"))  # Берём ссылку на гугл таблицу для статистики
