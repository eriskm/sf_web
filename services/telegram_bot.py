import os
import secrets
import time
import json
import asyncio
import threading
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load env
load_dotenv('.env')

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Engine imports
from extensions import db_session
from engine.db_tools import query_mysql, SCHEMA_PROMPT

# AIS Logic might be embedded in app.py, so we need to copy or import them.
# In app.py, AISBotLogic and AISKalkulator are defined as classes.
# We will import them if they exist in engine, but wait!
# AISBotLogic and AISKalkulator are defined in app.py in the original code!
# Let's import them from app directly for now (to avoid breaking).
from engine.bot_logic import AISBotLogic
from engine.kalkulator import AISKalkulator

from helpers import ai_tambah_servis

# Globals
AI_LOCK = threading.Lock()
PENDING_LOCK = threading.Lock()
PENDING_UNITS = {}

try:
    API_KEY = os.getenv('GEMINI_API_KEY')
    if API_KEY:
        client_gemini = genai.Client(api_key=API_KEY)
    else:
        client_gemini = None
except Exception as e:
    print(f"[AI] Gemini Cloud gagal dimuat: {e}")
    client_gemini = None

ALLOWED_TELEGRAM_IDS = []
_allowed = os.getenv('ALLOWED_TELEGRAM_IDS', '')
if _allowed:
    try:
        ALLOWED_TELEGRAM_IDS = [int(x.strip()) for x in _allowed.split(',') if x.strip()]
    except Exception:
        pass

def deteksi_is_tambah_unit(user_text: str) -> bool:
    text_lower = user_text.lower().strip()
    if any(text_lower.startswith(prefix) for prefix in ['/masuk', '/tambah', '/servis', '/unit', 'masuk ', 'tambah ']):
        return True
    pola_kata = ['masuk unit', 'masuk hp', 'tambah unit', 'tambah servis', 'servis masuk', 'servis baru', 'unit baru', 'terima unit', 'input unit', 'input servis']
    return any(p in text_lower for p in pola_kata)

def ekstrak_data_unit_ai(user_text: str) -> dict:
    if '|' in user_text:
        teks_bersih = user_text
        for pfx in ['/masuk', '/tambah', '/servis', '/unit']:
            if teks_bersih.lower().startswith(pfx):
                teks_bersih = teks_bersih[len(pfx):].strip()
        parts = [p.strip() for p in teks_bersih.split('|')]
        if len(parts) >= 2:
            def c_num(s):
                return "".join(filter(str.isdigit, str(s)))
            est_val = 0
            if len(parts) > 2 and parts[2]:
                try: est_val = int(c_num(parts[2]))
                except Exception: est_val = 0
            return {
                "is_valid": True,
                "device": parts[0] or "Unit tidak diketahui",
                "kerusakan": parts[1] or "Cek & Analisa",
                "estimasi": est_val,
                "nama": parts[3] if len(parts) > 3 and parts[3] else "Pelanggan",
                "wa": c_num(parts[4]) if len(parts) > 4 and parts[4] else "-",
                "teknisi": parts[5] if len(parts) > 5 and parts[5] else "Teknisi SF",
                "tindakan": "Cek & Analisa"
            }
            
    prompt = f"""Tugas: Kamu adalah Asisten AI Sukabumi Flasher.
Analisa apakah pesan berikut adalah instruksi untuk MEMASUKKAN / MENAMBAHKAN UNIT SERVIS BARU ke bengkel, atau sekadar pertanyaan/obrolan biasa.
Pesan Pengguna: "{user_text}"

Jika pesan ini adalah perintah/informasi penambahan unit servis baru, balas HANYA dengan JSON valid format:
{{
  "is_valid": true,
  "device": "Merek dan Tipe HP (contoh: Oppo A5s)",
  "kerusakan": "Keluhan / Kerusakan (contoh: Ganti Kaca LCD)",
  "estimasi": angka biaya dalam integer tanpa titik/koma (contoh: 250000, default 0 jika tidak dicantumkan),
  "nama": "Nama Pelanggan (contoh: Kang Dani, default 'Pelanggan')",
  "wa": "Nomor WA angka saja (contoh: 0812345678, default '-')",
  "teknisi": "Nama Teknisi (contoh: Asep, default 'Teknisi SF')",
  "tindakan": "Tindakan perbaikan awal (contoh: Cek & ganti LCD)"
}}

Jika pesan bukan untuk menambah unit baru (misal hanya tanya status atau ngobrol), balas HANYA dengan JSON:
{{"is_valid": false}}"""

    with AI_LOCK:
        raw_text = "{}"
        try:
            if 'client_gemini' in globals() and client_gemini:
                resp = client_gemini.models.generate_content(model='gemini-flash-latest', contents=prompt)
                raw_text = resp.text.strip().replace('```json', '').replace('```', '').strip()
        except Exception:
            pass
            
        if raw_text == "{}" or not raw_text:
            try:
                import requests
                resp_ollama = requests.post("http://localhost:11434/api/generate", 
                                          json={"model": "qwen2.5:1.5b", "prompt": prompt, "format": "json", "stream": False}, 
                                          timeout=45)
                raw_text = resp_ollama.json().get('response', '{}')
            except Exception:
                pass
                
        try:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
            
    return {"is_valid": False}

