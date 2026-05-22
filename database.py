"""
Database Connection Manager
Handles SQLite database connections and initialization
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class DatabaseManager:
    """Manages database connections and schema initialization"""
    
    def __init__(self, db_path: str = "erp_app.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database file exists and schema is initialized"""
        if not self.db_path.exists():
            # Create database file
            self.db_path.touch()
            # Initialize schema
            self._initialize_schema()
        else:
            # Check if schema exists, if not initialize
            self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize database schema from SQL file or SQLAlchemy models"""
        schema_file = Path(__file__).parent.parent / "storage" / "erp_schema.sql"
        
        if schema_file.exists():
            with self.get_connection() as conn:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                    conn.executescript(schema_sql)
                    conn.commit()
        else:
            from database.models import init_database as sqlalchemy_init
            sqlalchemy_init()
    
    @contextmanager
    def get_connection(self):
        """
        Get database connection (context manager)
        
        Usage:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM ...")
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_connection_sync(self) -> sqlite3.Connection:
        """
        Get database connection (synchronous, manual management)
        
        Returns:
            sqlite3.Connection: Database connection
            
        Note: You must manually close this connection
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def execute_script(self, script_path: Path):
        """Execute SQL script file"""
        with self.get_connection() as conn:
            with open(script_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
                conn.commit()
    
    def backup(self, backup_path: Optional[Path] = None):
        """
        Create database backup
        
        Args:
            backup_path: Path for backup file (default: db_path.backup)
        """
        if backup_path is None:
            backup_path = self.db_path.with_suffix('.backup.db')
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def restore(self, backup_path: Path):
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
        """
        import shutil
        shutil.copy2(backup_path, self.db_path)


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(db_path: str = "erp_app.db") -> DatabaseManager:
    """
    Get global database manager instance
    
    Args:
        db_path: Path to database file
        
    Returns:
        DatabaseManager: Database manager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager


def get_connection():
    """
    Get database connection (convenience function)
    
    Returns:
        Context manager for database connection
    """
    return get_db_manager().get_connection()
