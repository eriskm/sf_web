from .kalkulator import AISKalkulator
import json

class AISBotLogic:
    """
    Logika Berpikir 4 Bot AIS (Manajer, Akuntan, CS, Sparepart)
    Fokus: URUSAN & URAIAN
    """
    
    @staticmethod
    def proses_pesan_akuntan(user_text):
        # Contoh logika sederhana, bisa dikembangkan dengan AI
        if "laba" in user_text.lower():
            data = AISKalkulator.hitung_laba_hari_ini()
            return (f"📊 <b>LAPORAN KEUANGAN AIS</b>\n"
                    f"----------------------------\n"
                    f"💰 Laba Kotor: Rp {data['laba_kotor']:,.0f}\n"
                    f"📉 Total Beban: Rp {data['beban']:,.0f}\n"
                    f"✅ <b>LABA BERSIH: Rp {data['laba_bersih']:,.0f}</b>")
        return "Siap Bos Akuntan! Ada yang bisa dibantu?"

    @staticmethod
    def proses_pesan_manajer(user_text):
        if "status" in user_text.lower():
            milestone = AISKalkulator.cek_milestone()
            return (f"🛰️ <b>STATUS OPERASIONAL AIS</b>\n"
                    f"----------------------------\n"
                    f"📈 Laba Kotor: Rp {milestone['laba_kotor']:,.0f}\n"
                    f"🏁 Target Beban: Rp {milestone['total_beban']:,.0f}\n"
                    f"🚩 Status: <b>{milestone['status']}</b>")
        return "Pusat Komando Siap, Bos Manajer!"
