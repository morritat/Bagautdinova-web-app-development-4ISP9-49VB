"""Проверка плана запроса: python check_perf.py"""
import sqlite3
conn = sqlite3.connect("conferences.db")
# Если в плане USING INDEX — запрос быстрый
for row in conn.execute("EXPLAIN QUERY PLAN SELECT * FROM bookings WHERE user_id = 1"):
    print(row)
for row in conn.execute("EXPLAIN QUERY PLAN SELECT * FROM bookings WHERE status = 'Новая'"):
    print(row)