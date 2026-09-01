"""Respons deterministik untuk perintah sederhana bot manajer dan akuntan."""

from __future__ import annotations

from .kalkulator import AISKalkulator


def _rupiah(value) -> str:
    return f"Rp {float(value or 0):,.0f}".replace(",", ".")


class AISBotLogic:
    """Logika ringkas bot sebelum permintaan diteruskan ke model AI."""

    @staticmethod
    def proses_pesan_akuntan(user_text):
        if "laba" in str(user_text or "").lower():
            data = AISKalkulator.hitung_laba_hari_ini()
            return (
                "<b>LAPORAN KEUANGAN AIS</b>\n"
                "----------------------------\n"
                f"Laba Kotor: {_rupiah(data['laba_kotor'])}\n"
                f"Total Beban: {_rupiah(data['beban'])}\n"
                f"<b>LABA BERSIH: {_rupiah(data['laba_bersih'])}</b>"
            )
        return "Siap, Bos Akuntan. Ada yang bisa dibantu?"

    @staticmethod
    def proses_pesan_manajer(user_text):
        if "status" in str(user_text or "").lower():
            milestone = AISKalkulator.cek_milestone()
            return (
                "<b>STATUS OPERASIONAL AIS</b>\n"
                "----------------------------\n"
                f"Laba Kotor: {_rupiah(milestone['laba_kotor'])}\n"
                f"Target Beban: {_rupiah(milestone['total_beban'])}\n"
                f"Status: <b>{milestone['status']}</b>"
            )
        return "Pusat komando siap, Bos Manajer."