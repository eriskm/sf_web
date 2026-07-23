from .database import get_db
from datetime import datetime

class AISKalkulator:
    """
    Mesin Utama Kalkulasi AIS Technologies (5 BIT Logic)
    Fokus: UKURAN & URAIAN
    """
    
    @staticmethod
    def hitung_laba_hari_ini():
        conn = get_db()
        try:
            # 1. Total Laba Kotor (Servis Cash yang sudah diisi Modalnya)
            res_kotor = conn.execute("SELECT SUM(\"Laba Kotor\") as total FROM servis WHERE Status='Cash' AND (COALESCE(\"Modal Part\", 0) > 0 OR COALESCE(\"Modal Jasa\", 0) > 0 OR COALESCE(\"Lain-lain\", 0) > 0)").fetchone()
            laba_kotor = res_kotor[0] or 0
            
            # 2. Total Transaksi Tambahan
            res_tambahan = conn.execute("SELECT SUM(CASE WHEN jenis='Masuk' THEN nominal ELSE -nominal END) as total FROM transaksi_tambahan WHERE uraian != 'MODAL KAS KECIL (LACI)'").fetchone()
            tambahan = res_tambahan[0] or 0
            
            # 3. Total Beban (Gaji & Ops)
            res_beban = conn.execute("SELECT SUM(nilai) as total FROM beban").fetchone()
            beban = res_beban[0] or 0
            
            laba_bersih = laba_kotor + tambahan - beban
            
            return {
                "laba_kotor": laba_kotor,
                "tambahan": tambahan,
                "beban": beban,
                "laba_bersih": laba_bersih
            }
        finally:
            conn.close()

    @staticmethod
    def hitung_bagi_hasil(laba_bersih):
        """
        Logika Bagi Hasil AIS Technologies:
        10% Karyawan, 30% Kas Aset, 30% Founder, 30% Investor
        """
        if laba_bersih <= 0:
            return { "karyawan": 0, "kas_aset": 0, "founder": 0, "investor": 0 }
            
        return {
            "karyawan": laba_bersih * 0.10,
            "kas_aset": laba_bersih * 0.30,
            "founder": laba_bersih * 0.30,
            "investor": laba_bersih * 0.30
        }

    @staticmethod
    def cek_milestone():
        """Cek apakah target CTS/CTO/CTH sudah tercapai"""
        data = AISKalkulator.hitung_laba_hari_ini()
        laba_kotor = data['laba_kotor'] + data['tambahan']
        
        conn = get_db()
        try:
            gaji = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'gaji'").fetchone()[0] or 0
            ops = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'operasional'").fetchone()[0] or 0
            total_beban = gaji + ops
            
            status = "CTS" # Default: Belum tutup beban
            if laba_kotor >= gaji: status = "CTO"
            if laba_kotor >= total_beban: status = "CTH"
            
            return {
                "laba_kotor": laba_kotor,
                "total_beban": total_beban,
                "status": status,
                "gaji": gaji,
                "ops": ops
            }
        finally:
            conn.close()
