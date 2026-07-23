import sqlite3

try:
    conn = sqlite3.connect('sukabumi_flasher.db')
    conn.execute('ALTER TABLE servis ADD COLUMN "Lain-lain" INTEGER DEFAULT 0')
    conn.commit()
    print("Column 'Lain-lain' added successfully")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
