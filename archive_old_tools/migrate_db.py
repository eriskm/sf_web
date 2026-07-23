import sqlite3
import traceback

def migrate():
    conn = sqlite3.connect('sukabumi_flasher.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE servis ADD COLUMN updated_at DATETIME")
        print("Column updated_at added.")
    except Exception as e:
        print(f"updated_at already exists or error: {e}")
        
    try:
        cursor.execute("ALTER TABLE servis ADD COLUMN flag_kritis INTEGER DEFAULT 0")
        print("Column flag_kritis added.")
    except Exception as e:
        print(f"flag_kritis already exists or error: {e}")

    try:
        cursor.execute("UPDATE servis SET updated_at = datetime('now', 'localtime') WHERE updated_at IS NULL")
        conn.commit()
        print("Existing rows updated.")
    except Exception as e:
        print(f"Error updating existing rows: {e}")
        traceback.print_exc()

    conn.close()

if __name__ == '__main__':
    migrate()
