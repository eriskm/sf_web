import sqlite3
import pymysql

# 1. SQLite Schema
try:
    conn = sqlite3.connect('sukabumi_flasher.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    with open('schema_sqlite.txt', 'w', encoding='utf-8') as f:
        f.write("=== SQLite Schema (sukabumi_flasher.db) ===\n\n")
        for table in tables:
            f.write(f"Table: {table[0]}\n")
            f.write(f"{table[1]}\n\n")
    print("SQLite schema extracted.")
    conn.close()
except Exception as e:
    print(f"Error reading SQLite: {e}")

# 2. MySQL Schema
try:
    db = pymysql.connect(host='localhost', user='root', password='', database='db_ais_systems')
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    with open('schema_mysql.txt', 'w', encoding='utf-8') as f:
        f.write("=== MySQL Schema (db_ais_systems) ===\n\n")
        for table in tables:
            table_name = table[0]
            f.write(f"Table: {table_name}\n")
            cursor.execute(f"SHOW CREATE TABLE {table_name}")
            create_stmt = cursor.fetchone()[1]
            f.write(f"{create_stmt}\n\n")
    print("MySQL schema extracted.")
    db.close()
except Exception as e:
    print(f"Error reading MySQL: {e}")
