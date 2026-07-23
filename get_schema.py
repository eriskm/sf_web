import sqlite3
import os
try:
    conn = sqlite3.connect('sukabumi_flasher.db')
    cursor = conn.cursor()
    cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for type, name, sql in tables:
        print(f'Table: {name}')
        print(f'SQL: {sql}\n')
    conn.close()
except Exception as e:
    print(e)
