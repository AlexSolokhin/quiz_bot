import os
import logging.config
from dotenv import load_dotenv, find_dotenv
from peewee import SqliteDatabase
from logging_config import dict_config

if not find_dotenv():
    exit('Переменные окружения не загружены: проверьте файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB = SqliteDatabase('quiz_database/quiz_db')
logging.config.dictConfig(dict_config)
bot_logger = logging.getLogger('admin_logger')
db_logger = logging.getLogger('bd_logger')
