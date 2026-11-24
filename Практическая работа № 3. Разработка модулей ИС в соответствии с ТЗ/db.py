# db.py — класс Database: выполнение SQL-запросов к SQLite
import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row          # строки как словари
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _run(self, sql, params, fetch):
        conn = self._connect()
        try:
            cur = conn.execute(sql, params or ())
            if fetch == "one":
                row = cur.fetchone()
                return dict(row) if row else None
            if fetch == "all":
                return [dict(row) for row in cur.fetchall()]
            conn.commit()
            return None
        finally:
            conn.close()

    def fetch_all(self, sql, params=None):
        """SELECT: список строк-словарей."""
        return self._run(sql, params, "all")

    def fetch_one(self, sql, params=None):
        """SELECT: одна строка или None."""
        return self._run(sql, params, "one")

    def execute(self, sql, params=None):
        """INSERT / UPDATE / DELETE."""
        self._run(sql, params, None)

def init_db(db_path):
    """Создаёт таблицы по schema.sql."""
    with open("schema.sql", encoding="utf-8") as f:
        script = f.read()
    conn = sqlite3.connect(db_path)
    conn.executescript(script)
    conn.commit()
    conn.close()