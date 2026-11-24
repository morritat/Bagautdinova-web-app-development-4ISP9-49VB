"""Создание индексов: python add_indexes.py"""
import sqlite3
conn = sqlite3.connect("conferences.db")
conn.executescript("""
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings (user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_room_id ON bookings (room_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status  ON bookings (status);
""")
conn.commit()
conn.close()
print("Индексы созданы")