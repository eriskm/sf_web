import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
print(conn.execute("SELECT * FROM milestone_logs").fetchall())
