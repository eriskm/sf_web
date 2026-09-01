import logging
import os
import re

import pymysql


logger = logging.getLogger(__name__)


ALLOWED_TABLES = {
    'servis',
    'beban',
    'kas_utama',
    'transaksi_tambahan',
    'arsip_servis',
    'milestone_logs',
    'pembayaran',
    'arsip_garansi',
    'arsip_pelanggan',
    'data_sparepart',
    'master_kas',
}
SENSITIVE_SQL = re.compile(
    r'\b(?:password|no_wa|bukti_bayar|foto_profil)\b',
    re.IGNORECASE,
)
FORBIDDEN_SQL = re.compile(
    r'\b(?:INTO\s+OUTFILE|INTO\s+DUMPFILE|LOAD_FILE|SLEEP|BENCHMARK|'
    r'INFORMATION_SCHEMA|PERFORMANCE_SCHEMA|MYSQL\.|SYS\.|'
    r'GET_LOCK|RELEASE_LOCK|IS_FREE_LOCK|MASTER_POS_WAIT)\b',

    re.IGNORECASE,
)
TABLE_REFERENCE = re.compile(r'\b(?:FROM|JOIN)\s+`?([A-Za-z_][A-Za-z0-9_]*)`?', re.IGNORECASE)


def _validate_select(sql_query):
    query = str(sql_query or '').strip()
    if query.endswith(';'):
        query = query[:-1].rstrip()

    if not query or not re.match(r'^SELECT\b', query, re.IGNORECASE):
        raise ValueError('Hanya satu query SELECT yang diizinkan.')
    if ';' in query or '--' in query or '/*' in query or '*/' in query or '#' in query:
        raise ValueError('Komentar dan multi-statement SQL tidak diizinkan.')
    if FORBIDDEN_SQL.search(query):
        raise ValueError('Fungsi atau schema tersebut tidak diizinkan.')
    if SENSITIVE_SQL.search(query):
        raise ValueError('Kolom sensitif tidak boleh diakses oleh AI.')

    without_count_star = re.sub(
        r'COUNT\s*\(\s*\*\s*\)',
        'COUNT_ALL',
        query,
        flags=re.IGNORECASE,
    )
    if '*' in without_count_star:
        raise ValueError('SELECT * tidak diizinkan; sebutkan kolom yang diperlukan.')
    if re.search(
        r'\bFROM\s+`?[A-Za-z_][A-Za-z0-9_]*`?'
        r'(?:\s+(?:AS\s+)?[A-Za-z_][A-Za-z0-9_]*)?\s*,',
        query,
        re.IGNORECASE,
    ):
        raise ValueError('Gunakan JOIN eksplisit; comma join tidak diizinkan.')

    referenced_tables = {name.lower() for name in TABLE_REFERENCE.findall(query)}
    forbidden_tables = referenced_tables - ALLOWED_TABLES
    if forbidden_tables:
        raise ValueError(f"Tabel tidak diizinkan: {', '.join(sorted(forbidden_tables))}")
    if not referenced_tables:
        raise ValueError('Query harus membaca tabel aplikasi yang diizinkan.')

    return query


def query_mysql(sql_query):
    """Run a bounded, read-only SELECT over explicitly allowed application tables."""
    db = None
    try:
        query = _validate_select(sql_query)
        db = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'db_ais_systems'),
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4',
            connect_timeout=5,
            read_timeout=8,
            write_timeout=8,
            autocommit=False,
        )
        cursor = db.cursor()
        cursor.execute('SET TRANSACTION READ ONLY')
        cursor.execute(f'SELECT * FROM ({query}) AS sf_ai_query LIMIT 100')
        result = cursor.fetchall()
        db.rollback()

        if not result:
            return 'Data tidak ditemukan.'
        return f'Data: {result}'
    except ValueError as exc:
        return f'QUERY DITOLAK: {exc}'
    except pymysql.MySQLError:
        logger.exception('Query read-only AI gagal dijalankan.')
        return 'ERROR SQL: database tidak dapat memproses query.'
    finally:
        if db is not None:
            try:
                db.rollback()
            except pymysql.MySQLError:
                pass
            db.close()




SCHEMA_PROMPT = """
Gunakan query_mysql hanya untuk membaca data operasional yang memang diperlukan.

Tabel yang diizinkan:
- servis: id, tanggal_masuk, device, nama_user, analisa_kerusakan,
  estimasi_biaya, dp, status, harga_jual, modal_part, modal_jasa,
  laba_kotor, teknisi, tindakan_perbaikan, lain_lain, masa_garansi.
- beban: id, kategori, nama_beban, nilai.
- kas_utama: id, tanggal, saldo_awal, saldo_akhir, total_laba_bersih.
- transaksi_tambahan: id, tanggal, uraian, jenis, nominal.
- arsip_servis, arsip_garansi, arsip_pelanggan, data_sparepart,
  milestone_logs, pembayaran, dan master_kas.

Jangan meminta credential, password perangkat, token, atau data di luar kebutuhan
operasional. Untuk menambah unit servis gunakan ai_tambah_servis, bukan SQL.
"""
