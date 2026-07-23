import sqlite3

def run():
    conn = sqlite3.connect('sukabumi_flasher.db')
    try:
        # Tambah kolom masa_garansi ke tabel servis
        conn.execute("ALTER TABLE servis ADD COLUMN masa_garansi TEXT DEFAULT '1 Bulan'")
        conn.commit()
        print("Success: Added masa_garansi to servis")
    except Exception as e:
        print(f"Info/Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run()
