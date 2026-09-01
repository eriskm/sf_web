"""Pencarian stok sparepart read-only untuk asisten lokal."""

from __future__ import annotations

import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def search_sparepart_local(query: str) -> str:
    """Cari maksimal lima sparepart berdasarkan merek, barang, atau device."""
    keyword = (query or "").strip()
    if not keyword:
        return "Masukkan nama sparepart atau tipe device yang ingin dicari."
    if len(keyword) > 100:
        return "Kata pencarian terlalu panjang (maksimal 100 karakter)."

    connection = None
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DB", "db_ais_systems"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
            read_timeout=10,
            autocommit=True,
        )
        term = f"%{keyword}%"
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT kategori, merek, jenis_barang, jenis_device, qty, harga_jual
                FROM data_sparepart
                WHERE merek LIKE %s OR jenis_barang LIKE %s OR jenis_device LIKE %s
                LIMIT 5
                """,
                (term, term, term),
            )
            results = cursor.fetchall()
    except pymysql.MySQLError:
        return "Gagal mengakses database stok. Silakan coba lagi atau hubungi admin."
    finally:
        if connection is not None:
            connection.close()

    if not results:
        return "Sparepart tersebut tidak ditemukan di stok gudang lokal."

    lines = ["HASIL CEK STOK GUDANG SF:", "--------------------------"]
    for row in results:
        price = int(row.get("harga_jual") or 0)
        lines.append(
            f"- {row.get('merek') or '-'} {row.get('jenis_barang') or '-'} "
            f"({row.get('jenis_device') or '-'}): {row.get('qty') or 0} pcs | "
            f"Harga: Rp {price:,}"
        )
    return "\n".join(lines)