import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='servis'")
print(cursor.fetchone()[0])
