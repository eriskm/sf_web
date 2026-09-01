import os
import threading
from datetime import datetime

import requests

from extensions import db_session


LAPORAN_LOCK = threading.Lock()
MILESTONE_LOCK = threading.Lock()
TELEGRAM_TIMEOUT = (5, 15)


def _telegram_token():
    return os.getenv('BOT_TOKEN_LAPORAN', '').strip()


def _chat_ids(env_name='NOTIF_PRIVATE_ID'):
    raw = os.getenv(env_name, '').strip()
    return [chat_id.strip() for chat_id in raw.split(',') if chat_id.strip()]


def _post_telegram(endpoint, *, data, files=None):
    token = _telegram_token()
    if not token:
        print('[TELEGRAM] BOT_TOKEN_LAPORAN belum dikonfigurasi; pengiriman dibatalkan.')
        return False

    response = requests.post(
        f'https://api.telegram.org/bot{token}/{endpoint}',
        data=data,
        files=files,
        timeout=TELEGRAM_TIMEOUT,
    )
    response.raise_for_status()
    return True


def kirim_pesan_telegram(pesan, chat_ids=None):
    recipients = chat_ids or _chat_ids()
    if not recipients:
        print('[TELEGRAM] Penerima notifikasi belum dikonfigurasi; pengiriman dibatalkan.')
        return False

    sent = True
    for chat_id in recipients:
        try:
            _post_telegram(
                'sendMessage',
                data={'chat_id': chat_id, 'text': pesan, 'parse_mode': 'Markdown'},
            )
        except requests.RequestException as exc:
            sent = False
            print(f'[TELEGRAM] Gagal mengirim pesan: {exc}')
    return sent


def _run_notification(pesan):
    thread = threading.Thread(target=kirim_pesan_telegram, args=(pesan,), daemon=True)
    thread.start()
    return thread


def _format_rp(value):
    try:
        return f"Rp {int(value):,}".replace(',', '.')
    except (TypeError, ValueError):
        return f'Rp {value}'


def kirim_notif_unit_baru(device, analisa, tindakan, kelengkapan='', kondisi_fisik=''):
    detail = ''
    if kelengkapan and kelengkapan != '-':
        detail += f'\nKelengkapan: {kelengkapan}'
    if kondisi_fisik and kondisi_fisik != '-':
        detail += f'\nKondisi fisik: {kondisi_fisik}'

    pesan = (
        '*UNIT BARU MASUK*\n\n'
        f'Device: {device}\n'
        f'Analisa: {analisa or "-"}{detail}\n'
        f'Tindakan: {tindakan or "-"}'
    )
    return _run_notification(pesan)


def kirim_notif_kas_masuk(device, nama, harga_jual, laba_kotor, teknisi):
    pesan = (
        '*KAS MASUK - UNIT SELESAI*\n\n'
        f'Device: {device}\n'
        f'Konsumen: {nama}\n'
        f'Teknisi: {teknisi or "-"}\n\n'
        f'Harga jual: {_format_rp(harga_jual)}\n'
        f'Laba kotor: {_format_rp(laba_kotor)}'
    )
    return _run_notification(pesan)


