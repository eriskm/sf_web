"""Orkestrasi operasional tingkat tinggi untuk AIS."""

from __future__ import annotations

import logging

import requests

from .kalkulator import AISKalkulator

logger = logging.getLogger(__name__)


class AISOperasional:
    """Mesin operasional untuk perhitungan dan notifikasi eksplisit."""

    @staticmethod
    def ritual_tutup_buku():
        """Hitung ringkasan laba dan alokasi tanpa memutasi database."""
        data_laba = AISKalkulator.hitung_laba_hari_ini()
        bagi_hasil = AISKalkulator.hitung_bagi_hasil(data_laba["laba_bersih"])
        return {"status": "Sukses", "data": data_laba, "bagi_hasil": bagi_hasil}

    @staticmethod
    def kirim_notif_telegram(pesan, token, chat_ids):
        """Kirim pesan hanya bila token dan penerima dikonfigurasi secara eksplisit."""
        recipients = [str(chat_id).strip() for chat_id in (chat_ids or []) if str(chat_id).strip()]
        if not token or not recipients or not str(pesan or "").strip():
            logger.warning("Notifikasi Telegram diblokir karena konfigurasi tidak lengkap.")
            return False

        delivered = True
        for chat_id in recipients:
            try:
                response = requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={"chat_id": chat_id, "text": str(pesan), "parse_mode": "HTML"},
                    timeout=(5, 20),
                )
                response.raise_for_status()
            except requests.RequestException:
                delivered = False
                logger.exception("Notifikasi Telegram gagal dikirim ke penerima yang diizinkan.")
        return delivered