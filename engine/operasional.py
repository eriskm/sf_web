from .database import get_db
from .kalkulator import AISKalkulator
from datetime import datetime
import os
import requests

class AISOperasional:
    """
    Mesin Operasional AIS Technologies
    Fokus: URUTAN & ULANGAN
    """
    
    @staticmethod
    def ritual_tutup_buku():
        """
        Logika Tutup Buku 16:00 WIB
        1. Hitung laba bersih.
        2. Alokasikan bagi hasil.
        3. Pindahkan data ke arsip (SQLite -> MySQL jika ada).
        """
        data_laba = AISKalkulator.hitung_laba_hari_ini()
        bagi_hasil = AISKalkulator.hitung_bagi_hasil(data_laba['laba_bersih'])
        
        # Logika pengarsipan bisa ditaruh di sini
        # Untuk sementara, kita catat di log
        return {
            "status": "Sukses",
            "data": data_laba,
            "bagi_hasil": bagi_hasil
        }

    @staticmethod
    def kirim_notif_telegram(pesan, token, chat_ids):
        """Helper buat kirim pesan ke banyak penerima"""
        for chat_id in chat_ids:
            try:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {'chat_id': chat_id.strip(), 'text': pesan, 'parse_mode': 'HTML'}
                requests.post(url, data=payload)
            except Exception as e:
                print(f"[ENGINE ERROR] Gagal kirim notif: {e}")
