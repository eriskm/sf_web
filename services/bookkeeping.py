class BookkeepingError(ValueError):
    pass


def calculate_system_balance(conn, lock=False):
    """Reproduce the dashboard cash balance using server-side database values."""
    lock_sql = ' FOR UPDATE' if lock else ''
    last_kas = conn.execute(
        f'SELECT saldo_akhir FROM kas_utama ORDER BY id DESC LIMIT 1{lock_sql}'
    ).fetchone()
    saldo_awal = int(last_kas['saldo_akhir'] or 0) if last_kas else 0

    cash_rows = conn.execute(
        """SELECT harga_jual, modal_part, modal_jasa, lain_lain
           FROM servis
           WHERE status = 'Cash'
           AND (COALESCE(modal_part, 0) > 0
                OR COALESCE(modal_jasa, 0) > 0
                OR COALESCE(lain_lain, 0) > 0)"""
        + lock_sql
    ).fetchall()
    tambahan_rows = conn.execute(
        'SELECT id, uraian, jenis, nominal FROM transaksi_tambahan' + lock_sql
    ).fetchall()
    beban = conn.execute(
        """SELECT
               COALESCE(SUM(CASE WHEN LOWER(TRIM(kategori)) = 'gaji' THEN nilai ELSE 0 END), 0) AS gaji,
               COALESCE(SUM(CASE WHEN LOWER(TRIM(kategori)) = 'operasional' THEN nilai ELSE 0 END), 0) AS operasional
           FROM beban"""
    ).fetchone()

    modal_kas_kecil = sum(
        int(row['nominal'] or 0)
        for row in tambahan_rows
        if row['uraian'] == 'MODAL KAS KECIL (LACI)'
    )
    total_penjualan = sum(int(row['harga_jual'] or 0) for row in cash_rows)
    total_modal = sum(
        int(row['modal_part'] or 0)
        + int(row['modal_jasa'] or 0)
        + int(row['lain_lain'] or 0)
        for row in cash_rows
    )
    total_beban = int(beban['gaji'] or 0) + int(beban['operasional'] or 0)

    laba_bersih = total_penjualan - total_modal - total_beban
    saldo = saldo_awal + modal_kas_kecil + total_penjualan - total_modal - total_beban

    if laba_bersih > 0:
        saldo -= int(round(laba_bersih * 0.10))
        saldo -= int(round(laba_bersih * 0.30))
        saldo -= int(round(laba_bersih * 0.30))

    for row in tambahan_rows:
        if row['uraian'] == 'MODAL KAS KECIL (LACI)':
            continue
        nominal = int(row['nominal'] or 0)
        saldo += nominal if row['jenis'] == 'Masuk' else -nominal

    return int(saldo), int(laba_bersih)
