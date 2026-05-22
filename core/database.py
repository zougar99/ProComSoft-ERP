from config.settings import DATABASE_PATH
from database import get_db_manager


def get_connection():
    return get_db_manager(str(DATABASE_PATH)).get_connection()
