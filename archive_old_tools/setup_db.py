import sqlite3
import pandas as pd

def buat_database():
    # 1. Koneksi ke Database (akan buat file baru: sukabumi_flasher.db)
    conn = sqlite3.connect('sukabumi_flasher.db')
    cursor = conn.cursor()

    # 2. Buat Tabel User untuk Login
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    # 3. Masukkan Akun Default (Password sementara: 12345)
    users = [
        ('admin', '12345', 'admin'),
        ('erik', '12345', 'teknisi'),
        ('eja', '12345', 'teknisi'),
        ('dana', '12345', 'teknisi'),
        ('owner', '12345', 'owner')
    ]
    
    try:
        cursor.executemany('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', users)
        print("Akun login berhasil didaftarkan!")
    except Exception as e:
        print(f"Gagal daftar akun: {e}")

    # 4. Pindahkan Data dari CSV Bersih ke Database
    try:
        df = pd.read_csv('data_servis_clean.csv')
        df.to_sql('servis', conn, if_exists='replace', index=False)
        print("Data servis berhasil dimigrasi ke Database SQL!")
    except Exception as e:
        print(f"Gagal migrasi data servis: {e}")

    conn.commit()
    conn.close()
    print("-----------------------------------------")
    print("Bit 2 Selesai: Database 'sukabumi_flasher.db' siap digunakan!")

if __name__ == "__main__":
    buat_database()