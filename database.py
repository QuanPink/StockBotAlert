import sqlite3
from typing import List, Tuple

import config


class Database:
    _instance = None

    def __new__(cls):
        """Singleton pattern - chỉ 1 DB connection"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'conn'):
            self.conn = sqlite3.connect(
                config.DATABASE_FILE,
                check_same_thread=False,
                isolation_level='DEFERRED',  # Better performance
                timeout=30
            )
            # Enable WAL mode for better concurrent access
            self.conn.execute('PRAGMA journal_mode=WAL')
            self.conn.execute('PRAGMA synchronous=NORMAL')
            self.create_tables()

    def create_tables(self):
        """Create alerts table if not exists"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                target_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol 
                ON alerts(symbol)
            ''')

        cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_symbol 
                ON alerts(chat_id, symbol)
            ''')
        self.conn.commit()

    def add_alert(self, chat_id: int, symbol: str, target_price: float) -> bool:
        """Add a new alert"""
        try:
            # Check if alert already exists FOR THIS USER
            if self.alert_exists(chat_id, symbol):
                return False

            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO alerts (chat_id, symbol, target_price) VALUES (?, ?, ?)',
                (chat_id, symbol.upper(), target_price)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding alert: {e}")
            return False

    def alert_exists(self, chat_id: int, symbol: str) -> bool:
        """Check if alert already exists for THIS USER and symbol"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT id FROM alerts WHERE chat_id = ? AND symbol = ?',
                (chat_id, symbol.upper())
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking alert existence: {e}")
            return False

    def remove_alerts_by_symbol(self, chat_id: int, symbol: str) -> int:
        """Remove all alerts for a symbol FOR THIS USER"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM alerts WHERE chat_id = ? AND symbol = ?',
                (chat_id, symbol.upper())
            )
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error removing alerts: {e}")
            return 0

    def update_alert_by_symbol(self, chat_id: int, symbol: str, new_price: float) -> bool:
        """Update alert price by symbol FOR THIS USER"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE alerts SET target_price = ? WHERE chat_id = ? AND symbol = ?',
                (new_price, chat_id, symbol.upper())
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating alert: {e}")
            return False

    def clear_user_alerts(self, chat_id: int) -> int:
        """Remove all alerts for a user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM alerts WHERE chat_id = ?',
                (chat_id,)
            )
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error clearing alerts: {e}")
            return 0

    def get_all_alerts(self) -> List[Tuple]:
        """Get all alerts"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, chat_id, symbol, target_price FROM alerts')
        return cursor.fetchall()

    def get_user_alerts(self, chat_id: int) -> List[Tuple]:
        """Get all alerts for a specific user"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, symbol, target_price FROM alerts WHERE chat_id = ? ORDER BY symbol',
            (chat_id,)
        )
        return cursor.fetchall()

    def close(self):
        """Close database connection"""
        self.conn.close()
