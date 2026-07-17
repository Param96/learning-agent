import sqlite3
import time

print("Connecting...")
conn = sqlite3.connect('/tmp/readonly_test/test.db', timeout=2.0)
print("Setting WAL...")
try:
    conn.execute("PRAGMA journal_mode=WAL")
    print("WAL set.")
except Exception as e:
    print(f"WAL Error: {e}")

print("Creating table...")
try:
    conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    print("Table created.")
except Exception as e:
    print(f"Create Error: {e}")