def cek_dan_kirim_milestone():
    """Record and notify a milestone once per date and milestone type."""
    with MILESTONE_LOCK:
        try:
            with db_session() as conn:
                laba_servis = conn.execute(
                    """SELECT COALESCE(SUM(laba_kotor), 0) FROM servis
                       WHERE status = 'Cash'
                       AND (COALESCE(modal_part, 0) > 0
                            OR COALESCE(modal_jasa, 0) > 0
                            OR COALESCE(lain_lain, 0) > 0)"""
                ).fetchone()[0]
                laba_tambahan = conn.execute(
                    """SELECT COALESCE(SUM(CASE WHEN jenis='Masuk' THEN nominal ELSE -nominal END), 0)
                       FROM transaksi_tambahan
                       WHERE uraian != 'MODAL KAS KECIL (LACI)'"""
                ).fetchone()[0]
                gaji = conn.execute(
                    "SELECT COALESCE(SUM(nilai), 0) FROM beban WHERE LOWER(TRIM(kategori)) = 'gaji'"
                ).fetchone()[0]
                operasional = conn.execute(
                    "SELECT COALESCE(SUM(nilai), 0) FROM beban WHERE LOWER(TRIM(kategori)) = 'operasional'"
                ).fetchone()[0]

                laba_kotor = laba_servis + laba_tambahan
                total_beban = gaji + operasional
                jenis = None
                if total_beban > 0 and laba_kotor >= total_beban:
                    jenis = 'CTH'
                elif gaji > 0 and laba_kotor >= gaji:
                    jenis = 'CTS'

                if not jenis:
                    return False

                tanggal = datetime.now().strftime('%Y-%m-%d')
                existing = conn.execute(
                    'SELECT 1 FROM milestone_logs WHERE tanggal = %s AND jenis = %s LIMIT 1',
                    (tanggal, jenis),
                ).fetchone()
                if existing:
                    return False

                conn.execute(
                    'INSERT INTO milestone_logs (tanggal, jenis) VALUES (%s, %s)',
                    (tanggal, jenis),
                )

            pesan = (
                f'*MILESTONE {jenis} TERCAPAI*\n'
                f'Laba kotor: {_format_rp(laba_kotor)}\n'
                f'Total beban: {_format_rp(total_beban)}'
            )
            _run_notification(pesan)
            return True
        except Exception as exc:
            print(f'[MILESTONE] Gagal memproses milestone: {exc}')
            return False


def kirim_laporan_telegram(path_gambar, jenis='TUTUP'):
    with LAPORAN_LOCK:
        chat_ids = _chat_ids('CHAT_ID_LAPORAN')
        if not chat_ids:
            print('[TELEGRAM] CHAT_ID_LAPORAN belum dikonfigurasi; laporan dibatalkan.')
            return False
        if not os.path.isfile(path_gambar):
            print(f'[TELEGRAM] File laporan tidak ditemukan: {path_gambar}')
            return False

        caption = (
            '*LAPORAN TUTUP BUKU*\nSiklus operasional telah ditutup.'
            if jenis == 'TUTUP'
            else '*LAPORAN BUKA BUKU*\nSiklus pembukuan baru telah dimulai.'
        )
        try:
            with open(path_gambar, 'rb') as image_file:
                return _post_telegram(
                    'sendPhoto',
                    data={
                        'chat_id': chat_ids[0],
                        'caption': caption,
                        'parse_mode': 'Markdown',
                    },
                    files={'photo': image_file},
                )
        except (OSError, requests.RequestException) as exc:
            print(f'[TELEGRAM] Gagal mengirim laporan: {exc}')
            return False


def _parse_money(value):
    try:
        cleaned = (
            str(value)
            .lower()
            .replace('rp', '')
            .replace('.', '')
            .replace(',', '')
            .replace('rb', '000')
            .replace('k', '000')
            .strip()
        )
        return max(0, int(float(cleaned or 0)))
    except (TypeError, ValueError):
        return 0


def ai_tambah_servis(
    nama,
    device,
    kerusakan,
    estimasi=0,
    wa='-',
    tindakan='-',
    teknisi='Teknisi SF',
    dp=0,
):
    if not str(nama or '').strip() or not str(device or '').strip():
        return False

    try:
        with db_session() as conn:
            conn.execute(
                """INSERT INTO servis (
                       tanggal_masuk, device, nama_user, password, no_wa,
                       analisa_kerusakan, estimasi_biaya, dp, status,
                       tindakan_perbaikan, teknisi
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Analisa', %s, %s)""",
                (
                    datetime.now().strftime('%Y-%m-%d'),
                    str(device).strip(),
                    str(nama).strip(),
                    '-',
                    str(wa or '-').strip(),
                    str(kerusakan or '-').strip(),
                    _parse_money(estimasi),
                    _parse_money(dp),
                    str(tindakan or 'Cek & Analisa').strip(),
                    str(teknisi or 'Teknisi SF').strip(),
                ),
            )
        kirim_notif_unit_baru(device, kerusakan, tindakan)
        return True
    except Exception as exc:
        print(f'[AI] Gagal menambah servis: {exc}')
        return False