async def cek_proses_tambah_unit_telegram(update: Update) -> bool:
    user_id = update.effective_user.id
    user_text = update.message.text or ""
    
    if user_id not in ALLOWED_TELEGRAM_IDS:
        return False
        
    if deteksi_is_tambah_unit(user_text):
        msg_tunggu = await update.message.reply_text("🤖 <i>Sedang membaca dan menyusun data unit servis baru...</i>", parse_mode='HTML')
        data_ai = ekstrak_data_unit_ai(user_text)
        
        if data_ai and data_ai.get("is_valid"):
            token_id = secrets.token_urlsafe(12)
            unit_data = {
                "nama": str(data_ai.get("nama", "Pelanggan")),
                "device": str(data_ai.get("device") or "Unit tidak diketahui"),
                "kerusakan": str(data_ai.get("kerusakan", "-")),
                "estimasi": int(data_ai.get("estimasi", 0)),
                "wa": str(data_ai.get("wa", "-")),
                "tindakan": str(data_ai.get("tindakan", "Cek & Analisa")),
                "teknisi": str(data_ai.get("teknisi", "Teknisi SF"))
            }
            with PENDING_LOCK:
                now_ts = time.time()
                expired_tokens = [
                    key for key, pending in PENDING_UNITS.items()
                    if now_ts - pending.get('created_at', 0) > 900
                ]
                for expired_token in expired_tokens:
                    PENDING_UNITS.pop(expired_token, None)
                PENDING_UNITS[token_id] = {
                    'owner_id': user_id,
                    'created_at': now_ts,
                    'data': unit_data,
                }
                
            teks_konfirmasi = (
                f"🤖 <b>KONFIRMASI INPUT SERVIS BARU</b>\n"
                f"----------------------------------\n"
                f"📱 <b>Device:</b> {unit_data['device']}\n"
                f"👤 <b>Pelanggan:</b> {unit_data['nama']}\n"
                f"📞 <b>No. WA:</b> {unit_data['wa']}\n"
                f"🔧 <b>Kerusakan:</b> {unit_data['kerusakan']}\n"
                f"👨‍🔧 <b>Teknisi:</b> {unit_data['teknisi']}\n"
                f"💰 <b>Estimasi:</b> Rp {unit_data['estimasi']:,}\n"
                f"----------------------------------\n"
                f"<i>Apakah data di atas sudah pas bro? Klik tombol di bawah ini:</i>"
            ).replace(',', '.')
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Simpan ke Dashboard", callback_data=f"unit_simpan_{token_id}"),
                    InlineKeyboardButton("❌ Batal", callback_data=f"unit_batal_{token_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await msg_tunggu.delete()
            except Exception:
                pass
            await update.message.reply_text(teks_konfirmasi, parse_mode='HTML', reply_markup=reply_markup)
            return True
        else:
            try:
                await msg_tunggu.delete()
            except Exception:
                pass
    return False

async def handle_callback_konfirmasi_unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    if user_id not in ALLOWED_TELEGRAM_IDS:
        await query.answer('Akses ditolak.', show_alert=True)
        return

    data_cb = str(query.data or '').split('_', 2)
    if len(data_cb) != 3 or data_cb[1] not in {'simpan', 'batal'}:
        await query.answer('Permintaan tidak valid.', show_alert=True)
        return
    action, token_id = data_cb[1], data_cb[2]

    with PENDING_LOCK:
        pending = PENDING_UNITS.get(token_id)
        if pending and time.time() - pending.get('created_at', 0) > 900:
            PENDING_UNITS.pop(token_id, None)
            pending = None
        elif pending and pending.get('owner_id') == user_id:
            pending = PENDING_UNITS.pop(token_id)
        elif pending:
            pending = 'wrong_owner'

    if pending == 'wrong_owner':
        await query.answer('Konfirmasi ini milik pengguna lain.', show_alert=True)
        return
    await query.answer()
    if not pending:
        await query.edit_message_text(
            '<b>Sesi konfirmasi sudah kedaluwarsa atau unit sudah diproses.</b>',
            parse_mode='HTML',
        )
        return

    unit_data = pending['data']
    if action == 'batal':
        await query.edit_message_text('<b>Input unit servis dibatalkan.</b>', parse_mode='HTML')
        return

    berhasil = ai_tambah_servis(**unit_data)
    if not berhasil:
        await query.edit_message_text(
            '<b>Unit gagal disimpan. Silakan kirim ulang perintah input.</b>',
            parse_mode='HTML',
        )
        return

    waktu_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    teks_sukses = (
        '<b>UNIT BERHASIL DISIMPAN KE DASHBOARD</b>\n'
        '----------------------------------\n'
        f"<b>Device:</b> {unit_data['device']}\n"
        f"<b>Pelanggan:</b> {unit_data['nama']}\n"
        f"<b>No. WA:</b> {unit_data['wa']}\n"
        f"<b>Kerusakan:</b> {unit_data['kerusakan']}\n"
        f"<b>Teknisi:</b> {unit_data['teknisi']}\n"
        f"<b>Estimasi:</b> Rp {unit_data['estimasi']:,}\n"
        f"<b>Waktu:</b> {waktu_str}\n"
        '----------------------------------\n'
        '<i>Status unit: <b>Analisa</b>.</i>'
    ).replace(',', '.')
    await query.edit_message_text(teks_sukses, parse_mode='HTML')

def ai_cek_laba():
    """Fungsi untuk cek total laba kotor & bersih hari ini (Powered by AIS Engine)"""
    try:
        data = AISKalkulator.hitung_laba_hari_ini()
        laba_kotor = data['laba_kotor']
        tambahan = data['tambahan']
        beban = data['beban']
        laba_bersih = data['laba_bersih']
        
        return (f"📊 <b>REKAP KEUANGAN HARI INI</b>\n"
                f"----------------------------------\n"
                f"💰 Laba Kotor (Servis): Rp {laba_kotor:,.0f}\n"
                f"⚖️ Transaksi Lain: Rp {tambahan:,.0f}\n"
                f"📉 Total Beban Toko: Rp {beban:,.0f}\n"
                f"----------------------------------\n"
                f"✅ <b>LABA BERSIH: Rp {laba_bersih:,.0f}</b>")
    except Exception as e:
        return "Gagal mengecek laba karena sistem sedang tidak tersedia."

def ai_cek_modal():
    """Fungsi hitung modal part (Siklus Berjalan) - Powered by AIS Engine"""
    try:
        data = AISKalkulator.hitung_laba_hari_ini()
        # Kita bisa tambahkan logika khusus modal di engine nanti jika perlu
        # Untuk sekarang kita ambil dari servis langsung di sini atau pindah ke engine
        with db_session() as conn:
            res = conn.execute("SELECT SUM(modal_part) as total FROM servis WHERE status='Cash'").fetchone()
            modal = res['total'] or 0
        
        return f"📦 <b>TOTAL MODAL PART (SIKLUS BERJALAN)</b>\n--------------------------\nRp {modal:,.0f}"
    except Exception as e:
        return "Gagal mengecek modal karena sistem sedang tidak tersedia."

def ai_cek_status_pelanggan(wa_query, device_query=None):
    """Fungsi CS: Harus cocok WA DAN Merk HP biar Super Aman"""
    try:
        # Bersihkan input WA
        wa_clean = "".join(filter(str.isdigit, str(wa_query)))
        
        if len(wa_clean) < 5:
            return "Mohon masukkan Nomor WA Kakak yang terdaftar ya Kak. 😊"
        
        if not device_query or len(device_query) < 2:
            return "Terima kasih Kak. Untuk verifikasi data, mohon sebutkan juga <b>Merk/Tipe HP</b> yang Kakak servis ya? 😊"

        with db_session() as conn:
            # Cari yang WA-nya mirip DAN Device-nya mirip
            search_wa = f"%{wa_clean}%"
            search_dev = f"%{device_query}%"
            query = 'SELECT * FROM servis WHERE no_wa LIKE %s AND device LIKE %s ORDER BY id DESC LIMIT 1'
            res = conn.execute(query, (search_wa, search_dev)).fetchone()
        
        if not res:
            return "Maaf Kak, data dengan Nama/WA tersebut belum ditemukan di sistem kami. Pastikan penulisan sudah benar ya Kak. 😊"
        
        status = res['status'] or 'Proses'
        device = res['device'] or device_query or '-'
        kerusakan = res['analisa_kerusakan'] or '-'
        perbaikan = res['tindakan_perbaikan'] or '-'
        
        teks = (f"👋 <b>Halo Kak {res['nama_user']}!</b>\n\n"
                f"Berikut update status servis hp Kakak:\n"
                f"----------------------------------\n"
                f"📱 <b>Device:</b> {device}\n"
                f"🔧 <b>Kerusakan:</b> {kerusakan}\n"
                f"🛠️ <b>Perbaikan:</b> {perbaikan}\n"
                f"📊 <b>STATUS SAAT INI:</b> <b>{status.upper()}</b>\n"
                f"----------------------------------\n")
        
        if status.lower() == 'cash' or status.lower() == 'done':
            teks += "✅ HP Kakak sudah selesai! Silakan bisa diambil ke toko Sukabumi Flasher ya Kak. 🏃‍♂️💨"
        elif status.lower() == 'wait part':
            teks += "⏳ Sedang menunggu ketersediaan sparepart Kak. Mohon ditunggu ya, nanti kami update lagi. 🙏"
        else:
            teks += "👨‍🔧 Teknisi kami sedang mengerjakan unit Kakak. Mohon doanya biar cepat sembuh hp-nya! 💪"
            
        return teks
    except Exception as e:
        return "Maaf, sistem sedang tidak tersedia. Silakan coba lagi."

def ai_rekap_harian(mode="total"):
    """Fungsi rekap: bisa 'hari_ini' atau 'total'"""
    try:
        with db_session() as conn:
            if mode == "hari_ini":
                tgl_skrg = datetime.now().strftime("%Y-%m-%d")
                query = "SELECT LOWER(TRIM(status)) as stts, COUNT(*) as jumlah FROM servis WHERE tanggal_masuk = %s GROUP BY stts"
                res = conn.execute(query, (tgl_skrg,)).fetchall()
                judul = f"📊 <b>REKAP UNIT MASUK HARI INI ({tgl_skrg})</b>"
                nb = "<i>NB: Data ini sesuai dengan Tabel Dashboard Hari Ini.</i>"
            else:
                query = "SELECT LOWER(TRIM(status)) as stts, COUNT(*) as jumlah FROM servis GROUP BY stts"
                res = conn.execute(query).fetchall()
                judul = "📊 <b>TOTAL REKAP UNIT (SEMUA DATA)</b>"
                nb = "<i>NB: Data ini sesuai dengan Diagram Batang di Dashboard kamu.</i>"
        
        if not res: return f"{judul}\n--------------------------\nBelum ada data unit Bro."
        
        teks = f"{judul}\n--------------------------\n"
        for row in res:
            teks += f"• {row['stts'].title()}: {row['jumlah']} unit\n"
        
        teks += f"\n{nb}"
        return teks
    except Exception as e:
        return "Gagal membuat rekap karena sistem sedang tidak tersedia."

# --- BOT AGEN SPAREPART ---
def ai_cek_sparepart(user_text):
    prompt = f"""Tugas: Kamu adalah Agen Sparepart Sukabumi Flasher.
    1. Ekstrak nama SPAREPART (misal: LCD, Batre, Baterai, Backdoor) DAN tipe HP-nya. JANGAN ubah ejaan aslinya (misal user ketik 'batre' jangan diubah jadi 'baterai').
    2. Gabungkan jadi query pencarian (misal: "LCD iPhone 14").
    3. Jika user tanya 'stok' atau 'cek', set task="cari_lokal".
    4. Jika user tanya 'harga online', set task="cari_online".
    
    User: "{user_text}"
    Balas HANYA dengan JSON: {{"task":"cari_lokal", "query":"LCD iPhone 14"}}"""
    
    try:
        with AI_LOCK:
            try:
                # Coba Gemini 1.5 Flash
                response = client_gemini.models.generate_content(model='gemini-flash-latest', contents=prompt)
                raw_text = response.text.strip().replace('```json', '').replace('```', '')
            except:
                # Fallback ke Ollama lokal
                import requests
                resp_ollama = requests.post("http://localhost:11434/api/generate", 
                                          json={"model": "qwen2.5:1.5b", "prompt": prompt, "format": "json", "stream": False}, 
                                          timeout=60)
                raw_text = resp_ollama.json().get('response', '{}')
            
            data_ai = json.loads(raw_text)
        
        query = data_ai.get('query', '')
        if data_ai['task'] == "cari_lokal":
            words = query.split()
            if not words:
                res = []
            else:
                where_clauses = []
                params = []
                for word in words:
                    where_clauses.append(
                        "(kategori LIKE %s OR merek LIKE %s OR jenis_barang LIKE %s OR jenis_device LIKE %s)"
                    )
                    params.extend([f"%{word}%"] * 4)

                sql = f"SELECT * FROM data_sparepart WHERE {' AND '.join(where_clauses)} LIMIT 10"
                with db_session() as db:
                    res = db.execute(sql, tuple(params)).fetchall()
            
            if res:
                teks = f"📦 **STOK GUDANG LOKAL (SF):**\n"
                for r in res: teks += f"• {r['merek']} {r['jenis_barang']}: {r['qty']} pcs | Rp {r['harga_jual']:,}\n"
                return teks
            else:
                # Jika lokal kosong, otomatis tawarkan riset online
                info_kosong = f"Maaf Bos, stok <b>{query}</b> kosong di gudang lokal. ❌\n\n🔎 *Otomatis memulai riset pasar online...*\n"
                # Prompt riset ANTI-KILOAN & ANTI-NGASAL
                prompt_harga = f"""Tugas: Kamu Teknisi HP Sukabumi Flasher. Cari HARGA SATUAN (Pcs) {query} di Indonesia.
                - JANGAN GUNAKAN SATUAN BERAT (Kg/Gram)! INI BUKAN RONGSOK!
                - WAJIB BERIKAN HARGA PER PCS (SATUAN).
                - HARGA BIASANYA DI KISARAN Rp 200.000 s/d Rp 3.000.000 (Tergantung Kualitas).
                WAJIB Balas HANYA list Merk & Harga per pcs.
                Format:
                • {query} Merk GX: Rp [Harga Satuan]
                • {query} Merk OLED: Rp [Harga Satuan]
                • {query} Merk Incell: Rp [Harga Satuan]"""
                
                with AI_LOCK:
                    try:
                        # Coba Gemini 1.5 Flash
                        res_harga = client_gemini.models.generate_content(model='gemini-flash-latest', contents=prompt_harga)
                        detail_harga = res_harga.text
                    except:
                        # Fallback ke Ollama (Laptop kamu) buat riset
                        import requests
                        try:
                            resp_ollama = requests.post("http://localhost:11434/api/generate", 
                                                      json={"model": "qwen2.5:1.5b", "prompt": prompt_harga, "stream": False}, 
                                                      timeout=60)
                            detail_harga = resp_ollama.json().get('response', 'Gagal riset harga, coba sesaat lagi Bos.')
                        except:
                            detail_harga = f"Maaf Bos, server lagi sibuk. Estimasi harga {query} saat ini sekitar Rp 250rb - 700rb tergantung kualitas."
                
                return f"{info_kosong}\n🌐 **HASIL RISET PASAR ONLINE:**\n\n{detail_harga}"
        else:
            # Prompt riset ANTI-KILOAN & ANTI-NGASAL
            prompt_harga = f"""Tugas: Kamu Teknisi HP Sukabumi Flasher. Cari HARGA SATUAN (Pcs) {query} di Indonesia.
            - JANGAN GUNAKAN SATUAN BERAT (Kg/Gram)! INI BUKAN RONGSOK!
            - WAJIB BERIKAN HARGA PER PCS (SATUAN).
            - HARGA BIASANYA DI KISARAN Rp 200.000 s/d Rp 3.000.000 (Tergantung Kualitas).
            WAJIB Balas HANYA list Merk & Harga per pcs.
            Format:
            • {query} Merk GX: Rp [Harga Satuan]
            • {query} Merk OLED: Rp [Harga Satuan]
            • {query} Merk Incell: Rp [Harga Satuan]"""
            
            with AI_LOCK:
                try:
                    # Coba Gemini 1.5 Flash
                    res_harga = client_gemini.models.generate_content(model='gemini-flash-latest', contents=prompt_harga)
                    detail_harga = res_harga.text
                except:
                    import requests
                    try:
                        resp_ollama = requests.post("http://localhost:11434/api/generate", 
                                                  json={"model": "qwen2.5:1.5b", "prompt": prompt_harga, "stream": False}, 
                                                  timeout=60)
                        detail_harga = resp_ollama.json().get('response', f"Estimasi harga {query} Rp 150rb - 500rb.")
                    except:
                        detail_harga = f"Maaf Bos, server lagi sibuk. Estimasi harga {query} sekitar Rp 200rb - 600rb."
            
            return f"🌐 **HASIL RISET PASAR ONLINE:**\n\n{detail_harga}\n\n<i>NB: Data ini adalah estimasi AI berdasarkan tren pasar.</i>"
    except Exception as e:
        print(f"[ERROR SPAREPART]: {str(e)}")
        return "🤖 Maaf Bos, Agen Sparepart lagi pusing, coba tanya lagi ya."

async def handle_message_manajer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if user_id not in ALLOWED_TELEGRAM_IDS: return
    if await cek_proses_tambah_unit_telegram(update): return

    try:
        # Gunakan AIS Engine untuk logika respons
        jawaban = AISBotLogic.proses_pesan_manajer(user_text)
        await update.message.reply_text(jawaban, parse_mode='HTML')
    except Exception as e:
        print(f"[ERROR MANAJER]: {str(e)}")
        await update.message.reply_text("Bot manajer sedang tidak tersedia.")

async def handle_message_akuntan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if user_id not in ALLOWED_TELEGRAM_IDS: return
    if await cek_proses_tambah_unit_telegram(update): return

    try:
        # Gunakan AIS Engine untuk logika respons
        jawaban = AISBotLogic.proses_pesan_akuntan(user_text)
        await update.message.reply_text(jawaban, parse_mode='HTML')
    except Exception as e:
        print(f"[ERROR AKUNTAN]: {str(e)}")
        await update.message.reply_text("Bot akuntan sedang tidak tersedia.")

async def handle_message_cs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_TELEGRAM_IDS:
        return
    if await cek_proses_tambah_unit_telegram(update): return
    user_text = update.message.text
    try:
        prompt = f"""Role: CS SF. 
        Tugas: Ekstrak data dari chat user.
        Ambil Nomor WA (angka saja) DAN Merk/Tipe HP.
        Balas HANYA dengan JSON: {{"task":"cek_status", "wa":"08xxx", "device":"Samsung S25"}}
        User: \"{user_text}\" """
        
        with AI_LOCK:
            try:
                # Coba pake Gemini 1.5 Flash (Lebih lega kuotanya)
                response = client_gemini.models.generate_content(model='gemini-flash-latest', contents=prompt)
                raw_text = response.text.strip().replace('```json', '').replace('```', '')
            except:
                # Kalau Gemini limit, pake Ollama lokal (Laptop kamu)
                import requests
                resp_ollama = requests.post("http://localhost:11434/api/generate", 
                                          json={"model": "qwen2.5:1.5b", "prompt": prompt, "format": "json", "stream": False}, 
                                          timeout=60)
                raw_text = resp_ollama.json().get('response', '{}')
            
            data_ai = json.loads(raw_text)
        
        task = str(data_ai.get('task', '')).lower()
        if task == "cek_status":
            if data_ai.get('wa'): context.user_data['wa'] = data_ai.get('wa')
            if data_ai.get('device'): context.user_data['device'] = data_ai.get('device')
            
            wa = context.user_data.get('wa', '')
            device = context.user_data.get('device', '')
            
            if not wa or not device:
                await update.message.reply_text("Halo Kak! Bisa dibantu WA dan Tipe HP-nya untuk verifikasi? 😊")
            else:
                hasil = ai_cek_status_pelanggan(wa, device)
                if "STATUS SAAT INI" in hasil: context.user_data.clear()
                await update.message.reply_text(hasil, parse_mode='HTML')
    except Exception as e:
        print(f"[ERROR CS]: {str(e)}")
        await update.message.reply_text("CS sedang istirahat. 😊")

async def handle_message_sparepart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_TELEGRAM_IDS:
        return
    if await cek_proses_tambah_unit_telegram(update): return
    await update.message.reply_text("🔎 Sedang mengecek data sparepart... Mohon tunggu ya Bos.")
    jawaban = ai_cek_sparepart(update.message.text)
    await update.message.reply_text(jawaban, parse_mode='HTML')

def run_bot(token, handler_func, name):
    if not ALLOWED_TELEGRAM_IDS:
        print(f'[AI] Whitelist kosong. Bot {name} dinonaktifkan (fail-close).')
        return
    if not token:
        print(f"[AI] Token untuk Bot {name} belum diatur. Bot {name} dinonaktifkan.")
        return
    print(f"[AI] Memulai Bot {name}...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_bot = Application.builder().token(token).build()
    app_bot.add_handler(CallbackQueryHandler(handle_callback_konfirmasi_unit, pattern="^unit_"))
    app_bot.add_handler(MessageHandler(filters.TEXT, handler_func))
    app_bot.run_polling(poll_interval=1.0)


def main():
    print("=========================================")
    print("      MEMULAI LAYANAN BOT TELEGRAM       ")
    print("=========================================")
    
    TOKEN_MANAJER = os.getenv('BOT_TOKEN_MANAJER')
    TOKEN_AKUNTAN = os.getenv('BOT_TOKEN_AKUNTAN')
    TOKEN_CS = os.getenv('BOT_TOKEN_CS')
    TOKEN_SPAREPART = os.getenv('BOT_TOKEN_SPAREPART')
    
    threads = []
    
    # threads.append(threading.Thread(target=run_bot, args=(TOKEN_MANAJER, handle_message_manajer, "MANAJER"), daemon=True))
    threads.append(threading.Thread(target=run_bot, args=(TOKEN_AKUNTAN, handle_message_akuntan, "AKUNTAN"), daemon=True))
    threads.append(threading.Thread(target=run_bot, args=(TOKEN_CS, handle_message_cs, "CS"), daemon=True))
    threads.append(threading.Thread(target=run_bot, args=(TOKEN_SPAREPART, handle_message_sparepart, "SPAREPART"), daemon=True))
    
    for t in threads:
        t.start()
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Bot dihentikan.")

if __name__ == "__main__":
    main()
