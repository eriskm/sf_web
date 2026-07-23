import os
import sqlite3
import pymysql

def query_sqlite(sql_query: str) -> str:
    """Run a strictly SELECT SQL query on the SQLite database (sukabumi_flasher.db) and return results."""
    sql_query = sql_query.strip()
    # Keamanan: Hanya izinkan SELECT
    if not sql_query.upper().startswith("SELECT"):
        return "ERROR: Dilarang merubah data. Hanya operasi SELECT yang diizinkan."
    
    try:
        from .database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        conn.close()
        
        if not result:
            return "Data tidak ditemukan."
            
        return f"Columns: {columns}\nData: {result[:50]}" # Limit to 50 rows to prevent token overflow
    except Exception as e:
        return f"ERROR SQL: {str(e)}"

def query_mysql(sql_query: str) -> str:
    """Run a strictly SELECT SQL query on the MySQL database (db_ais_systems) and return results."""
    sql_query = sql_query.strip()
    if not sql_query.upper().startswith("SELECT"):
        return "ERROR: Dilarang merubah data. Hanya operasi SELECT yang diizinkan."
        
    try:
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        database = os.getenv('MYSQL_DB', 'db_ais_systems')
        db = pymysql.connect(host=host, user=user, password=password, database=database)
        cursor = db.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        db.close()
        
        if not result:
            return "Data tidak ditemukan."
            
        return f"Columns: {columns}\nData: {result[:50]}"
    except Exception as e:
        return f"ERROR SQL: {str(e)}"

SCHEMA_PROMPT = """
Daftar Database & Tabel yang bisa kamu query:

1. SQLite (sukabumi_flasher.db) -> gunakan tool `query_sqlite(sql_query)`
   - tabel: `servis` (No, "Tanggal Masuk", Device, "Nama User", PassWord, "No. WA", Deadline, "Analisa Kerusakan", "Estimasi Biaya", DP, Status, Part, Tindakan, "Harga Jual", "Modal Part", "Modal Jasa", "Laba Kotor", Teknisi, "Tindakan Perbaikan", "Lain-lain", masa_garansi, updated_at, flag_kritis)
   - tabel: `beban` (id, kategori, nama_beban, nilai)
   - tabel: `kas_utama` (id, tanggal, saldo_awal, saldo_akhir, total_laba_bersih)
   - tabel: `transaksi_tambahan` (id, tanggal, uraian, jenis, nominal)
   - tabel: `arsip_servis` (id, tanggal_masuk, tanggal_keluar, nama_user, wa, device, kerusakan, tindakan, modal_part, modal_jasa, harga_jual, laba_kotor, teknisi)
   - tabel: `milestone_logs` (tanggal, jenis)
   - tabel: `pembayaran` (id, servis_id, metode, nominal, status, bukti_bayar, tanggal)

2. MySQL (db_ais_systems) -> gunakan tool `query_mysql(sql_query)`
   - tabel: `arsip_garansi` (id_garansi, id_arsip, nama_user, device, tgl_mulai, tgl_akhir)
   - tabel: `arsip_pelanggan` (id_arsip, nama_user, no_wa, device, tindakan, harga_jual, status_final)
   - tabel: `data_sparepart` (id_sparepart, kategori, merek, jenis_barang, jenis_device, qty, tanggal_masuk, harga_beli, harga_jual)
   - tabel: `master_kas` (id_kas, kas_kecil_laci, kas_aset_pengelola)

3. Input/Tambah Unit Servis Baru -> gunakan tool `ai_tambah_servis(nama, device, kerusakan, estimasi, wa, tindakan, teknisi)`
   - Jika pengguna meminta memasukkan/menambahkan unit servis baru ke sistem, WAJIB panggil tool `ai_tambah_servis` dengan parameter yang sesuai.

ATURAN PENTING:
- JIKA ANDA DIMINTA INFORMASI TENTANG DATA (LABA, KEUANGAN, NAMA PELANGGAN, STOK, DLL), ANDA WAJIB MENGGUNAKAN TOOL INI UNTUK MENCARI DATANYA DULU DARI DATABASE SEBELUM MENJAWAB.
- GUNAKAN TANDA KUTIP PADA NAMA KOLOM YANG MEMILIKI SPASI DI SQLITE (misal: SELECT "Tanggal Masuk" FROM servis).
"""
