from database import get_db_manager
from config.settings import DATABASE_PATH


_db_instance = None


def get_database():
    global _db_instance
    if _db_instance is None:
        _db_instance = get_db_manager(str(DATABASE_PATH)).get_connection_sync()
    return _db_instance
