from extensions import db_session


class AISKalkulator:
    """Perhitungan operasional yang selalu memakai koneksi mandiri dan terkelola."""

    @staticmethod
    def hitung_laba_hari_ini():
        with db_session() as conn:
            laba_kotor = conn.execute(
                """SELECT COALESCE(SUM(laba_kotor), 0) AS total
                   FROM servis
                   WHERE status = 'Cash'
                   AND (COALESCE(modal_part, 0) > 0
                        OR COALESCE(modal_jasa, 0) > 0
                        OR COALESCE(lain_lain, 0) > 0)"""
            ).fetchone()[0]
            tambahan = conn.execute(
                """SELECT COALESCE(
                       SUM(CASE WHEN jenis = 'Masuk' THEN nominal ELSE -nominal END),
                       0
                   ) AS total
                   FROM transaksi_tambahan
                   WHERE uraian != 'MODAL KAS KECIL (LACI)'"""
            ).fetchone()[0]
            beban = conn.execute(
                'SELECT COALESCE(SUM(nilai), 0) AS total FROM beban'
            ).fetchone()[0]

        return {
            'laba_kotor': laba_kotor,
            'tambahan': tambahan,
            'beban': beban,
            'laba_bersih': laba_kotor + tambahan - beban,
        }

    @staticmethod
    def hitung_bagi_hasil(laba_bersih):
        if laba_bersih <= 0:
            return {'karyawan': 0, 'kas_aset': 0, 'founder': 0, 'investor': 0}

        return {
            'karyawan': laba_bersih * 0.10,
            'kas_aset': laba_bersih * 0.30,
            'founder': laba_bersih * 0.30,
            'investor': laba_bersih * 0.30,
        }

    @staticmethod
    def cek_milestone():
        data = AISKalkulator.hitung_laba_hari_ini()
        laba_kotor = data['laba_kotor'] + data['tambahan']

        with db_session() as conn:
            gaji = conn.execute(
                "SELECT COALESCE(SUM(nilai), 0) FROM beban WHERE LOWER(TRIM(kategori)) = 'gaji'"
            ).fetchone()[0]
            operasional = conn.execute(
                "SELECT COALESCE(SUM(nilai), 0) FROM beban WHERE LOWER(TRIM(kategori)) = 'operasional'"
            ).fetchone()[0]

        total_beban = gaji + operasional
        status = 'OTW'
        if gaji > 0 and laba_kotor >= gaji:
            status = 'CTS'
        if total_beban > 0 and laba_kotor >= total_beban:
            status = 'CTH'

        return {
            'laba_kotor': laba_kotor,
            'total_beban': total_beban,
            'status': status,
            'gaji': gaji,
            'ops': operasional,
        }
