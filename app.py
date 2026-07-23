

# ==============================================================================
# 1 & 2. INIT, CONFIG & MIDDLEWARE
# ==============================================================================

import pymysql
import time
import os
import requests
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dateutil.relativedelta import relativedelta
from html2image import Html2Image
import threading
import shutil
import json
from google import genai
from google.genai import types
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import asyncio
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- IMPORT AIS ENGINE (Mesin Utama) ---
from engine.kalkulator import AISKalkulator
from engine.operasional import AISOperasional
from engine.bot_logic import AISBotLogic
from engine.db_tools import query_sqlite, query_mysql, SCHEMA_PROMPT

# --- CONFIG AI & TELEGRAM (Diambil dari Brankas .env) ---
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

load_env()

TOKEN_MANAJER = os.getenv("TOKEN_MANAJER")
TOKEN_AKUNTAN = os.getenv("TOKEN_AKUNTAN")
TOKEN_CS = os.getenv("TOKEN_CS")
TOKEN_SPAREPART = os.getenv("TOKEN_SPAREPART")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Inisialisasi Gemini Client Baru
if GEMINI_API_KEY:
    try:
        client_gemini = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini Client: {e}")
        client_gemini = None
else:
    client_gemini = None
    print("Warning: GOOGLE_API_KEY is not set. AI features will fallback to local Ollama if available.")
_raw_ids = os.getenv("ALLOWED_TELEGRAM_IDS", os.getenv("NOTIF_PRIVATE_ID", "1646882270"))
ALLOWED_TELEGRAM_IDS = [int(x.strip()) for x in _raw_ids.split(',') if x.strip().isdigit()] # ID Telegram Bos Sukabumi Flasher
AI_LOCK = threading.Lock() # Biar bot ngga tabrakan manggil Gemini

# Pastikan folder output ada
output_dir = os.path.join(os.getcwd(), 'static', 'nota_digital')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- AUTO BACKUP DATABASE (Per 3 Hari) ---
def auto_backup_worker():
    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    db_file = os.path.join(os.getcwd(), 'sukabumi_flasher.db')
    
    while True:
        try:
            if os.path.exists(db_file):
                existing_backups = [f for f in os.listdir(backup_dir) if f.startswith('backup_db_') and f.endswith('.db')]
                
                needs_backup = False
                if not existing_backups:
                    needs_backup = True
                else:
                    existing_backups.sort(reverse=True)
                    latest_backup_path = os.path.join(backup_dir, existing_backups[0])
                    
                    file_time = os.path.getmtime(latest_backup_path)
                    current_time = time.time()
                    
                    # 3 hari = 3 * 24 * 60 * 60 detik = 259200 detik
                    if (current_time - file_time) >= 259200:
                        needs_backup = True
                        
                if needs_backup:
                    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    dest_file = os.path.join(backup_dir, f'backup_db_{now_str}.db')
                    shutil.copy2(db_file, dest_file)
                    print(f"[AUTO BACKUP] Database berhasil di-backup ke: {dest_file}")
                    
                    try:
                        TOKEN = os.getenv('BOT_TOKEN_LAPORAN')
                        pesan = f"✅ *AUTO BACKUP BERHASIL*\nDatabase SQLite telah dicadangkan secara otomatis pada `{now_str}`."
                        penerima_ids = os.getenv("NOTIF_PRIVATE_ID", "").split(',')
                        for chat_id in penerima_ids:
                            if chat_id.strip():
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                              data={'chat_id': chat_id.strip(), 'text': pesan, 'parse_mode': 'Markdown'})
                    except Exception:
                        pass
        except Exception as e:
            print(f"[AUTO BACKUP ERROR] Gagal melakukan backup otomatis: {e}")
            
        # Tidur 4 jam sebelum mengecek kembali
        time.sleep(4 * 60 * 60)

threading.Thread(target=auto_backup_worker, daemon=True).start()

# Mesin 1: Khusus Nota Garansi (Lebar 850px, Tinggi 850px untuk 2 Kolom)
hti_garansi = Html2Image(
    output_path=output_dir,
    size=(1024, 1536),
    custom_flags=['--headless=new', '--no-sandbox', '--disable-gpu', '--window-size=1024,1536', '--force-device-scale-factor=2', '--default-background-color=ffffffff']
)

# Mesin 2: Khusus Nota Penerimaan (Desain Baru Lebih Panjang 880px)
hti_penerimaan = Html2Image(
    output_path=output_dir,
    custom_flags=['--headless=new', '--no-sandbox', '--disable-gpu', '--window-size=1024,1536', '--force-device-scale-factor=2', '--default-background-color=ffffffff']
)

# Mesin 3: Khusus Milestone (Ukuran 1000x800)
hti_milestone = Html2Image(
    output_path=output_dir,
    custom_flags=[
        '--headless=new', 
        '--no-sandbox', 
        '--disable-gpu', 
        '--remote-debugging-port=9222',
        '--window-size=1000,800', 
        '--disable-web-security', 
        '--force-device-scale-factor=2', 
        '--default-background-color=ffffffff'
    ]
)

# --- KONFIGURASI UPLOAD PEMBAYARAN ---
UPLOAD_FOLDER = os.path.join('static', 'bukti_bayar')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

UPLOAD_FOLDER_PROFIL = os.path.join('static', 'uploads', 'profiles')
if not os.path.exists(UPLOAD_FOLDER_PROFIL):
    os.makedirs(UPLOAD_FOLDER_PROFIL)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_PROFIL'] = UPLOAD_FOLDER_PROFIL
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    print("WARNING: FLASK_SECRET_KEY is not set in .env! Generating a random one for this session.")
    app.secret_key = os.urandom(24).hex()
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Initialize Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://"
)

from flask import g
from engine.database import get_db, get_db_connection, db_session

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

@app.context_processor
def inject_teknisi_list():
    try:
        conn = get_db()
        rows = conn.execute("SELECT username FROM users WHERE role='teknisi' ORDER BY username ASC").fetchall()
        tech_list = [r['username'].title() for r in rows if r['username']]
    except Exception:
        tech_list = []
    return dict(daftar_teknisi=tech_list)

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS beban (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategori TEXT, 
            nama_beban TEXT UNIQUE, 
            nilai INTEGER
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS kas_utama (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            saldo_awal INTEGER DEFAULT 0,
            saldo_akhir INTEGER DEFAULT 0,
            total_laba_bersih INTEGER DEFAULT 0
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS transaksi_tambahan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            uraian TEXT,
            jenis TEXT, -- 'Masuk' atau 'Keluar'
            nominal INTEGER
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS arsip_servis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal_masuk TEXT,
            tanggal_keluar TEXT,
            nama_user TEXT,
            wa TEXT,
            device TEXT,
            kerusakan TEXT,
            tindakan TEXT,
            modal_part INTEGER,
            modal_jasa INTEGER,
            harga_jual INTEGER,
            laba_kotor INTEGER,
            teknisi TEXT,
            kelengkapan TEXT,
            kondisi_fisik TEXT
        )
    ''')
    for tbl in ['servis', 'arsip_servis']:
        try:
            cols = [col[1] for col in conn.execute(f'PRAGMA table_info({tbl})').fetchall()]
            if 'kelengkapan' not in cols: conn.execute(f'ALTER TABLE {tbl} ADD COLUMN kelengkapan TEXT;')
            if 'kondisi_fisik' not in cols: conn.execute(f'ALTER TABLE {tbl} ADD COLUMN kondisi_fisik TEXT;')
        except Exception:
            pass

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT, -- 'admin', 'teknisi', 'kasir', 'custom'
            permissions TEXT DEFAULT '', -- Contoh: 'keuangan,sparepart,servis,tutup_buku,users'
            foto_profil TEXT
        )
    ''')

    # Buat admin default kalau belum ada user sama sekali
    admin_exists = conn.execute('SELECT * FROM users LIMIT 1').fetchone()
    if not admin_exists:
        from werkzeug.security import generate_password_hash
        conn.execute('INSERT INTO users (username, password, role, permissions) VALUES (?, ?, ?, ?)', 
                     ('admin', generate_password_hash('admin123'), 'admin', 'keuangan,sparepart,servis,tutup_buku,users'))

    conn.execute('''
        CREATE TABLE IF NOT EXISTS pembayaran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servis_id INTEGER,
            metode TEXT, -- 'QRIS', 'Transfer', 'Tunai'
            nominal INTEGER,
            status TEXT DEFAULT 'Pending', -- 'Pending', 'Sukses', 'Gagal'
            bukti_bayar TEXT, -- Path file gambar bukti transfer
            tanggal TEXT,
            FOREIGN KEY (servis_id) REFERENCES servis (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("[INFO] Database initialized.")

# --- ASISTEN TELEGRAM: NOTIFIKASI UNIT BARU ---
def kirim_notif_unit_baru(device, analisa, tindakan, kelengkapan="", kondisi_fisik=""):
    TOKEN = os.getenv('BOT_TOKEN_LAPORAN', '8670230633:AAF91XoMmWQtEM2yN3nF-sLwpTJPJ-XqEiY')
    
    # Ambil ID Private dari .env (khusus untuk notif masuk & cash)
    penerima_ids = os.getenv("NOTIF_PRIVATE_ID", "1516667237,1646882270").split(',')
    # Hapus string kosong jika ada
    penerima_ids = [cid.strip() for cid in penerima_ids if cid.strip()]
    
    # Bersihkan data kalau kosong
    analisa = analisa if analisa else "-"
    tindakan = tindakan if tindakan else "-"
    
    chk_str = ""
    if kelengkapan and kelengkapan != '-': chk_str += f"\n📦 *Kelengkapan*: {kelengkapan}"
    if kondisi_fisik and kondisi_fisik != '-': chk_str += f"\n⚠️ *Kondisi Fisik*: {kondisi_fisik}"
    
    pesan = f"🆕 *UNIT BARU MASUK!*\n\n📱 *Device*: {device}\n🔍 *Analisa*: {analisa}{chk_str}\n🛠️ *Tindakan*: {tindakan}\n\nSemangat pengerjaannya tim! 💪🔥"
    
    def send_to_all():
        for chat_id in penerima_ids:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                payload = {'chat_id': chat_id.strip(), 'text': pesan, 'parse_mode': 'Markdown'}
                resp = requests.post(url, data=payload)
                print(f"[TELEGRAM] Notif ke {chat_id.strip()}: {resp.status_code}")
            except Exception as e:
                print(f"[TELEGRAM ERROR] Gagal kirim ke {chat_id}: {e}")

    # Jalankan di background biar ngga lambat
    threading.Thread(target=send_to_all, daemon=True).start()

def kirim_notif_kas_masuk(device, nama, harga_jual, laba_kotor, teknisi):
    TOKEN = os.getenv('BOT_TOKEN_LAPORAN', '8670230633:AAF91XoMmWQtEM2yN3nF-sLwpTJPJ-XqEiY')
    # Gunakan NOTIF_PRIVATE_ID untuk laporan cash
    penerima_ids = os.getenv("NOTIF_PRIVATE_ID", "1516667237,1646882270").split(',')
    penerima_ids = [cid.strip() for cid in penerima_ids if cid.strip()]
    
    def format_rp(val):
        try:
            return f"Rp {int(val):,}".replace(',', '.')
        except:
            return f"Rp {val}"
            
    pesan = f"✅ *KAS MASUK (UNIT SELESAI)*\n\n📱 *Device*: {device}\n👤 *Konsumen*: {nama}\n👨‍🔧 *Teknisi*: {teknisi}\n\n💰 *Harga Jual*: {format_rp(harga_jual)}\n📈 *Laba Kotor*: {format_rp(laba_kotor)}\n\nAlhamdulillah, nota berhasil ditutup! 🚀"
    
    def send_to_all():
        for chat_id in penerima_ids:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                payload = {'chat_id': chat_id.strip(), 'text': pesan, 'parse_mode': 'Markdown'}
                requests.post(url, data=payload)
            except Exception:
                pass

    threading.Thread(target=send_to_all, daemon=True).start()

# --- ASISTEN TELEGRAM: MILESTONE OTOMATIS ---
def cek_dan_kirim_milestone():
    """Fungsi otomatis cek apakah sudah tembus CTS/CTO/CTH hari ini"""
    print("[MILESTONE] Memulai pengecekan otomatis...")
    tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    
    try:
        # 1. Hitung Laba Kotor dari SEMUA yang statusnya 'Cash' di tabel utama (khusus yang sudah diisi modal)
        # (Karena yang siklus lalu sudah dipindah ke Arsip, jadi ini pasti laba siklus sekarang)
        laba_servis = conn.execute("SELECT SUM(\"Laba Kotor\") FROM servis WHERE Status='Cash' AND (COALESCE(\"Modal Part\", 0) > 0 OR COALESCE(\"Modal Jasa\", 0) > 0 OR COALESCE(\"Lain-lain\", 0) > 0)").fetchone()[0] or 0
        
        # 2. Hitung Laba/Rugi dari TRANSAKSI LAIN (Siklus sekarang)
        res_tambahan = conn.execute("SELECT SUM(CASE WHEN jenis='Masuk' THEN nominal ELSE -nominal END) FROM transaksi_tambahan WHERE uraian != 'MODAL KAS KECIL (LACI)'")
        laba_tambahan = res_tambahan.fetchone()[0] or 0
        
        # TOTAL LABA KOTOR (Gabungan)
        laba_kotor = laba_servis + laba_tambahan
        
        # Ambil Gaji & Ops
        gaji = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'gaji'").fetchone()[0] or 0
        ops = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'operasional'").fetchone()[0] or 0
        total_beban = gaji + ops
        
        print(f"[MILESTONE DEBUG] Servis: {laba_servis}, Tambahan: {laba_tambahan}, Total Laba: {laba_kotor}")
        print(f"[MILESTONE DEBUG] Target -> Gaji: {gaji}, Ops: {ops}, Total Beban: {total_beban}")
        
        # Ambil log hari ini
        logs = conn.execute("SELECT jenis FROM milestone_logs WHERE tanggal = ?", (tgl_hari_ini,)).fetchall()
        sudah_sent = [l['jenis'] for l in logs]
        print(f"[MILESTONE] Milestone yang sudah terkirim hari ini: {sudah_sent}")
        
        # Hitung jumlah transaksi Cash untuk mendeteksi penambahan
        jml_servis = conn.execute("SELECT COUNT(*) FROM servis WHERE Status='Cash'").fetchone()[0] or 0
        jml_tambahan = conn.execute("SELECT COUNT(*) FROM transaksi_tambahan WHERE jenis='Masuk' AND uraian != 'MODAL KAS KECIL (LACI)'").fetchone()[0] or 0
        total_cash_trx = jml_servis + jml_tambahan

        cth_count = 0
        last_trx_sent = 0
        for j in sudah_sent:
            if j == 'CTH':
                cth_count += 1
                # Fallback untuk CTH lama tanpa _trx_, anggap trx saat ini sebagai base supaya tidak spam
                if last_trx_sent == 0: last_trx_sent = total_cash_trx
            elif j.startswith('CTH_trx_'):
                cth_count += 1
                try:
                    t = int(j.split('_')[2])
                    if t > last_trx_sent: last_trx_sent = t
                except: pass

        # LOGIKA MILESTONE (HIERARKI: CTH > CTO > CTS)
        jenis_kirim = None
        pesan = ""
        status_text_override = None
        
        if total_beban > 0 and laba_kotor > total_beban:
            if cth_count == 0:
                jenis_kirim = f'CTH_trx_{total_cash_trx}'
                laba_bersih = laba_kotor - total_beban
                pesan = f"MILESTONE: CTH TERLAMPAUI!\n\nAlhamdulillah, toko sudah menghasilkan Laba Bersih Rp {laba_bersih:,.0f} hari ini!"
                status_text_override = "CTH! (LABA BERSIH)"
            elif total_cash_trx > last_trx_sent:
                cth_ke = cth_count + 1
                jenis_kirim = f'CTH_trx_{total_cash_trx}'
                laba_bersih = laba_kotor - total_beban
                pesan = f"MILESTONE: CTH {cth_ke} TERLAMPAUI!\n\nGas Terus! Laba Bersih saat ini mencapai Rp {laba_bersih:,.0f}!"
                status_text_override = f"CTH {cth_ke}! (LABA BERSIH)"
        
        if not jenis_kirim and cth_count == 0 and total_beban > 0 and laba_kotor >= total_beban:
            if 'CTO' not in sudah_sent:
                jenis_kirim = 'CTO'
                pesan = "MILESTONE: CTO TERLAMPAUI!\n\nGaji dan Biaya Operasional hari ini sudah AMAN!"
        
        if not jenis_kirim and cth_count == 0 and 'CTO' not in sudah_sent and gaji > 0 and laba_kotor >= gaji:
            if 'CTS' not in sudah_sent:
                jenis_kirim = 'CTS'
                pesan = "MILESTONE: CTS TERLAMPAUI!\n\nGaji karyawan hari ini sudah terpenuhi!"
        if jenis_kirim:
            nama_gambar = f"Milestone_{jenis_kirim}_{tgl_hari_ini}.png"
            
            # Itung persentase buat di gambar
            p_gaji = min(100, (laba_kotor / gaji * 100)) if gaji > 0 else 0
            p_ops = min(100, (max(0, laba_kotor - gaji) / ops * 100)) if ops > 0 else 0
            
            status_text = "OTW TARGET GAJI"
            status_class = "status-otw"
            if laba_kotor >= total_beban:
                status_text = status_text_override if status_text_override else ("CTH! (LABA BERSIH)" if laba_kotor > total_beban else "CTO! (BIAYA AMAN)")
                status_class = "status-cth" if laba_kotor > total_beban else "status-cto"
            elif laba_kotor >= gaji:
                status_text = "CTS! (GAJI AMAN)"
                status_class = "status-cts"

            def proses_milestone_bg(jk, p, ng, tgl, lk, gj, op, tb, lb, pg, po, st, sc):
                try:
                    print(f"[MILESTONE] Background: Memulai Kamera Mandiri...")
                    from html2image import Html2Image
                    hti_lokal = Html2Image(
                        output_path=os.path.join(os.getcwd(), 'static', 'nota_digital'),
                        custom_flags=['--headless=new', '--no-sandbox', '--disable-gpu', '--window-size=1000,800', '--disable-web-security', '--default-background-color=ffffffff']
                    )
                    
                    with app.app_context():
                        html_str = render_template('milestone_view.html', 
                                               laba_kotor=lk, gaji=gj, ops=op, 
                                               total_beban=tb, laba_bersih=lb,
                                               p_gaji=pg, p_ops=po, 
                                               status_text=st, status_class=sc)
                    
                    print(f"[MILESTONE] Background: Sedang memotret...")
                    hti_lokal.screenshot(html_str=html_str, save_as=ng)
                    
                    print(f"[MILESTONE] Background: Foto Selesai! Mengecek file...")
                    path_lengkap = os.path.join('static', 'nota_digital', ng)
                    time.sleep(2)
                    
                    if os.path.exists(path_lengkap):
                        print(f"[MILESTONE] Background: File OK. Mengirim ke Telegram...")
                        TOKEN_KIRIM = '8604967039:AAFbBMb5sMGulDDbGKMAvLsL4Q9uc_cTQvk'
                        CHAT_ID_KIRIM = '-1003742654600'
                        url_tele = f'https://api.telegram.org/bot{TOKEN_KIRIM}/sendPhoto'
                        
                        with open(path_lengkap, 'rb') as img_file:
                            payload = {'chat_id': CHAT_ID_KIRIM, 'caption': p, 'parse_mode': 'Markdown'}
                            files = {'photo': img_file}
                            r = requests.post(url_tele, data=payload, files=files, timeout=20)
                            print(f"[MILESTONE] Background: Telegram Berhasil (Status: {r.status_code})")
                            
                            if r.status_code == 200:
                                with db_session() as conn_thread:
                                    conn_thread.execute("INSERT INTO milestone_logs (tanggal, jenis) VALUES (?, ?)", (tgl, jk))
                                print(f"[MILESTONE] Laporan {jk} terkirim ke Telegram.")
                    else:
                        print(f"[MILESTONE] Background ERROR: File {ng} TIDAK DITEMUKAN!")
                except Exception as ex:
                    print(f"[MILESTONE THREAD ERROR] CRASH: {ex}")
            print(f"[MILESTONE] Mendeteksi Milestone Baru: {jenis_kirim}. Menjalankan background worker...")
            threading.Thread(target=proses_milestone_bg, args=(jenis_kirim, pesan, nama_gambar, tgl_hari_ini, laba_kotor, gaji, ops, total_beban, laba_bersih, p_gaji, p_ops, status_text, status_class), daemon=True).start()
        else:
            print("[MILESTONE] Belum ada milestone baru yang tercapai.")
            
    except Exception as e:
        print(f"[MILESTONE ERROR] Terjadi kesalahan: {e}")
    finally:
        conn.close()

LAPORAN_LOCK = threading.Lock()

def kirim_laporan_telegram(path_gambar, jenis="TUTUP"):
    with LAPORAN_LOCK:
        TOKEN = os.getenv('BOT_TOKEN_LAPORAN', '8670230633:AAF91XoMmWQtEM2yN3nF-sLwpTJPJ-XqEiY') 
        CHAT_ID = os.getenv('CHAT_ID_LAPORAN', '-1003724043513')
        
        if jenis == "TUTUP":
            pesan = (
                "🏢 *LAPORAN TUTUP BUKU SIKLUS 16.00*\n"
                "----------------------------------------\n"
                "Selamat sore Tim & Manajemen,\n\n"
                "Siklus operasional hari ini telah ditutup. Bersama ini kami lampirkan rekap otomatis Buku Kas & Alokasi Bagi Hasil (Aliran Kas) sebagai bentuk transparansi dan pertanggungjawaban.\n\n"
                "Terima kasih atas dedikasi dan kerja keras seluruh tim hari ini. Istirahat yang cukup dan tetap semangat! 💪\n"
                "----------------------------------------\n"
                "*SUKABUMI FLASHER*"
            )
        else:
            pesan = (
                "🌅 *LAPORAN BUKA BUKU SIKLUS BARU*\n"
                "----------------------------------------\n"
                "Siklus pembukuan yang baru telah resmi dimulai!\n\n"
                "Berikut adalah posisi Kas Aset dan Modal Kas Laci yang siap digunakan sebagai amunisi operasional kita selanjutnya.\n\n"
                "Mari kita mulai siklus ini dengan energi positif dan gaspol capai target berikutnya! 🚀\n"
                "----------------------------------------\n"
                "*SUKABUMI FLASHER*"
            )
        
        targets = [
            (TOKEN, CHAT_ID),
            ('8604967039:AAFbBMb5sMGulDDbGKMAvLsL4Q9uc_cTQvk', '-1003742654600') # Fallback grup Akuntan
        ]
        
        path_lengkap = os.path.join('static', 'nota_digital', path_gambar)
        
        for tok, cid in targets:
            if not tok or not cid: continue
            url = f"https://api.telegram.org/bot{tok}/sendPhoto"
            try:
                with open(path_lengkap, 'rb') as img_file:
                    payload = {'chat_id': cid, 'caption': pesan, 'parse_mode': 'Markdown'}
                    files = {'photo': img_file}
                    response = requests.post(url, data=payload, files=files, timeout=15)
                    if response.status_code == 200:
                        print(f"[OK] Telegram {jenis} ke {cid} Sukses!")
                    else:
                        print(f"[ERROR] Telegram {jenis} ke {cid} Error: {response.text}")
            except Exception as e:
                print(f"[ERROR] Telegram {jenis} ke {cid} Gagal: {e}")


# --- GLOBAL ERROR HANDLER ---
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    print(f"[GLOBAL ERROR] An error occurred: {e}")
    traceback.print_exc()
    # Jangan terekspos stacktrace penuh ke user untuk keamanan
    return f"Terjadi kesalahan internal pada server. Silakan coba beberapa saat lagi atau hubungi admin.", 500



# ==============================================================================
# 3. AUTENTIKASI & PROFIL (Login, Logout, Profil)
# ==============================================================================

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    error = request.args.get('error')
    return render_template('login.html', error=error)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if user and check_password_hash(user['password'], password):
        # Cek status akun
        try:
            if dict(user).get('status') == 'Nonaktif':
                return redirect(url_for('index', error='Akun Anda telah dinonaktifkan oleh Admin!'))
        except Exception:
            pass

        session['user'] = user['username']
        session['role'] = user['role']
        try:
            session['foto_profil'] = user['foto_profil']
        except Exception:
            session['foto_profil'] = None
        
        try:
            session['nama_lengkap'] = user['nama_lengkap'] or user['username']
        except Exception:
            session['nama_lengkap'] = user['username']

        # Update last_login
        try:
            now_str = datetime.now().strftime('%H:%M')
            conn.execute('UPDATE users SET last_login = ? WHERE username = ?', (f'Hari ini {now_str}', username))
            conn.commit()
        except Exception:
            pass
        
        # Set permission berdasarkan role
        if user['role'] == 'admin':
            session['permissions'] = 'keuangan,sparepart,servis,tutup_buku,users'
        elif user['role'] == 'teknisi':
            session['permissions'] = 'sparepart,servis'
        elif user['role'] == 'kasir':
            session['permissions'] = 'servis'
        else: # Role CUSTOM
            session['permissions'] = user['permissions'] or ''
            
        return redirect(url_for('dashboard'))
    return redirect(url_for('index', error='Username atau password salah!'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload_foto_profil', methods=['POST'])
def upload_foto_profil():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Belum login'}), 401
    
    if 'foto' not in request.files:
        return jsonify({'success': False, 'message': 'Tidak ada file yang dipilih'}), 400
        
    file = request.files['foto']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Tidak ada file yang dipilih'}), 400
        
    if file:
        filename = secure_filename(f"profil_{session['user']}_{int(time.time())}.png")
        filepath = os.path.join(app.config['UPLOAD_FOLDER_PROFIL'], filename)
        file.save(filepath)
        
        db_path = f"/static/uploads/profiles/{filename}"
        
        conn = get_db()
        conn.execute('UPDATE users SET foto_profil = ? WHERE username = ?', (db_path, session['user']))
        conn.commit()
        
        session['foto_profil'] = db_path
        return jsonify({'success': True, 'path': db_path, 'message': 'Foto profil berhasil diperbarui!'})


# --- FITUR MANAJEMEN USER ---


# ==============================================================================
# 4. MANAJEMEN USER (Admin Area, CRUD User)
# ==============================================================================

@app.route('/users')
def manage_users():
    if session.get('role') != 'admin':
        return "Hanya Admin yang bisa akses menu ini Bro!", 403
    
    conn = get_db()
    all_users = conn.execute('SELECT * FROM users ORDER BY id ASC').fetchall()
    
    stats = {
        'total': len(all_users),
        'admin': sum(1 for u in all_users if dict(u).get('role','').lower() == 'admin'),
        'teknisi': sum(1 for u in all_users if dict(u).get('role','').lower() == 'teknisi'),
        'kasir': sum(1 for u in all_users if dict(u).get('role','').lower() == 'kasir'),
        'cs': sum(1 for u in all_users if dict(u).get('role','').lower() not in ['admin', 'teknisi', 'kasir'])
    }
    return render_template('users.html', users=all_users, stats=stats)

@app.route('/users_mockup')
def users_mockup():
    return render_template('users_mockup.html')

@app.route('/users_mockup_v1')
def users_mockup_v1():
    return render_template('users_mockup_v1.html')

@app.route('/users_mockup_v2')
def users_mockup_v2():
    return render_template('users_mockup_v2.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    if session.get('role') != 'admin': return "Akses ditolak!", 403
    
    user = request.form.get('username')
    nama_lengkap = request.form.get('nama_lengkap') or user
    pw = request.form.get('password')
    role = request.form.get('role', 'teknisi').lower()
    status = request.form.get('status', 'Aktif')
    
    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username, nama_lengkap, password, role, status, last_login) VALUES (?, ?, ?, ?, ?, ?)', 
                     (user, nama_lengkap, generate_password_hash(pw), role, status, 'Baru dibuat'))
        conn.commit()
    except Exception as e:
        print(f"Gagal tambah user: {e}")
    return redirect(url_for('manage_users'))

@app.route('/edit_user/<int:id>', methods=['POST'])
def edit_user(id):
    if session.get('role') != 'admin': return "Akses ditolak!", 403
    
    nama_lengkap = request.form.get('nama_lengkap')
    role = request.form.get('role', 'teknisi').lower()
    
    conn = get_db()
    try:
        conn.execute('UPDATE users SET nama_lengkap = ?, role = ? WHERE id = ?', (nama_lengkap, role, id))
        conn.commit()
    except Exception as e:
        print(f"Gagal edit user: {e}")
    return redirect(url_for('manage_users'))

@app.route('/reset_password/<int:id>', methods=['POST'])
def reset_password(id):
    if session.get('role') != 'admin': return "Akses ditolak!", 403
    
    new_pw = request.form.get('password')
    if new_pw:
        conn = get_db()
        try:
            conn.execute('UPDATE users SET password = ? WHERE id = ?', (generate_password_hash(new_pw), id))
            conn.commit()
        except Exception as e:
            print(f"Gagal reset password: {e}")
    return redirect(url_for('manage_users'))

@app.route('/toggle_status/<int:id>')
def toggle_status(id):
    if session.get('role') != 'admin': return "Akses ditolak!", 403
    if id == 1: return "Admin utama tidak dapat dinonaktifkan!", 400
    
    conn = get_db()
    try:
        u = conn.execute('SELECT status FROM users WHERE id = ?', (id,)).fetchone()
        if u:
            new_status = 'Nonaktif' if dict(u).get('status') == 'Aktif' else 'Aktif'
            conn.execute('UPDATE users SET status = ? WHERE id = ?', (new_status, id))
            conn.commit()
    except Exception as e:
        print(f"Gagal toggle status: {e}")
    return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    if session.get('role') != 'admin': return "Akses ditolak!", 403
    
    if id == 1:
        return "Admin utama tidak boleh dihapus!", 400

    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    return redirect(url_for('manage_users'))



# ==============================================================================
# 5. DASHBOARD & PENCARIAN (Halaman Utama, API Search)
# ==============================================================================

@app.route('/api/check_update')
def check_update():
    try:
        db_path = os.path.join(os.getcwd(), 'sukabumi_flasher.db')
        wal_path = db_path + '-wal'
        mtime = os.path.getmtime(db_path) if os.path.exists(db_path) else 0
        if os.path.exists(wal_path):
            wal_mtime = os.path.getmtime(wal_path)
            if wal_mtime > mtime:
                mtime = wal_mtime
        return jsonify({"status": "success", "last_update": mtime})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/dashboard')
def dashboard():
    # Log buat debug
    if request.args.get('bot') == os.getenv('BOT_SECRET_KEY', 'SF_RAHASIA_NEGARA'):
        print(f"[DEBUG] Bot sedang mengakses Dashboard view={request.args.get('view')}")

    # Cek session ATAU kasih akses khusus ke bot telegram kita buat ambil screenshot
    if 'user' not in session and request.args.get('bot') != os.getenv('BOT_SECRET_KEY', 'SF_RAHASIA_NEGARA'): 
        return redirect(url_for('index'))
    
    # JIKA MODE MILESTONE (KHUSUS BOT)
    if request.args.get('view') == 'milestone':
        conn = get_db()
        # SYNC LOGIC: Hitung semua Cash yang sudah diisi Modalnya (Siklus Sekarang)
        laba_servis = conn.execute("SELECT SUM(\"Laba Kotor\") FROM servis WHERE Status='Cash' AND (COALESCE(\"Modal Part\", 0) > 0 OR COALESCE(\"Modal Jasa\", 0) > 0 OR COALESCE(\"Lain-lain\", 0) > 0)").fetchone()[0] or 0
        res_tambahan = conn.execute("SELECT SUM(CASE WHEN jenis='Masuk' THEN nominal ELSE -nominal END) FROM transaksi_tambahan WHERE uraian != 'MODAL KAS KECIL (LACI)'")
        laba_tambahan = res_tambahan.fetchone()[0] or 0
        laba_kotor = laba_servis + laba_tambahan

        gaji = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'gaji'").fetchone()[0] or 0
        ops = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'operasional'").fetchone()[0] or 0
        total_beban = gaji + ops
        laba_bersih = laba_kotor - total_beban
        
        # Hitung persen
        p_gaji = min(100, (laba_kotor / gaji * 100)) if gaji > 0 else 0
        p_ops = min(100, (max(0, laba_kotor - gaji) / ops * 100)) if ops > 0 else 0
        
        status_text = "OTW TARGET GAJI"
        status_class = "status-otw"
        if laba_kotor >= total_beban:
            status_text = "CTH! (LABA BERSIH)" if laba_kotor > total_beban else "CTO! (OPERASIONAL AMAN)"
            status_class = "status-cth" if laba_kotor > total_beban else "status-cto"
        elif laba_kotor >= gaji:
            status_text = "CTS! (GAJI AMAN)"
            status_class = "status-cts"
            
        # conn.close()
            
        pass
        return render_template('milestone_view.html', 
                               laba_kotor=laba_kotor, gaji=gaji, ops=ops, 
                               total_beban=total_beban, laba_bersih=laba_bersih,
                               p_gaji=p_gaji, p_ops=p_ops, 
                               status_text=status_text, status_class=status_class)

    
    page = request.args.get('page', 1, type=int)
    tgl_filter = request.args.get('tgl', '')
    q_filter = request.args.get('q', '')
    per_page = 10
    offset = (page - 1) * per_page
    
    conn = get_db()
    
    # 1. AMBIL SALDO AWAL
    last_kas = conn.execute('SELECT saldo_akhir FROM kas_utama ORDER BY id DESC LIMIT 1').fetchone()
    saldo_berjalan = last_kas['saldo_akhir'] if last_kas else 0
    kas_awal_tampilan = saldo_berjalan

    # BUILD QUERY CONDITIONS
    query_conditions = []
    params = []
    if tgl_filter:
        query_conditions.append('"Tanggal Masuk" LIKE ?')
        params.append(f'%{tgl_filter}%')
    if q_filter:
        query_conditions.append('("Nama User" LIKE ? OR "Device" LIKE ?)')
        params.append(f'%{q_filter}%')
        params.append(f'%{q_filter}%')
    
    where_clause = ""
    if query_conditions:
        where_clause = "WHERE " + " AND ".join(query_conditions)

    # 2. HITUNG TOTAL DATA & PAGINATION
    total_data = conn.execute(f'SELECT COUNT(*) FROM servis {where_clause}', params).fetchone()[0]
    total_pages = (total_data + per_page - 1) // per_page

    # 3. AMBIL DATA SERVIS UNTUK TABEL UTAMA
    order_logic = 'ORDER BY CASE WHEN Status = "Cash" THEN 0 WHEN Status = "Cancel" THEN 1 ELSE 2 END, "Tanggal Masuk" DESC, rowid DESC'
    query = f'SELECT rowid as id, * FROM servis {where_clause} {order_logic} LIMIT ? OFFSET ?'
    servis_raw = conn.execute(query, params + [per_page, offset]).fetchall()

    # 3.5 AMBIL REKAP STATUS UNTUK DIAGRAM BATANG
    status_counts = conn.execute(f'SELECT Status, COUNT(*) as count FROM servis {where_clause} GROUP BY Status', params).fetchall()
        
    status_data = {
        'Analisa': 0, 'Konfirmasi': 0, 'Wait Part': 0, 'Repair': 0, 
        'Done': 0, 'Failed': 0, 'Garansi': 0, 'Refund': 0, 
        'Cancel': 0, 'Cash': 0
    }
    for row in status_counts:
        st_raw = row['Status']
        if st_raw:
            # Cari yang cocok tanpa peduli besar-kecil huruf
            st_key = st_raw.strip().title()
            if st_key in status_data:
                status_data[st_key] += row['count']
            elif st_key == "Wait Part": # Tambahan jaga-jaga kalau ada typo lain
                status_data["Wait Part"] += row['count']

    # 3.8 AMBIL DATA AUTOCOMPLETE
    semua_nama = conn.execute('SELECT DISTINCT "Nama User" FROM servis WHERE "Nama User" IS NOT NULL').fetchall()
    semua_device = conn.execute('SELECT DISTINCT "Device" FROM servis WHERE "Device" IS NOT NULL').fetchall()
    autocomplete_data = list(set([row['Nama User'] for row in semua_nama] + [row['Device'] for row in semua_device]))

    # 3.9 AMBIL STATISTIK JENIS KERUSAKAN DENGAN KATEGORISASI (LEVEL 1)
    kerusakan_raw = conn.execute('''
        SELECT LOWER(TRIM("Analisa Kerusakan")) as k_text
        FROM servis 
        WHERE "Analisa Kerusakan" IS NOT NULL AND TRIM("Analisa Kerusakan") != ''
    ''').fetchall()
    
    kategori_count = {
        "LCD": 0,
        "Baterai": 0,
        "Charging": 0,
        "Software": 0,
        "Audio": 0,
        "Kamera": 0,
        "Sinyal": 0,
        "Mesin": 0,
        "Kena Air": 0,
        "Lainnya": 0
    }
    
    for row in kerusakan_raw:
        teks = row['k_text']
        
        # Cek kondisi dari yang paling spesifik ke umum
        if 'air' in teks or 'water' in teks or 'basah' in teks:
            kategori_count["Kena Air"] += 1
        elif 'lcd' in teks or 'layar' in teks or 'pecah' in teks or 'blank' in teks or 'garis' in teks or 'touch' in teks or 'sentuh' in teks:
            kategori_count["LCD"] += 1
        elif 'cas' in teks or 'charge' in teks or 'charging' in teks or 'connector' in teks or 'konektor' in teks or 'adapter' in teks or 'plug' in teks:
            kategori_count["Charging"] += 1
        elif 'batre' in teks or 'battery' in teks or 'baterai' in teks or 'drop' in teks or 'kembung' in teks:
            kategori_count["Baterai"] += 1
        elif 'frp' in teks or 'bootloop' in teks or 'unlock' in teks or 'update' in teks or 'software' in teks or 'stuck' in teks or 'logo' in teks or 'flash' in teks:
            kategori_count["Software"] += 1
        elif 'audio' in teks or 'suara' in teks or 'mic' in teks or 'speaker' in teks or 'buzzer' in teks or 'bunyi' in teks:
            kategori_count["Audio"] += 1
        elif 'kamera' in teks or 'camera' in teks or 'lensa' in teks:
            kategori_count["Kamera"] += 1
        elif 'sinyal' in teks or 'jaringan' in teks or 'wifi' in teks or 'imei' in teks or 'no service' in teks or 'bluetooth' in teks:
            kategori_count["Sinyal"] += 1
        elif 'matot' in teks or 'mati' in teks or 'mesin' in teks or 'ic' in teks or 'cpu' in teks or 'short' in teks or 'konslet' in teks:
            kategori_count["Mesin"] += 1
        else:
            kategori_count["Lainnya"] += 1
            
    # Hapus filter > 0 agar semua 10 kategori muncul, lalu sort
    sorted_kategori = sorted([(k, v) for k, v in kategori_count.items()], key=lambda x: x[1], reverse=True)
    
    kerusakan_stats = {
        'labels': [item[0] for item in sorted_kategori],
        'data': [item[1] for item in sorted_kategori]
    }
    # 4. HITUNGAN KAS HARIAN (ALL CASH yang sudah diisi Modalnya)
    s_cash = conn.execute('SELECT * FROM servis WHERE Status = "Cash" AND (COALESCE("Modal Part", 0) > 0 OR COALESCE("Modal Jasa", 0) > 0 OR COALESCE("Lain-lain", 0) > 0)').fetchall()
    t_tambahan = conn.execute('SELECT * FROM transaksi_tambahan').fetchall()
    g_hari = conn.execute("SELECT SUM(nilai) FROM beban WHERE kategori = 'Gaji'").fetchone()[0] or 0
    o_hari = conn.execute("SELECT SUM(nilai) FROM beban WHERE kategori = 'Operasional'").fetchone()[0] or 0

    # 5. BUAT HISTORY KAS & HITUNG VARIABEL UNTUK TEMPLATE
    history_kas = []
    history_kas.append({'uraian': 'KAS ASET AWAL', 'debit': kas_awal_tampilan, 'kredit': 0, 'saldo': kas_awal_tampilan})

    # Cari Modal Kas Kecil biar nampil di atas
    modal_kas_kecil = 0
    sisa_tambahan = []
    for t in t_tambahan:
        if t['uraian'] == 'MODAL KAS KECIL (LACI)':
            modal_kas_kecil += t['nominal']
        else:
            sisa_tambahan.append(t)

    if modal_kas_kecil > 0:
        saldo_berjalan += modal_kas_kecil
        history_kas.append({'uraian': 'MODAL KAS KECIL (LACI)', 'debit': modal_kas_kecil, 'kredit': 0, 'saldo': saldo_berjalan})

    # Hitung Penjualan
    total_penjualan = sum(s['Harga Jual'] or 0 for s in s_cash)
    saldo_berjalan += total_penjualan
    history_kas.append({'uraian': 'TOTAL PENJUALAN SERVICE', 'debit': total_penjualan, 'kredit': 0, 'saldo': saldo_berjalan})

    # Hitung Modal
    t_modal_barang = sum(s['Modal Part'] or 0 for s in s_cash)
    t_modal_jasa = sum(s['Modal Jasa'] or 0 for s in s_cash)
    t_modal_lain = sum(s['Lain-lain'] or 0 for s in s_cash)
    total_modal = t_modal_barang + t_modal_jasa + t_modal_lain
    saldo_berjalan -= total_modal
    history_kas.append({'uraian': 'TOTAL MODAL (PART + JASA + LAIN)', 'debit': 0, 'kredit': total_modal, 'saldo': saldo_berjalan})

    # Hitung Beban Tetap
    beban_tetap = g_hari + o_hari
    saldo_berjalan -= beban_tetap
    history_kas.append({'uraian': 'TOTAL BEBAN (GAJI + OPS)', 'debit': 0, 'kredit': beban_tetap, 'saldo': saldo_berjalan})

    # 6. HITUNG BAGI HASIL SEBELUM TRANSAKSI TAMBAHAN
    laba_bersih_calc = saldo_berjalan - kas_awal_tampilan - modal_kas_kecil
    bonus = int(round(laba_bersih_calc * 0.1)) if laba_bersih_calc > 0 else 0
    pengelola = int(round(laba_bersih_calc * 0.3)) if laba_bersih_calc > 0 else 0
    investor = int(round(laba_bersih_calc * 0.3)) if laba_bersih_calc > 0 else 0
    aset_30 = int(round(laba_bersih_calc * 0.3)) if laba_bersih_calc > 0 else 0

    if laba_bersih_calc > 0:
        saldo_berjalan -= bonus
        history_kas.append({'uraian': 'Bagi Hasil: Bonus Karyawan (10%)', 'debit': 0, 'kredit': bonus, 'saldo': saldo_berjalan})
        saldo_berjalan -= pengelola
        history_kas.append({'uraian': 'Bagi Hasil: Pengelola (30%)', 'debit': 0, 'kredit': pengelola, 'saldo': saldo_berjalan})
        saldo_berjalan -= investor
        history_kas.append({'uraian': 'Bagi Hasil: Investor (30%)', 'debit': 0, 'kredit': investor, 'saldo': saldo_berjalan})
        # Kas aset tidak mengurangi saldo fisik laci
        history_kas.append({'uraian': 'Setoran Kas Aset (30%)', 'debit': aset_30, 'kredit': 0, 'saldo': saldo_berjalan, 'highlight': True})

    # 7. TRANSAKSI TAMBAHAN LAINNYA (Paling Bawah)
    for t in sisa_tambahan:
        if t['jenis'] == 'Masuk':
            saldo_berjalan += t['nominal']
            history_kas.append({'id': t['id'], 'uraian': t['uraian'], 'debit': t['nominal'], 'kredit': 0, 'saldo': saldo_berjalan, 'manual': True})
        else:
            saldo_berjalan -= t['nominal']
            history_kas.append({'id': t['id'], 'uraian': t['uraian'], 'debit': 0, 'kredit': t['nominal'], 'saldo': saldo_berjalan, 'manual': True})

    # Clean row data untuk tabel utama
    servis_clean = []
    for row in servis_raw:
        clean_row = {k.strip(): v for k, v in dict(row).items()}
        clean_row['id'] = row['id']
        servis_clean.append(clean_row)

    # 7.8 HITUNG INSIGHT HARI INI & TEKNISI TERBAIK
    tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
    insight_masuk = conn.execute('SELECT COUNT(*) FROM servis WHERE "Tanggal Masuk" = ?', (tgl_hari_ini,)).fetchone()[0]
    insight_selesai = conn.execute('SELECT COUNT(*) FROM servis WHERE updated_at LIKE ? AND Status IN ("Done", "Cash")', (f'{tgl_hari_ini}%',)).fetchone()[0]
    insight_cash = conn.execute('SELECT COUNT(*) FROM servis WHERE updated_at LIKE ? AND Status = "Cash"', (f'{tgl_hari_ini}%',)).fetchone()[0]
    insight_pending = conn.execute('SELECT COUNT(*) FROM servis WHERE Status IN ("Analisa", "Konfirmasi", "Wait Part", "Repair")').fetchone()[0]
    
    total_laba_kotor = total_penjualan - total_modal
    
    best_tech_row = conn.execute('''
        SELECT Teknisi, SUM("Harga Jual") as revenue, COUNT(*) as jobs
        FROM servis
        WHERE updated_at LIKE ? AND Status = "Cash" AND Teknisi IS NOT NULL AND TRIM(Teknisi) != ""
        GROUP BY Teknisi
        ORDER BY revenue DESC
        LIMIT 1
    ''', (f'{tgl_hari_ini}%',)).fetchone()
    
    if best_tech_row:
        tech_name = best_tech_row['Teknisi']
        user_row = conn.execute('SELECT foto_profil FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(username) LIKE LOWER(?) LIMIT 1', (tech_name.strip(), f"%{tech_name.strip()}%")).fetchone()
        foto_profil = user_row['foto_profil'] if user_row and user_row['foto_profil'] else '/static/icon_teknisi.png'
        
        teknisi_terbaik = {
            'nama': tech_name,
            'revenue': best_tech_row['revenue'],
            'jobs': best_tech_row['jobs'],
            'foto_profil': foto_profil
        }
    else:
        teknisi_terbaik = {'nama': 'Belum Ada', 'revenue': 0, 'jobs': 0, 'foto_profil': '/static/icon_teknisi.png'}


    # 7.5 AMBIL DATA ARSIP DARI MySQL (Lemari Baja)
    try:
        db_mysql = pymysql.connect(host=os.getenv('MYSQL_HOST', 'localhost'), user=os.getenv('MYSQL_USER', 'root'), password=os.getenv('MYSQL_PASSWORD', ''), database=os.getenv('MYSQL_DB', 'db_ais_systems'))
        cur_mysql = db_mysql.cursor(pymysql.cursors.DictCursor)

        # 1. Hapus Otomatis Garansi yang sudah kadaluarsa
        cur_mysql.execute("DELETE FROM arsip_garansi WHERE tgl_akhir < CURDATE()")
        db_mysql.commit()

        # 2. Ambil Statistik Sisa Umur Garansi
        cur_mysql.execute("""
            SELECT 
                SUM(CASE WHEN DATEDIFF(tgl_akhir, CURDATE()) <= 30 THEN 1 ELSE 0 END) as sisa_1_bulan,
                SUM(CASE WHEN DATEDIFF(tgl_akhir, CURDATE()) BETWEEN 31 AND 60 THEN 1 ELSE 0 END) as sisa_2_bulan,
                SUM(CASE WHEN DATEDIFF(tgl_akhir, CURDATE()) > 60 THEN 1 ELSE 0 END) as sisa_3_bulan
            FROM arsip_garansi
        """)
        g_stats_raw = cur_mysql.fetchone()
        garansi_stats = {
            '1_bulan': int(g_stats_raw['sisa_1_bulan'] or 0) if g_stats_raw else 0,
            '2_bulan': int(g_stats_raw['sisa_2_bulan'] or 0) if g_stats_raw else 0,
            '3_bulan': int(g_stats_raw['sisa_3_bulan'] or 0) if g_stats_raw else 0
        }

        # 3. Ambil Statistik Tindakan Pelanggan
        cur_mysql.execute("""
            SELECT tindakan, COUNT(*) as jumlah 
            FROM arsip_pelanggan 
            WHERE tindakan IS NOT NULL AND TRIM(tindakan) != ''
            GROUP BY tindakan 
            ORDER BY jumlah DESC 
            LIMIT 5
        """)
        top_tindakan = cur_mysql.fetchall()
        tindakan_labels = [row['tindakan'].title() for row in top_tindakan]
        tindakan_data = [row['jumlah'] for row in top_tindakan]
        
        pelanggan_stats = {
            'labels': tindakan_labels,
            'data': tindakan_data
        }

        q_garansi = request.args.get('q_garansi', '')
        q_pelanggan = request.args.get('q_pelanggan', '')
        q_sparepart = request.args.get('q_sparepart', '')

        # Pagination & Filter Garansi
        p_garansi = request.args.get('p_garansi', 1, type=int)
        offset_garansi = (p_garansi - 1) * 10
        
        where_g = ""
        params_g = []
        if q_garansi:
            where_g = "WHERE nama_user LIKE %s OR device LIKE %s"
            params_g = [f"%{q_garansi}%", f"%{q_garansi}%"]

        cur_mysql.execute(f"SELECT COUNT(*) as total FROM arsip_garansi {where_g}", params_g)
        total_garansi = cur_mysql.fetchone()['total']
        total_p_garansi = (total_garansi + 9) // 10 if total_garansi > 0 else 1
        cur_mysql.execute(f"SELECT * FROM arsip_garansi {where_g} ORDER BY id_garansi DESC LIMIT 10 OFFSET %s", params_g + [offset_garansi])
        arsip_garansi = cur_mysql.fetchall()

        # Pagination & Filter Pelanggan
        p_pelanggan = request.args.get('p_pelanggan', 1, type=int)
        offset_pelanggan = (p_pelanggan - 1) * 10
        
        where_p = ""
        params_p = []
        if q_pelanggan:
            where_p = "WHERE nama_user LIKE %s OR device LIKE %s"
            params_p = [f"%{q_pelanggan}%", f"%{q_pelanggan}%"]

        cur_mysql.execute(f"SELECT COUNT(*) as total FROM arsip_pelanggan {where_p}", params_p)
        total_pelanggan = cur_mysql.fetchone()['total']
        total_p_pelanggan = (total_pelanggan + 9) // 10 if total_pelanggan > 0 else 1
        cur_mysql.execute(f"SELECT * FROM arsip_pelanggan {where_p} ORDER BY id_arsip DESC LIMIT 10 OFFSET %s", params_p + [offset_pelanggan])
        arsip_pelanggan = cur_mysql.fetchall()

        # Pagination & Filter Sparepart
        p_sparepart = request.args.get('p_sparepart', 1, type=int)
        offset_sparepart = (p_sparepart - 1) * 10
        where_s = ""
        params_s = []
        if q_sparepart:
            where_s = "WHERE kategori LIKE %s OR merek LIKE %s OR jenis_barang LIKE %s OR jenis_device LIKE %s"
            params_s = [f"%{q_sparepart}%", f"%{q_sparepart}%", f"%{q_sparepart}%", f"%{q_sparepart}%"]
            
        cur_mysql.execute(f"SELECT COUNT(*) as total FROM data_sparepart {where_s}", params_s)
        total_sparepart = cur_mysql.fetchone()['total']
        total_p_sparepart = (total_sparepart + 9) // 10 if total_sparepart > 0 else 1
        cur_mysql.execute(f"SELECT * FROM data_sparepart {where_s} ORDER BY id_sparepart DESC LIMIT 10 OFFSET %s", params_s + [offset_sparepart])
        data_sparepart = cur_mysql.fetchall()

        # 4. Ambil Statistik Kategori Sparepart
        cur_mysql.execute("""
            SELECT kategori, SUM(qty) as jumlah 
            FROM data_sparepart 
            WHERE kategori IS NOT NULL AND TRIM(kategori) != ''
            GROUP BY kategori 
            ORDER BY jumlah DESC
        """)
        kat_rows = cur_mysql.fetchall()
        sparepart_stats = {
            'labels': [row['kategori'] for row in kat_rows],
            'data': [row['jumlah'] for row in kat_rows]
        }
        
        # Autocomplete Garansi
        cur_mysql.execute("SELECT DISTINCT nama_user FROM arsip_garansi WHERE nama_user IS NOT NULL")
        g_nama = cur_mysql.fetchall()
        cur_mysql.execute("SELECT DISTINCT device FROM arsip_garansi WHERE device IS NOT NULL")
        g_device = cur_mysql.fetchall()
        auto_garansi = list(set([row['nama_user'] for row in g_nama] + [row['device'] for row in g_device]))

        # Autocomplete Pelanggan
        cur_mysql.execute("SELECT DISTINCT nama_user FROM arsip_pelanggan WHERE nama_user IS NOT NULL")
        p_nama = cur_mysql.fetchall()
        cur_mysql.execute("SELECT DISTINCT device FROM arsip_pelanggan WHERE device IS NOT NULL")
        p_device = cur_mysql.fetchall()
        auto_pelanggan = list(set([row['nama_user'] for row in p_nama] + [row['device'] for row in p_device]))
        
        # Autocomplete Sparepart
        cur_mysql.execute("SELECT DISTINCT jenis_barang FROM data_sparepart WHERE jenis_barang IS NOT NULL")
        s_barang = cur_mysql.fetchall()
        cur_mysql.execute("SELECT DISTINCT jenis_device FROM data_sparepart WHERE jenis_device IS NOT NULL")
        s_device = cur_mysql.fetchall()
        auto_sparepart = list(set([row['jenis_barang'] for row in s_barang] + [row['jenis_device'] for row in s_device]))

        db_mysql.close()
    except Exception as e:
        print(f"Error load arsip: {e}")
        arsip_garansi = []
        arsip_pelanggan = []
        data_sparepart = []
        p_garansi = 1
        p_pelanggan = 1
        p_sparepart = 1
        total_p_garansi = 1
        total_p_pelanggan = 1
        total_p_sparepart = 1
        q_garansi = ''
        q_pelanggan = ''
        q_sparepart = ''
        auto_garansi = []
        auto_pelanggan = []
        auto_sparepart = []
        garansi_stats = {'1_bulan': 0, '2_bulan': 0, '3_bulan': 0}
        pelanggan_stats = {'labels': [], 'data': []}
        sparepart_stats = {'labels': [], 'data': []}

    # 7.5 CEK NOTIFIKASI SLA (Tidak Ada Update)
    sla_notifications = []
    try:
        cur_sla = conn.execute("SELECT rowid, * FROM servis WHERE Status NOT IN ('Cash', 'Cancel', 'Done', 'Refund') AND updated_at IS NOT NULL")
        now_dt = datetime.now()
        for row in cur_sla.fetchall():
            row_dict = dict(row)
            updated_str = row_dict.get('updated_at')
            if updated_str:
                try:
                    up_dt = datetime.strptime(updated_str, '%Y-%m-%d %H:%M:%S')
                    diff = now_dt - up_dt
                    hours_diff = diff.total_seconds() / 3600
                    
                    wa_number = row_dict.get('No. WA', '')
                    if wa_number and wa_number.startswith('0'):
                        wa_number = '62' + wa_number[1:]
                    wa_link = f"https://wa.me/{wa_number}" if wa_number else "#"
                    
                    dev_name = row_dict.get('Device', 'Unknown')
                    
                    if hours_diff >= 168:
                        if int(row_dict.get('flag_kritis', 0)) == 0:
                            tok = '8604967039:AAFbBMb5sMGulDDbGKMAvLsL4Q9uc_cTQvk'
                            cid = '-1003742654600'
                            pesan_tele = f"🚨 *KASUS KRITIS (Mandek >7 Hari)*\nDevice: {dev_name}\nStatus: {row_dict.get('Status')}\nTeknisi: {row_dict.get('Teknisi')}\nSegera tindak lanjuti!"
                            try:
                                import requests
                                requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={'chat_id': cid, 'text': pesan_tele, 'parse_mode': 'Markdown'})
                                conn.execute("UPDATE servis SET flag_kritis = 1 WHERE rowid = ?", (row_dict['rowid'],))
                                conn.commit()
                            except Exception as e:
                                print("Gagal kirim notif kritis tele:", e)
                        sla_notifications.append({'level': 'kritis', 'badge': '🚨', 'title': f"[{int(hours_diff//24)} Hari] {dev_name}", 'desc': 'Kritis (Telah diekskalasi)', 'wa_link': wa_link})
                    elif hours_diff >= 72:
                        sla_notifications.append({'level': 'owner', 'badge': '🔴', 'title': f"[72 Jam] {dev_name}", 'desc': 'Eskalasi Admin', 'wa_link': wa_link})
                    elif hours_diff >= 48:
                        sla_notifications.append({'level': 'happy_call', 'badge': '🟠', 'title': f"[48 Jam] {dev_name}", 'desc': 'Happy Call / Customer Update', 'wa_link': wa_link})
                    elif hours_diff >= 24:
                        sla_notifications.append({'level': 'teknisi', 'badge': '🟡', 'title': f"[24 Jam] {dev_name}", 'desc': 'Reminder Teknisi', 'wa_link': wa_link})
                except Exception as e:
                    pass
    except Exception as e:
        print("Error SLA notif:", e)

    # 8. RETURN DENGAN NAMA VARIABEL YANG PAS
    # conn.close()
    pass
    new_unit_popup = None
    if request.args.get('new_unit_id'):
        new_unit_popup = {
            'id': request.args.get('new_unit_id'),
            'user': request.args.get('new_user', 'Pelanggan'),
            'device': request.args.get('new_dev', 'Unit Servis')
        }

    return render_template('dashboard.html', 
                           new_unit_popup=new_unit_popup,
                           insight_masuk=insight_masuk,
                           insight_selesai=insight_selesai,
                           insight_cash=insight_cash,
                           insight_pending=insight_pending,
                           total_laba_kotor=total_laba_kotor,
                           teknisi_terbaik=teknisi_terbaik,
                           sla_notifications=sla_notifications,
                           servis=servis_clean, 
                           current_page=page, 
                           total_pages=total_pages,
                           history_kas=history_kas, 
                           kas_awal=kas_awal_tampilan,
                           total_penjualan=total_penjualan,
                           total_modal_barang=t_modal_barang,
                           total_modal_jasa=t_modal_jasa,
                           total_modal_lain=t_modal_lain,
                           g_hari=g_hari, 
                           o_hari=o_hari,
                           laba_bersih=laba_bersih_calc,
                           bonus=bonus, 
                           aset_30=aset_30,
                           pengelola=pengelola, 
                           investor=investor,
                           t_tambahan=t_tambahan,
                           tgl_aktif=tgl_filter,
                           q_aktif=q_filter,
                           saldo_terakhir=saldo_berjalan,
                           arsip_garansi=arsip_garansi,
                           arsip_pelanggan=arsip_pelanggan,
                           p_garansi=p_garansi,
                           total_p_garansi=total_p_garansi,
                           p_pelanggan=p_pelanggan,
                           total_p_pelanggan=total_p_pelanggan,
                           q_garansi=q_garansi,
                           q_pelanggan=q_pelanggan,
                           status_data=status_data,
                           autocomplete_data=autocomplete_data,
                           auto_garansi=auto_garansi,
                           auto_pelanggan=auto_pelanggan,
                           garansi_stats=garansi_stats,
                           pelanggan_stats=pelanggan_stats,
                           data_sparepart=data_sparepart,
                           p_sparepart=p_sparepart,
                           total_p_sparepart=total_p_sparepart,
                           q_sparepart=q_sparepart,
                           auto_sparepart=auto_sparepart,
                           sparepart_stats=sparepart_stats,
                           kerusakan_stats=kerusakan_stats)

@app.route('/api/search_pelanggan')
def search_pelanggan():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2: return jsonify([])
    
    results_map = {}
    import re
    
    # 1. Cari di SQLite (servis & arsip_servis)
    try:
        conn = get_db()
        search_term = f'%{q}%'
        query_sql = '''
            SELECT DISTINCT nama, wa FROM (
                SELECT "Nama User" as nama, "No. WA" as wa FROM servis WHERE "Nama User" LIKE ? OR REPLACE(REPLACE("No. WA", '-', ''), ' ', '') LIKE ?
                UNION
                SELECT nama_user as nama, wa as wa FROM arsip_servis WHERE nama_user LIKE ? OR REPLACE(REPLACE(wa, '-', ''), ' ', '') LIKE ?
            ) WHERE nama IS NOT NULL AND nama != ''
            ORDER BY nama ASC LIMIT 15
        '''
        rows = conn.execute(query_sql, (search_term, search_term, search_term, search_term)).fetchall()
        for r in rows:
            if r['nama']:
                k = f"{r['nama'].strip().lower()}_{str(r['wa'] or '').strip().lower()}"
                results_map[k] = {'nama': r['nama'].strip(), 'wa': str(r['wa'] or '').strip()}
    except Exception as e:
        print("Error search_pelanggan SQLite:", e)

    # 2. Cari di MySQL (arsip_pelanggan & arsip_garansi)
    try:
        import pymysql, os
        db_m = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'db_ais_systems'),
            cursorclass=pymysql.cursors.DictCursor
        )
        cur_m = db_m.cursor()
        search_term_m = f"%{q}%"
        clean_q = re.sub(r'[\s\-+]', '', q)
        if clean_q and len(clean_q) >= 2 and clean_q.isdigit():
            search_wa_m = f"%{clean_q[-9:] if len(clean_q) >= 9 else clean_q}%"
        else:
            search_wa_m = search_term_m
            
        cur_m.execute("""
            SELECT DISTINCT nama_user as nama, no_wa as wa FROM arsip_pelanggan 
            WHERE nama_user LIKE %s OR REPLACE(REPLACE(no_wa, '-', ''), ' ', '') LIKE %s
            UNION
            SELECT DISTINCT nama_user as nama, '' as wa FROM arsip_garansi 
            WHERE nama_user LIKE %s
            LIMIT 20
        """, (search_term_m, search_wa_m, search_term_m))
        rows_m = cur_m.fetchall()
        for r in rows_m:
            if r['nama']:
                k = f"{r['nama'].strip().lower()}_{str(r['wa'] or '').strip().lower()}"
                if k not in results_map:
                    results_map[k] = {'nama': r['nama'].strip(), 'wa': str(r['wa'] or '').strip()}
        db_m.close()
    except Exception as e:
        print("Error search_pelanggan MySQL:", e)
        
    final_results = sorted(list(results_map.values()), key=lambda x: x['nama'].lower())[:15]
    return jsonify(final_results)

@app.route('/api/check_wa')
def check_wa():
    wa = request.args.get('wa', '').strip()
    import re
    clean_wa = re.sub(r'[\s\-+]', '', wa)
    if not clean_wa or len(clean_wa) < 5: return jsonify({'found': False})
    
    last_digits = clean_wa[-9:] if len(clean_wa) >= 9 else clean_wa
    search_pattern_sql = f'%{last_digits}%'
    search_pattern_mysql = f'%{last_digits}%'
    
    all_rows = []
    
    # 1. Cari di SQLite (servis & arsip_servis)
    try:
        conn = get_db()
        query = '''
            SELECT "Nama User" as nama, "Tanggal Masuk" as tgl, "Device" as device FROM servis WHERE REPLACE(REPLACE("No. WA", '-', ''), ' ', '') LIKE ?
            UNION ALL
            SELECT nama_user as nama, tanggal_masuk as tgl, device as device FROM arsip_servis WHERE REPLACE(REPLACE(wa, '-', ''), ' ', '') LIKE ?
        '''
        rows = conn.execute(query, (search_pattern_sql, search_pattern_sql)).fetchall()
        for r in rows:
            all_rows.append({'nama': r['nama'], 'tgl': r['tgl'], 'device': r['device']})
    except Exception as e:
        print("Error check_wa SQLite:", e)
        
    # 2. Cari di MySQL (arsip_pelanggan)
    try:
        import pymysql, os
        db_m = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'db_ais_systems'),
            cursorclass=pymysql.cursors.DictCursor
        )
        cur_m = db_m.cursor()
        cur_m.execute("""
            SELECT nama_user as nama, device, status_final, id_arsip FROM arsip_pelanggan 
            WHERE REPLACE(REPLACE(no_wa, '-', ''), ' ', '') LIKE %s
            ORDER BY id_arsip DESC
        """, (search_pattern_mysql,))
        rows_m = cur_m.fetchall()
        for r in rows_m:
            all_rows.append({'nama': r['nama'], 'tgl': 'Arsip Selesai', 'device': r['device'], 'id_arsip': r['id_arsip']})
        db_m.close()
    except Exception as e:
        print("Error check_wa MySQL:", e)
        
    if not all_rows:
        return jsonify({'found': False})
        
    valid_dates = []
    latest_name = all_rows[0]['nama']
    latest_device = all_rows[0]['device']
    
    for r in all_rows:
        tgl_str = r.get('tgl', '')
        if tgl_str and tgl_str != 'Arsip Selesai':
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(str(tgl_str).split()[0], '%Y-%m-%d')
                valid_dates.append((parsed_date, r['nama'], r['device'], tgl_str))
            except Exception:
                pass
                
    if valid_dates:
        valid_dates.sort(key=lambda x: x[0], reverse=True)
        latest_date = valid_dates[0][0]
        latest_name = valid_dates[0][1]
        latest_device = valid_dates[0][2]
        months = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agt", "Sep", "Okt", "Nov", "Des"]
        formatted_date = f"{latest_date.day} {months[latest_date.month]} {latest_date.year}"
    else:
        formatted_date = 'Arsip Pelanggan'
        latest_name = all_rows[0]['nama']
        latest_device = all_rows[0]['device']
        
    return jsonify({
        'found': True,
        'nama': latest_name,
        'device': latest_device or '',
        'total_servis': len(all_rows),
        'terakhir': formatted_date
    })



# ==============================================================================
# 6. TRANSAKSI SERVIS (Input, Update, Detail, Delete)
# ==============================================================================

@app.route('/detail/<int:id>')
def detail(id):
    if 'user' not in session: return redirect(url_for('index'))
    conn = get_db()
    row = conn.execute('SELECT rowid as id, * FROM servis WHERE rowid = ?', (id,)).fetchone()
    # conn.close()
    pass
    
    if row:
        # Bersihkan nama kolom seperti di dashboard
        s_clean = {k.strip(): v for k, v in dict(row).items()}
        s_clean['id'] = row['id']
        return render_template('detail.html', s=s_clean)
    return "Data tidak ditemukan!"

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if 'user' not in session: return redirect(url_for('index'))
    
    conn_check = get_db()
    s_old = conn_check.execute('SELECT * FROM servis WHERE rowid = ?', (id,)).fetchone()
    if not s_old: return "Data tidak ditemukan", 404
    
    # 1. Ambil data dari form
    nama = request.form.get('nama_user')
    wa = request.form.get('no_wa')
    dev = request.form.get('device')
    pw = request.form.get('password_hp')
    ana = request.form.get('analisa')
    tind = request.form.get('tindakan')
    est = request.form.get('estimasi')
    dp = request.form.get('dp')
    h_jual = int(request.form.get('harga_jual') or 0)
    m_part_raw = request.form.get('modal_part')
    m_jasa_raw = request.form.get('modal_jasa')
    
    m_part = int(m_part_raw or 0)
    m_jasa = int(m_jasa_raw or 0)
    m_lain = int(request.form.get('lain_lain') or 0)
    stat = request.form.get('status')
    garansi_val = request.form.get('masa_garansi') or "1 Bulan"
    tek = request.form.get('teknisi')
    
    kelengkapan_list = request.form.getlist('kelengkapan[]')
    kondisi_list = request.form.getlist('kondisi[]')
    kelengkapan_str = ', '.join(kelengkapan_list) if kelengkapan_list else '-'
    kondisi_str = ', '.join(kondisi_list) if kondisi_list else '-'
    
    # --- PROTEKSI ROLE (ADMIN vs KASIR vs TEKNISI) ---
    role = session.get('role', 'custom')
    
    # Proteksi Khusus KASIR
    if role == 'kasir':
        if stat == 'Cash' and s_old['Status'] not in ['Done', 'Cash']:
            return """
            <html><head><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script></head>
            <body style="background:#0b1120; color:white;">
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Akses Kasir Dibatasi',
                    text: 'Akun Kasir HANYA BISA merubah status ke CASH dari status DONE! Pastikan unit sudah selesai diperbaiki oleh Teknisi terlebih dahulu.',
                    background: '#1e293b',
                    color: '#f8fafc',
                    confirmButtonColor: '#3b82f6'
                }).then(function() {
                    window.history.back();
                });
            });
            </script>
            </body></html>
            """
        if stat == 'Selesai Klaim' and s_old['Status'] not in ['Done', 'Garansi', 'Klaim Garansi', 'Selesai Klaim']:
            return """
            <html><head><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script></head>
            <body style="background:#0b1120; color:white;">
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Akses Kasir Dibatasi',
                    text: 'Akun Kasir HANYA BISA merubah status ke SELESAI KLAIM dari status DONE atau GARANSI!',
                    background: '#1e293b',
                    color: '#f8fafc',
                    confirmButtonColor: '#3b82f6'
                }).then(function() {
                    window.history.back();
                });
            });
            </script>
            </body></html>
            """
        # Pertahankan modal part/jasa lama agar Kasir tidak bisa merubah/menimpa modal toko
        m_part = s_old['Modal Part'] or 0
        m_jasa = s_old['Modal Jasa'] or 0
        m_lain = s_old['Lain-lain'] or 0
        m_part_raw = str(m_part)
        m_jasa_raw = str(m_jasa)
        
    # Proteksi Khusus TEKNISI
    elif role == 'teknisi':
        if stat in ['Cash', 'Selesai Klaim', 'Refund']:
            return """
            <html><head><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script></head>
            <body style="background:#0b1120; color:white;">
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Akses Ditolak',
                    text: 'Akun Teknisi tidak diizinkan merubah status closing (CASH / SELESAI KLAIM / REFUND)! Proses closing & finansial adalah tugas Kasir atau Admin.',
                    background: '#1e293b',
                    color: '#f8fafc',
                    confirmButtonColor: '#3b82f6'
                }).then(function() {
                    window.history.back();
                });
            });
            </script>
            </body></html>
            """
        # Pertahankan harga jual dan modal agar Teknisi tidak menimpa/merubah data finansial
        h_jual = s_old['Harga Jual'] or 0
        m_part = s_old['Modal Part'] or 0
        m_jasa = s_old['Modal Jasa'] or 0
        m_lain = s_old['Lain-lain'] or 0
        m_part_raw = str(m_part)
        m_jasa_raw = str(m_jasa)
    # ------------------------------------------------
    
    # --- VALIDASI ATURAN TOKO ---
    if stat in ['Done', 'Cash', 'Selesai Klaim', 'Refund']:
        if not tind or tind.strip() == '' or tind.strip() == '-':
            return """
            <html><head><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script></head>
            <body style="background:#0b1120; color:white;">
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Gagal Menyimpan',
                    text: 'Ketika status diubah ke Done, Cash, Selesai Klaim, atau Refund, Kolom Tindakan WAJIB diisi dengan benar.',
                    background: '#1e293b',
                    color: '#f8fafc',
                    confirmButtonColor: '#3b82f6'
                }).then(function() {
                    window.history.back();
                });
            });
            </script>
            </body></html>
            """
            
    if stat == 'Done':
        if not tek or tek.strip() == '' or tek.strip() == '-':
            return """
            <html><head><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script></head>
            <body style="background:#0b1120; color:white;">
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Gagal Menyimpan',
                    text: 'Ketika status diubah ke Done, Nama Teknisi penanggung jawab WAJIB dipilih/diisi dengan benar!',
                    background: '#1e293b',
                    color: '#f8fafc',
                    confirmButtonColor: '#3b82f6'
                }).then(function() {
                    window.history.back();
                });
            });
            </script>
            </body></html>
            """

    if stat == 'Cash':
        if not m_part_raw or not m_jasa_raw or m_part_raw.strip() == '' or m_jasa_raw.strip() == '':
            return """
            <html><head><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script></head>
            <body style="background:#0b1120; color:white;">
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Gagal Menyimpan',
                    text: 'Ketika status diubah ke Cash, Kolom Modal Part dan Modal Jasa WAJIB diisi.',
                    background: '#1e293b',
                    color: '#f8fafc',
                    confirmButtonColor: '#3b82f6'
                }).then(function() {
                    window.history.back();
                });
            });
            </script>
            </body></html>
            """
            
    if stat == 'Selesai Klaim':
        h_jual = 0
    # ----------------------------
    
    # 2. Hitung Laba
    laba_final = h_jual - m_part - m_jasa - m_lain if stat == 'Cash' else 0

    conn = get_db()
    try:
        # PENTING: Perhatikan nama kolom "Laba Kotor" (pakai spasi sesuai database lo)
        conn.execute('''
            UPDATE servis SET 
                "Nama User" = ?, "No. WA" = ?, "Device" = ?, "Password" = ?,
                "Analisa Kerusakan" = ?, "Tindakan Perbaikan" = ?,
                "Estimasi Biaya" = ?, "DP" = ?, "Harga Jual" = ?, 
                "Modal Part" = ?, "Modal Jasa" = ?, "Lain-lain" = ?,
                "Laba Kotor" = ?, "Status" = ?, "masa_garansi" = ?,
                "Teknisi" = ?, kelengkapan = ?, kondisi_fisik = ?, updated_at = ?
            WHERE rowid = ?
        ''', (nama, wa, dev, pw, ana, tind, est, dp, h_jual, m_part, m_jasa, m_lain, laba_final, stat, garansi_val, tek, kelengkapan_str, kondisi_str, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
        conn.commit()
        print(f"[OK] Berhasil Update Unit: {dev}")
    except Exception as e:
        print(f"[ERROR] Gagal Update: {e}")
        return f"Waduh Bro, Gagal Simpan ke Database: {e}", 500
    finally:
        # conn.close()
        pass
    
    # CEK MILESTONE OTOMATIS JIKA STATUS CASH (Balikin ke Background biar kenceng)
    if stat == 'Cash':
        kirim_notif_kas_masuk(dev, nama, h_jual, laba_final, tek)
        threading.Thread(target=cek_dan_kirim_milestone, daemon=True).start()

    if stat == 'Done':
        return redirect(url_for('dashboard', wa_done=id))
    elif stat == 'Cash':
        if s_old['Status'] != 'Cash':
            return redirect(url_for('dashboard', cash_done=id))

    return redirect(url_for('dashboard'))

@app.route('/input_baru')
def input_baru():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('input.html')

@app.route('/preview')
def preview_input():
    return render_template('preview_input.html')

@app.route('/preview_update')
def preview_update():
    return render_template('preview_update.html')



@app.route('/tambah', methods=['GET', 'POST']) # Tambahkan 'GET' di sini
def tambah():
    if 'user' not in session: return redirect(url_for('index'))
    
    if request.method == 'POST':
        tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
        
        # Tangkap semua data dari form
        n_user = request.form.get('nama_user')
        wa = request.form.get('no_wa')
        dev = request.form.get('device')
        pw = request.form.get('password_hp')
        ana = request.form.get('analisa') or ''
        
        # Tangkap checklist Kelengkapan Aksesoris dan Kondisi Fisik unit
        kelengkapan_list = request.form.getlist('kelengkapan[]')
        kondisi_list = request.form.getlist('kondisi[]')
        kelengkapan_str = ', '.join(kelengkapan_list) if kelengkapan_list else '-'
        kondisi_str = ', '.join(kondisi_list) if kondisi_list else '-'

        tindakan = request.form.get('tindakan')
        est = request.form.get('estimasi') or 0 # Default 0 kalau kosong
        dp = request.form.get('dp') or 0 # Default 0 kalau kosong
        tek = request.form.get('teknisi')
        status_input = request.form.get('status') or 'Analisa'

        conn = get_db()
        new_id = None
        try:
            # Pastikan urutan kolom sesuai dengan tabel servis lo
            cur = conn.execute('''
                INSERT INTO servis (
                    "Tanggal Masuk", "Device", "Nama User", "No. WA", 
                    "Password", "Analisa Kerusakan", "Tindakan Perbaikan", 
                    "Status", "Teknisi", "Estimasi Biaya", "DP", updated_at,
                    kelengkapan, kondisi_fisik
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tgl_hari_ini, dev, n_user, wa, pw, ana.strip() if ana else '-', tindakan, status_input, tek, est, dp, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), kelengkapan_str, kondisi_str))
            new_id = cur.lastrowid
            conn.commit()
            print(f"Berhasil input unit baru dengan status: {status_input} (ID: {new_id})")
        except Exception as e:
            print(f"Gagal simpan: {e}")
        finally:
            # conn.close()
            pass
        
        # 1. Notifikasi Unit Baru ke Telegram
        kirim_notif_unit_baru(dev, ana.strip() if ana else '-', tindakan, kelengkapan_str, kondisi_str)

        # 2. Tambahkan cek milestone jika status awal langsung Cash (Background)
        if status_input == 'Cash':
            kirim_notif_kas_masuk(dev, n_user, est, est, tek)
            threading.Thread(target=cek_dan_kirim_milestone, daemon=True).start()
            
        if new_id:
            return redirect(url_for('dashboard', new_unit_id=new_id, new_user=n_user, new_dev=dev))
        return redirect(url_for('dashboard'))

    # Jika method GET (klik tombol dari dashboard), tampilkan form tambah.html
    return render_template('input.html')

# FUNGSI HAPUS DATA
@app.route('/delete/<int:id>')
def delete(id):
    # Cek apakah yang login admin
    if session.get('role') != 'admin':
        return "Akses Ditolak! Cuma Admin yang bisa hapus."
    
    conn = get_db()
    conn.execute('DELETE FROM servis WHERE rowid = ?', (id,))
    conn.commit()
    # conn.close()
    pass
    return redirect(url_for('dashboard'))

# FUNGSI EDIT DATA (Update Identitas Unit)
@app.route('/edit_data/<int:id>', methods=['POST'])
def edit_data(id):
    if 'user' not in session: return redirect(url_for('index'))
    
    n_user = request.form.get('nama_user')
    wa = request.form.get('no_wa')
    dev = request.form.get('device')
    pw = request.form.get('password_hp')
    ana = request.form.get('analisa')
    tindakan = request.form.get('tindakan') # Ambil input tindakan baru
    tek = request.form.get('teknisi')
    
    kelengkapan_list = request.form.getlist('kelengkapan[]')
    kondisi_list = request.form.getlist('kondisi[]')
    kelengkapan_str = ', '.join(kelengkapan_list) if kelengkapan_list else '-'
    kondisi_str = ', '.join(kondisi_list) if kondisi_list else '-'
    
    conn = get_db()
    try:
        # Update query dengan kolom "Tindakan Perbaikan", kelengkapan, dan kondisi_fisik
        conn.execute('''
            UPDATE servis SET 
            "Nama User" = ?, 
            "No. WA" = ?, 
            Device = ?, 
            PassWord = ?, 
            "Analisa Kerusakan" = ?, 
            "Tindakan Perbaikan" = ?, 
            Teknisi = ?,
            kelengkapan = ?,
            kondisi_fisik = ?,
            updated_at = ?
            WHERE rowid = ?
        ''', (n_user, wa, dev, pw, ana, tindakan, tek, kelengkapan_str, kondisi_str, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
        conn.commit()
    except Exception as e:
        print(f"Gagal update: {{e}}")
    finally:
        # conn.close()
        pass
        
    return redirect(url_for('detail', id=id))

# --- FITUR UPLOAD FOTO PROFIL ---
@app.route('/simpan_sparepart', methods=['POST'])
def simpan_sparepart():
    if 'user' not in session: return redirect(url_for('index'))
    
    id_sparepart = request.form.get('id_sparepart', '').strip()
    tgl = request.form.get('tanggal_masuk')
    kategori = request.form.get('kategori')
    merek = request.form.get('merek')
    barang = request.form.get('jenis_barang')
    device = request.form.get('jenis_device')
    
    # Fungsi pembersih angka (hapus koma/titik/huruf)
    def clean_number(val):
        if not val: return 0
        num_str = ''.join(filter(str.isdigit, str(val)))
        return int(num_str) if num_str else 0

    beli = clean_number(request.form.get('harga_beli'))
    jual = clean_number(request.form.get('harga_jual'))
    qty = clean_number(request.form.get('qty'))
    
    try:
        db = pymysql.connect(host=os.getenv('MYSQL_HOST', 'localhost'), user=os.getenv('MYSQL_USER', 'root'), password=os.getenv('MYSQL_PASSWORD', ''), database=os.getenv('MYSQL_DB', 'db_ais_systems'))
        cur = db.cursor()
        
        if id_sparepart:
            # Edit mode
            cur.execute("""
                UPDATE data_sparepart 
                SET tanggal_masuk=%s, kategori=%s, merek=%s, jenis_barang=%s, jenis_device=%s, qty=%s, harga_beli=%s, harga_jual=%s
                WHERE id_sparepart=%s
            """, (tgl, kategori, merek, barang, device, qty, beli, jual, id_sparepart))
        else:
            # Tambah baru
            cur.execute("""
                INSERT INTO data_sparepart (tanggal_masuk, kategori, merek, jenis_barang, jenis_device, qty, harga_beli, harga_jual)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tgl, kategori, merek, barang, device, qty, beli, jual))
            
        db.commit()
        db.close()
    except Exception as e:
        print(f"[ERROR] Gagal simpan sparepart: {e}")
        # Bisa diarahkan ke error page atau dikembalikan ke dashboard dengan alert
        # Saat ini kita akan return fallback yang tidak crash
        
    return redirect(url_for('dashboard') + '#tabel-sparepart')

@app.route('/delete_sparepart/<int:id>')
def delete_sparepart(id):
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    
    db = pymysql.connect(host=os.getenv('MYSQL_HOST', 'localhost'), user=os.getenv('MYSQL_USER', 'root'), password=os.getenv('MYSQL_PASSWORD', ''), database=os.getenv('MYSQL_DB', 'db_ais_systems'))
    cur = db.cursor()
    cur.execute("DELETE FROM data_sparepart WHERE id_sparepart=%s", (id,))
    db.commit()
    return redirect(url_for('dashboard') + '#tabel-sparepart')

# ==========================================================
#                  AI AGENT TELEGRAM LOGIC
# ==========================================================

PENDING_UNITS = {}
PENDING_LOCK = threading.Lock()



# ==============================================================================
# 7. KEUANGAN & BEBAN (Beban Harian, Kas Tambahan, Pembayaran)
# ==============================================================================

@app.route('/beban')
def beban():
    if 'user' not in session: return redirect(url_for('index'))
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS beban 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, kategori TEXT, nama_beban TEXT, nilai INTEGER)''')
    semua_beban = conn.execute('SELECT rowid as id, * FROM beban').fetchall()
    # conn.close()
    pass
    tgl_skrg = datetime.now().strftime("%Y-%m-%d")
    return render_template('beban.html', tgl=tgl_skrg, beban_list=semua_beban)

# FITUR BARU: EDIT BEBAN
@app.route('/edit_beban/<int:id>', methods=['POST'])
def edit_beban(id):
    nama = request.form.get('nama_beban')
    nilai = int(request.form.get('nilai', 0))
    conn = get_db()
    conn.execute('UPDATE beban SET nama_beban = ?, nilai = ? WHERE rowid = ?', (nama, nilai, id))
    conn.commit()
    # conn.close()
    pass
    return redirect(url_for('beban'))

@app.route('/tambah_beban', methods=['POST'])
def tambah_beban():
    if 'user' not in session: return redirect(url_for('index'))
    
    kat = request.form.get('kategori')
    nama = request.form.get('nama_beban').strip()
    nilai = request.form.get('nilai')
    
    if not nama or not nilai:
        return redirect(url_for('beban'))

    conn = get_db()
    try:
        # INSERT OR REPLACE: Kalau nama sudah ada, timpa nilainya (jangan double)
        conn.execute('INSERT OR REPLACE INTO beban (kategori, nama_beban, nilai) VALUES (?, ?, ?)', 
                     (kat, nama, int(nilai)))
        conn.commit()
    except Exception as e:
        print(f"Gagal simpan beban: {{e}}")
    finally:
        # conn.close()
        pass
        
    return redirect(url_for('beban'))

@app.route('/hapus_beban/<int:id>')
def hapus_beban(id):
    conn = get_db()
    conn.execute('DELETE FROM beban WHERE rowid = ?', (id,))
    conn.commit()
    # conn.close()
    pass
    return redirect(url_for('beban'))

@app.route('/tambah_tambahan', methods=['POST'])
def tambah_tambahan():
    if 'user' not in session: return redirect(url_for('index'))
    
    jenis = request.form.get('jenis')
    uraian_select = request.form.get('uraian_select')
    uraian_custom = request.form.get('uraian_custom')
    
    if uraian_select == 'Lainnya' or not uraian_select:
        uraian = request.form.get('uraian') or uraian_custom or "Tambahan"
    else:
        uraian = uraian_select
        
    nominal = request.form.get('nominal', 0)
    tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO transaksi_tambahan (tanggal, uraian, jenis, nominal)
            VALUES (?, ?, ?, ?)
        ''', (tgl_hari_ini, uraian, jenis, int(nominal)))
        conn.commit()
    except Exception as e:
        print(f"Gagal tambah transaksi: {{e}}")
    finally:
        # conn.close()
        pass
        
    return redirect(url_for('dashboard'))

@app.route('/hapus_tambahan/<int:id>')
def hapus_tambahan(id):
    if 'user' not in session: return redirect(url_for('index'))
    
    conn = get_db()
    try:
        conn.execute('DELETE FROM transaksi_tambahan WHERE id = ?', (id,))
        conn.commit()
    except Exception as e:
        print(f"Gagal hapus transaksi: {e}")
    finally:
        # conn.close()
        pass
        
    return redirect(url_for('dashboard') + '#tabel-kas')

@app.route('/bayar/<int:id>')
def portal_pembayaran(id):
    conn = get_db()
    unit = conn.execute('SELECT * FROM servis WHERE No = ?', (id,)).fetchone()
    if not unit:
        return "Unit tidak ditemukan", 404
    return render_template('pembayaran.html', unit=unit)

@app.route('/proses_bayar', methods=['POST'])
def proses_bayar():
    servis_id = request.form.get('servis_id')
    metode = request.form.get('metode')
    nominal = request.form.get('nominal')
    
    file = request.files.get('bukti_bayar')
    filename = None
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"BUKTI_{servis_id}_{int(time.time())}.png")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    conn = get_db()
    conn.execute('''
        INSERT INTO pembayaran (servis_id, metode, nominal, bukti_bayar, tanggal, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (servis_id, metode, nominal, filename, datetime.now().strftime("%Y-%m-%d %H:%M"), 'Pending'))
    conn.commit()
    
    return jsonify({"status": "success", "message": "Pembayaran sedang diverifikasi oleh sistem AIS!"})



# ==============================================================================
# 8. NOTA, CETAK & ENGINE RENDER (Cetak Termal, WA Bridge)
# ==============================================================================

@app.route('/milestone_preview')
def milestone_preview():
    # Akses khusus bot
    if request.args.get('bot') != os.getenv('BOT_SECRET_KEY', 'SF_RAHASIA_NEGARA'):
        return "Akses Ditolak", 403
        
    conn = get_db()
    laba_servis = conn.execute("SELECT SUM(\"Laba Kotor\") FROM servis WHERE Status='Cash' AND (COALESCE(\"Modal Part\", 0) > 0 OR COALESCE(\"Modal Jasa\", 0) > 0 OR COALESCE(\"Lain-lain\", 0) > 0)").fetchone()[0] or 0
    res_tambahan = conn.execute("SELECT SUM(CASE WHEN jenis='Masuk' THEN nominal ELSE -nominal END) FROM transaksi_tambahan WHERE uraian != 'MODAL KAS KECIL (LACI)'")
    laba_tambahan = res_tambahan.fetchone()[0] or 0
    laba_kotor = laba_servis + laba_tambahan

    gaji = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'gaji'").fetchone()[0] or 0
    ops = conn.execute("SELECT SUM(nilai) FROM beban WHERE LOWER(TRIM(kategori)) = 'operasional'").fetchone()[0] or 0
    total_beban = gaji + ops
    laba_bersih = laba_kotor - total_beban
    
    p_gaji = min(100, (laba_kotor / gaji * 100)) if gaji > 0 else 0
    p_ops = min(100, (max(0, laba_kotor - gaji) / ops * 100)) if ops > 0 else 0
    
    status_text = "OTW TARGET GAJI"
    status_class = "status-otw"
    if laba_kotor >= total_beban:
        status_text = "CTH! (LABA BERSIH)" if laba_kotor > total_beban else "CTO! (OPERASIONAL AMAN)"
        status_class = "status-cth" if laba_kotor > total_beban else "status-cto"
    elif laba_kotor >= gaji:
        status_text = "CTS! (GAJI AMAN)"
        status_class = "status-cts"
        
        # conn.close()
        
        pass
    return render_template('milestone_view.html', 
                           laba_kotor=laba_kotor, gaji=gaji, ops=ops, 
                           total_beban=total_beban, laba_bersih=laba_bersih,
                           p_gaji=p_gaji, p_ops=p_ops, 
                           status_text=status_text, status_class=status_class)

@app.route('/cetak_nota/<int:id>')
def cetak_nota(id):
    if 'user' not in session: return redirect(url_for('index'))
    
    conn = get_db()
    s = conn.execute('SELECT rowid as id, * FROM servis WHERE rowid = ?', (id,)).fetchone()
    # conn.close()
    pass
    
    garansi_pilihan = request.args.get('garansi', 'Tanpa Garansi')
    tgl_akhir = "-"
    
    # Logic hitung tanggal akhir garansi
    if "Bulan" in garansi_pilihan:
        jumlah_bulan = int(garansi_pilihan.split()[0])
        # Hitung dari tanggal hari ini (saat nota dicetak)
        akhir = datetime.now() + relativedelta(months=jumlah_bulan)
        tgl_akhir = akhir.strftime('%d %b %Y') # Format: 23 Jul 2026
    tgl_cetak = datetime.now().strftime('%d/%m/%Y')
    jam_cetak = datetime.now().strftime('%H:%M')

    return render_template('nota_termal.html', s=s, garansi=garansi_pilihan, tgl_akhir=tgl_akhir, tgl_cetak=tgl_cetak, jam_cetak=jam_cetak)

@app.route('/cetak_penerimaan/<int:id>')
def cetak_penerimaan(id):
    if 'user' not in session: return redirect(url_for('index'))
    conn = get_db()
    s = conn.execute('SELECT rowid as id, * FROM servis WHERE rowid = ?', (id,)).fetchone()
    # conn.close()
    pass
    tgl_cetak = datetime.now().strftime('%d/%m/%Y')
    jam_cetak = datetime.now().strftime('%H:%M')
    return render_template('nota_penerimaan_termal.html', s=s, tgl_cetak=tgl_cetak, jam_cetak=jam_cetak)

@app.route('/generate_nota_image/<int:id>')
def generate_nota_image(id):
    conn = get_db()
    s = conn.execute('SELECT rowid as id, * FROM servis WHERE rowid = ?', (id,)).fetchone()
    # conn.close()
    pass
    
    garansi = request.args.get('garansi', 'Tanpa Garansi')
    tgl_akhir = request.args.get('tgl_akhir', '-')
    tgl_sekarang = datetime.now().strftime('%d/%m/%Y')
    jam_sekarang = datetime.now().strftime('%H:%M')

    invoice_no = f"SF-{datetime.now().strftime('%y%m%d')}-{id:03d}"
    
    imei_sn = '-'
    teknisi = s['Teknisi'] if 'Teknisi' in s.keys() and s['Teknisi'] else 'Tim SF'
    kondisi_awal = s['Analisa Kerusakan'] if 'Analisa Kerusakan' in s.keys() and s['Analisa Kerusakan'] else '-'
    tindakan = s['Tindakan Perbaikan'] if 'Tindakan Perbaikan' in s.keys() and s['Tindakan Perbaikan'] else '-'
    
    import base64
    try:
        with open('static/logo.png', 'rb') as img_file:
            logo_b64 = base64.b64encode(img_file.read()).decode('utf-8')
    except:
        logo_b64 = ""

    html_content = render_template(
        'nota_garansi.html',
        s=s,
        invoice_no=invoice_no,
        garansi_durasi=garansi,
        tgl_akhir=tgl_akhir,
        tgl_sekarang=tgl_sekarang,
        kondisi_awal=kondisi_awal,
        tindakan=tindakan,
        teknisi=teknisi,
        jam_cetak=jam_sekarang,
        logo_b64=logo_b64
    )

    try:
        filename = f"nota_{id}.png"
        hti_garansi.screenshot(html_str=html_content, save_as=filename)
        import time
        return url_for('static', filename=f'nota_digital/{filename}', v=int(time.time()))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Python Exception: {str(e)}", 500

@app.route('/generate_penerimaan_image/<int:id>')
def generate_penerimaan_image(id):
    conn = get_db()
    s = conn.execute('SELECT rowid as id, * FROM servis WHERE rowid = ?', (id,)).fetchone()
    # conn.close()
    pass
    
    tgl_sekarang = datetime.now().strftime('%d/%m/%Y')
    jam_sekarang = datetime.now().strftime('%H:%M')

    try:
        est_val = int(s['Estimasi Biaya']) if s['Estimasi Biaya'] else 0
    except:
        est_val = 0
        
    try:
        dp_val = int(s['DP']) if 'DP' in s.keys() and s['DP'] else 0
    except:
        dp_val = 0
        
    sisa_val = est_val - dp_val

    est_str = f"Rp {est_val:,.0f}".replace(',', '.')
    dp_str = f"Rp {dp_val:,.0f}".replace(',', '.')
    sisa_str = f"Rp {sisa_val:,.0f}".replace(',', '.')

    import base64
    try:
        with open('static/logo.png', 'rb') as img_file:
            logo_b64 = base64.b64encode(img_file.read()).decode('utf-8')
    except:
        logo_b64 = ""

    html_content = render_template('nota_penerimaan.html', s=s, jam_cetak=jam_sekarang, est_str=est_str, dp_str=dp_str, sisa_str=sisa_str, logo_b64=logo_b64)
    try:
        filename = f"penerimaan_{id}.png"
        hti_penerimaan.screenshot(html_str=html_content, save_as=filename)
        import time
        return url_for('static', filename=f'nota_digital/{filename}', v=int(time.time()))
    except Exception as e:
        print(f"Error Generate Penerimaan: {e}")
        return f"Gagal bikin gambar nota penerimaan! Error: {str(e)}", 500

@app.route('/nota_bridge/<int:id>')
def nota_bridge(id):
    if 'user' not in session: return redirect(url_for('index'))
    
    conn = get_db()
    s = conn.execute('SELECT rowid as id, * FROM servis WHERE rowid = ?', (id,)).fetchone()
    # conn.close()
    pass
    
    if not s: return "Data tidak ditemukan", 404
    
    type_nota = request.args.get('type', 'penerimaan')
    garansi = request.args.get('garansi', '')
    tgl_akhir = request.args.get('tgl_akhir', '')
    
    # Siapkan URL Gambar & Print
    if type_nota == 'penerimaan':
        img_url = url_for('generate_penerimaan_image', id=id)
        print_url = url_for('cetak_penerimaan', id=id)
        tgl = datetime.now().strftime('%d/%m/%Y')
        jam = datetime.now().strftime('%H:%M')
        keluhan = s['Analisa Kerusakan'] or s['Tindakan Perbaikan'] or '-'
        is_klaim = (s['Status'] in ['Garansi', 'Klaim Garansi'])
        judul_nota = "*NOTA PENERIMAAN KLAIM GARANSI*" if is_klaim else "*NOTA PENERIMAAN SERVICE*"
        ket_teks = (
            f"Bukti serah terima unit untuk pengecekan & perbaikan ulang dalam masa garansi Sukabumi Flasher.\n"
            if is_klaim else
            f"Bukti penerimaan barang untuk perbaikan.\nHarap simpan nota ini untuk pengambilan unit.\n"
        )
        
        chk_wa = ""
        if 'kelengkapan' in s.keys() and s['kelengkapan'] and s['kelengkapan'] != '-':
            chk_wa += f"\n📦 *Kelengkapan*: {s['kelengkapan']}"
        if 'kondisi_fisik' in s.keys() and s['kondisi_fisik'] and s['kondisi_fisik'] != '-':
            chk_wa += f"\n⚠️ *Kondisi Fisik*: {s['kondisi_fisik']}"
            
        teks_wa = (
            f"{judul_nota}\n\n"
            f"*SUKABUMI FLASHER*\n"
            f"WA: +62 811-1737-030\n\n"
            f"Tanggal : {tgl}\n"
            f"Jam : {jam}\n\n"
            f"ID Transaksi : *#{s['id']}*\n"
            f"Status : *{'🛡️ Klaim Garansi' if is_klaim else s['Status']}*\n\n"
            f"Pelanggan : *{s['Nama User']}*\n\n"
            f"Device : *{s['Device']}*\n\n"
            f"Keluhan/Klaim : *{keluhan}*{chk_wa}\n\n"
            f"*Keterangan:*\n"
            f"{ket_teks}\n"
            f"*PERHATIAN:*\n"
            f"• Nota ini bukan bukti pembayaran."
        )
    else:
        img_url = url_for('generate_nota_image', id=id, garansi=garansi, tgl_akhir=tgl_akhir)
        print_url = url_for('cetak_nota', id=id, garansi=garansi)
        teks_wa = (
            f"Halo Kak *{s['Nama User']}* 👋\n\n"
            f"Terima kasih telah mempercayakan perbaikan *{s['Device']}* kepada *Sukabumi Flasher*.\n\n"
            f"Sebagai bentuk komitmen kami terhadap kualitas layanan, \n"
            f"kami lampirkan *Nota Garansi Digital* sebagai bukti garansi sekaligus riwayat servis perangkat Anda.\n\n"
            f"Mohon simpan nota ini dengan baik. \n"
            f"Apabila selama masa garansi terdapat kendala yang berkaitan dengan hasil servis, jangan ragu untuk menghubungi kami. Tim kami akan dengan senang hati membantu.\n\n"
            f"Terima kasih atas kepercayaan yang telah diberikan kepada Sukabumi Flasher. Semoga perangkat Anda selalu berfungsi dengan baik dan nyaman digunakan.\n\n"
            f"Salam hangat,\n"
            f"*Sukabumi Flasher* 🙏"
        )

    # Bersihkan nomor WA
    no_wa = s['No. WA'].replace(' ', '').replace('-', '').replace('+', '')
    if no_wa.startswith('0'): no_wa = '62' + no_wa[1:]

    return render_template('bridge_nota.html', 
                           id=id, 
                           type=type_nota, 
                           img_url=img_url, 
                           print_url=print_url, 
                           no_wa=no_wa, 
                           teks_wa=teks_wa)

@app.route('/wa_selesai/<int:id>')
def wa_selesai(id):
    if 'user' not in session: return redirect(url_for('index'))
    conn = get_db()
    s = conn.execute('SELECT rowid as id, * FROM servis WHERE rowid = ?', (id,)).fetchone()
    # conn.close()
    pass
    
    if not s: return redirect(url_for('dashboard'))
    
    no_wa = s['No. WA'] or ''
    no_wa = no_wa.replace(' ', '').replace('-', '').replace('+', '')
    if no_wa.startswith('0'): no_wa = '62' + no_wa[1:]
    
    nama = s['Nama User']
    device = s['Device']
    
    teks = f"Halo kak *{nama}* 👋\n\nInfo dari *Sukabumi Flasher*, unit *{device}* kakak sudah *Selesai* diperbaiki dan sudah bisa diambil di toko ya kak. ✅\n\nTerima kasih! 🙏"
    
    import urllib.parse
    teks_encoded = urllib.parse.quote(teks)
    
    return redirect(f"https://api.whatsapp.com/send?phone={no_wa}&text={teks_encoded}")

@app.route('/engine')
def engine_dashboard():
    """Halaman Visual Utama AIS Engine (Command Center)"""
    if 'user' not in session: return redirect(url_for('index'))
    
    # Ambil data live dari Engine
    data = AISKalkulator.hitung_laba_hari_ini()
    bagi_hasil = AISKalkulator.hitung_bagi_hasil(data['laba_bersih'])
    milestone = AISKalkulator.cek_milestone()
    
    return render_template('engine_dashboard.html', 
                           data=data, 
                           bagi_hasil=bagi_hasil, 
                           milestone=milestone)

@app.route('/preview-teknisi')
def preview_teknisi():
    from flask import send_file
    return send_file('preview_teknisi_terbaik.html')

@app.route('/preview-header')
def preview_header():
    from flask import send_file
    return send_file('preview_header_options.html')



# ==============================================================================
# 9. TELEGRAM BOT & BACKGROUND WORKER (Telebot, Milestone)
# ==============================================================================

def kirim_laporan_ke_grup(path_gambar):
    # --- 1. TEKS PENGANTAR YANG ETIS & ESTETIS ---
    pesan_teks = (
        "🏢 *LAPORAN SIKLUS TUTUP BUKU - SUKABUMI FLASHER*\n\n"
        "Selamat sore Tim & Manajemen,\n"
        "Bersama ini kami lampirkan rekap otomatis Buku Kas dan Visual Alokasi Bagi Hasil (Hasil Penjualan) untuk siklus cut-off pukul 16:00 WIB hari ini.\n\n"
        "Terima kasih atas dedikasi dan kerja keras seluruh tim. Mari kita persiapkan siklus operasional selanjutnya dengan energi penuh.\n\n"
        "Salam,\n*SUKABUMI FLASHER*"
    )

    # --- 2. KIRIM KE TELEGRAM ---
    tele_token = os.getenv('BOT_TOKEN_LAPORAN')
    tele_chat_id = os.getenv('CHAT_ID_LAPORAN')
    url_tele = f"https://api.telegram.org/bot{{tele_token}}/sendPhoto"

    try:
        with open(path_gambar, 'rb') as img_file:
            payload = {
                'chat_id': tele_chat_id,
                'caption': pesan_teks,
                'parse_mode': 'Markdown'
            }
            files = {{'photo': img_file}}
            response = requests.post(url_tele, data=payload, files=files, timeout=10)
            if response.status_code == 200:
                print("Mantap! Laporan sukses mendarat di Grup Telegram.")
            else:
                print(f"Gagal Telegram: {{response.text}}")
    except Exception as e:
        print(f"Error kirim Telegram: {{e}}")

@app.route('/telegram_tutup_buku', methods=['POST'])
def telegram_tutup_buku():
    try:
        print("[INFO] Mengambil screenshot TUTUP BUKU...")
        tgl_sekarang = datetime.now().strftime('%Y%m%d_%H%M%S')
        nama_gambar = f"Laporan_Tutup_{tgl_sekarang}.png"
        from html2image import Html2Image
        hti_lokal = Html2Image(
            output_path=os.path.join(os.getcwd(), 'static', 'nota_digital'),
            custom_flags=['--headless=new', '--no-sandbox', '--disable-gpu', '--window-size=1050,720', '--disable-web-security', '--default-background-color=ffffffff']
        )
        hti_lokal.screenshot(url='http://127.0.0.1:5000/dashboard?bot=SF_RAHASIA_NEGARA', save_as=nama_gambar)
        import threading
        threading.Thread(target=kirim_laporan_telegram, args=(nama_gambar, "TUTUP")).start()
        return "Telegram Tutup Buku Sukses", 200
    except Exception as e:
        return f"Gagal Telegram Tutup Buku: {{e}}", 500

@app.route('/eksekusi_db', methods=['POST'])
def eksekusi_db():
    try:
        data = request.get_json()
        uang_fisik_raw = data.get('uang_fisik')
        if uang_fisik_raw is None or uang_fisik_raw == '':
            return "Waduh, nominal uang fisik kosong bro!", 400
        uang_fisik = int(uang_fisik_raw)
        total_saldo = int(data.get('total_saldo', 0))

        kas_aset_baru = total_saldo - uang_fisik

        conn_sqlite = get_db_connection()
        cur_sqlite = conn_sqlite.cursor()

        db_mysql = pymysql.connect(host=os.getenv('MYSQL_HOST', 'localhost'), user=os.getenv('MYSQL_USER', 'root'), password=os.getenv('MYSQL_PASSWORD', ''), database=os.getenv('MYSQL_DB', 'db_ais_systems'))
        cur_mysql = db_mysql.cursor(pymysql.cursors.DictCursor)

        # 1. Pindah Arsip (Dari tutup_buku)
        cur_sqlite.execute("SELECT rowid as id, * FROM servis")
        data_harian = cur_sqlite.fetchall()

        counter = 0
        for row in data_harian:
            data_row = dict(row)
            stts_raw = data_row.get('Status') or data_row.get('status')
            if not stts_raw: continue
            stts = str(stts_raw).strip().lower()

            if stts in ['cash', 'cancel', 'selesai klaim', 'garansi void', 'refund']:
                no_id = data_row.get('id')
                nama  = data_row.get('Nama User')
                wa    = data_row.get('No. WA')
                unit  = data_row.get('Device')
                aksi  = data_row.get('Tindakan Perbaikan')
                biaya = data_row.get('Harga Jual')

                sql_arsip = """INSERT INTO arsip_pelanggan 
                               (nama_user, no_wa, device, tindakan, harga_jual, status_final) 
                               VALUES (%s, %s, %s, %s, %s, %s)"""
                cur_mysql.execute(sql_arsip, (nama, wa, unit, aksi, biaya, stts.upper()))
                
                if stts == 'cash':
                    id_arsip = db_mysql.insert_id()
                    
                    # Ambil angka bulan dari masa_garansi (misal '3 Bulan' -> 3)
                    m_garansi_raw = data_row.get('masa_garansi') or "1 Bulan"
                    try:
                        m_garansi_num = int(m_garansi_raw.split()[0])
                    except:
                        m_garansi_num = 1
                    
                    sql_garansi = """INSERT INTO arsip_garansi 
                                     (id_arsip, nama_user, device, tgl_mulai, tgl_akhir) 
                                     VALUES (%s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s MONTH))"""
                    cur_mysql.execute(sql_garansi, (id_arsip, nama, unit, m_garansi_num))
                    
                # Copy ke arsip_servis lokal (SQLite)
                try:
                    kerusakan_val = data_row.get('Analisa Kerusakan') or ''
                    m_part_val = data_row.get('Modal Part') or 0
                    m_jasa_val = data_row.get('Modal Jasa') or 0
                    laba_val = data_row.get('Laba Kotor') or 0
                    tek_val = data_row.get('Teknisi') or ''
                    kelengkapan_val = data_row.get('kelengkapan') or '-'
                    kondisi_val = data_row.get('kondisi_fisik') or '-'
                    tgl_masuk_val = data_row.get('Tanggal Masuk') or ''
                    tgl_keluar_val = datetime.now().strftime('%Y-%m-%d')
                    cur_sqlite.execute("""
                        INSERT INTO arsip_servis (
                            tanggal_masuk, tanggal_keluar, nama_user, wa, device, 
                            kerusakan, tindakan, modal_part, modal_jasa, harga_jual, 
                            laba_kotor, teknisi, kelengkapan, kondisi_fisik
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (tgl_masuk_val, tgl_keluar_val, nama, wa, unit, kerusakan_val, aksi, m_part_val, m_jasa_val, biaya, laba_val, tek_val, kelengkapan_val, kondisi_val))
                except Exception as ex_arsip:
                    print(f"Error arsip lokal: {ex_arsip}")

                cur_sqlite.execute("DELETE FROM servis WHERE rowid = ?", (no_id,))
                counter += 1

        # 2. Update Master Kas di MySQL (Dari tutup_kas)
        cur_mysql.execute("UPDATE master_kas SET kas_kecil_laci = %s, kas_aset_pengelola = %s ORDER BY id_kas DESC LIMIT 1", (uang_fisik, kas_aset_baru))
        
        # 3. Reset Papan Tulis (SQLite) (Dari tutup_kas)
        cur_sqlite.execute("DELETE FROM transaksi_tambahan")
        tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
        cur_sqlite.execute("""
            INSERT INTO transaksi_tambahan (tanggal, uraian, jenis, nominal) 
            VALUES (?, 'MODAL KAS KECIL (LACI)', 'Masuk', ?)
        """, (tgl_hari_ini, uang_fisik))

        cur_sqlite.execute("INSERT INTO kas_utama (saldo_awal, saldo_akhir, total_laba_bersih) VALUES (?, ?, 0)", (kas_aset_baru, kas_aset_baru))

        conn_sqlite.commit()
        db_mysql.commit()

        return f"Siklus Selesai! {{counter}} data diarsip. Kas terkunci.", 200

    except Exception as e:
        if 'conn_sqlite' in locals(): conn_sqlite.rollback()
        if 'db_mysql' in locals(): db_mysql.rollback()
        print(f"ERROR DB: {{str(e)}}") 
        return f"Gagal eksekusi DB: {{str(e)}}", 500
    finally:
        if 'conn_sqlite' in locals(): conn_sqlite.close()
        if 'db_mysql' in locals(): db_mysql.close()

@app.route('/telegram_buka_buku', methods=['POST'])
def telegram_buka_buku():
    try:
        print("[INFO] Mengambil screenshot BUKA BUKU...")
        tgl_sekarang = datetime.now().strftime('%Y%m%d_%H%M%S')
        nama_gambar = f"Laporan_Buka_{tgl_sekarang}.png"
        from html2image import Html2Image
        hti_lokal = Html2Image(
            output_path=os.path.join(os.getcwd(), 'static', 'nota_digital'),
            custom_flags=['--headless=new', '--no-sandbox', '--disable-gpu', '--window-size=1050,720', '--disable-web-security', '--default-background-color=ffffffff']
        )
        hti_lokal.screenshot(url='http://127.0.0.1:5000/dashboard?bot=SF_RAHASIA_NEGARA', save_as=nama_gambar)
        import threading
        threading.Thread(target=kirim_laporan_telegram, args=(nama_gambar, "BUKA")).start()
        return "Telegram Buka Buku Sukses", 200
    except Exception as e:
        return f"Gagal Telegram Buka Buku: {{e}}", 500

def ai_tambah_servis(nama: str, device: str, kerusakan: str, estimasi: int = 0, wa: str = "-", tindakan: str = "-", teknisi: str = "Teknisi SF", dp: int = 0):
    """Fungsi untuk input unit servis baru lewat Telegram AI atau Web Assistant."""
    try:
        tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
        pw = "-"
        if not tindakan or tindakan == "":
            tindakan = "Cek & Analisa"
        if not teknisi or teknisi == "":
            teknisi = "Teknisi SF"
        try:
            estimasi = int(float(str(estimasi).replace('.', '').replace(',', '').replace('rb', '000').replace('k', '000').replace('Rp', '').strip()))
        except Exception:
            estimasi = 0
        try:
            dp = int(float(str(dp).replace('.', '').replace(',', '').strip()))
        except Exception:
            dp = 0
            
        with db_session() as conn:
            conn.execute('''
                INSERT INTO servis (
                    "Tanggal Masuk", "Device", "Nama User", "No. WA", 
                    "Password", "Analisa Kerusakan", "Tindakan Perbaikan", 
                    "Status", "Teknisi", "Estimasi Biaya", "DP", updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tgl_hari_ini, device, nama, wa, pw, kerusakan, tindakan, "Analisa", teknisi, estimasi, dp, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
        try:
            kirim_notif_unit_baru(device, kerusakan, tindakan)
        except Exception as e_notif:
            print(f"[WARNING] Gagal kirim notif unit baru: {e_notif}")
            
        return (f"✅ Berhasil input unit ke database:\n"
                f"📱 Device: {device}\n"
                f"👤 Pelanggan: {nama}\n"
                f"📞 WA: {wa}\n"
                f"🔧 Kerusakan: {kerusakan}\n"
                f"👨‍🔧 Teknisi: {teknisi}\n"
                f"💰 Estimasi: Rp {estimasi:,}".replace(',', '.'))
    except Exception as e:
        return f"❌ Gagal input unit: {str(e)}"

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
                "device": parts[0] or "Device",
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
    
    if ALLOWED_TELEGRAM_IDS and user_id not in ALLOWED_TELEGRAM_IDS:
        return False
        
    if deteksi_is_tambah_unit(user_text):
        msg_tunggu = await update.message.reply_text("🤖 <i>Sedang membaca dan menyusun data unit servis baru...</i>", parse_mode='HTML')
        data_ai = ekstrak_data_unit_ai(user_text)
        
        if data_ai and data_ai.get("is_valid"):
            token_id = str(int(time.time() * 1000))[-8:]
            unit_data = {
                "nama": str(data_ai.get("nama", "Pelanggan")),
                "device": str(data_ai.get("device", "Device")),
                "kerusakan": str(data_ai.get("kerusakan", "-")),
                "estimasi": int(data_ai.get("estimasi", 0)),
                "wa": str(data_ai.get("wa", "-")),
                "tindakan": str(data_ai.get("tindakan", "Cek & Analisa")),
                "teknisi": str(data_ai.get("teknisi", "Teknisi SF"))
            }
            with PENDING_LOCK:
                PENDING_UNITS[token_id] = unit_data
                
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
    await query.answer()
    
    data_cb = query.data.split('_')
    if len(data_cb) < 3: return
    action = data_cb[1]
    token_id = data_cb[2]
    
    with PENDING_LOCK:
        unit_data = PENDING_UNITS.pop(token_id, None)
        
    if not unit_data:
        await query.edit_message_text("⚠️ <b>Sesi konfirmasi sudah kedaluwarsa atau unit sudah disimpan sebelumnya.</b>", parse_mode='HTML')
        return
        
    if action == "batal":
        await query.edit_message_text("❌ <b>Input unit servis dibatalkan.</b>", parse_mode='HTML')
        return
        
    if action == "simpan":
        hasil = ai_tambah_servis(**unit_data)
        waktu_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        teks_sukses = (
            f"✅ <b>UNIT BERHASIL DISIMPAN KE DASHBOARD!</b>\n"
            f"----------------------------------\n"
            f"📱 <b>Device:</b> {unit_data['device']}\n"
            f"👤 <b>Pelanggan:</b> {unit_data['nama']}\n"
            f"📞 <b>No. WA:</b> {unit_data['wa']}\n"
            f"🔧 <b>Kerusakan:</b> {unit_data['kerusakan']}\n"
            f"👨‍🔧 <b>Teknisi:</b> {unit_data['teknisi']}\n"
            f"💰 <b>Estimasi:</b> Rp {unit_data['estimasi']:,}\n"
            f"⏱️ <b>Waktu:</b> {waktu_str}\n"
            f"----------------------------------\n"
            f"✨ <i>Status unit: <b>Analisa</b>. Langsung aktif di Web Dashboard!</i>"
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
        return f"❌ Gagal cek laba: {str(e)}"

def ai_cek_modal():
    """Fungsi hitung modal part (Siklus Berjalan) - Powered by AIS Engine"""
    try:
        data = AISKalkulator.hitung_laba_hari_ini()
        # Kita bisa tambahkan logika khusus modal di engine nanti jika perlu
        # Untuk sekarang kita ambil dari servis langsung di sini atau pindah ke engine
        with db_session() as conn:
            res = conn.execute("SELECT SUM(\"Modal Part\") as total FROM servis WHERE Status='Cash'").fetchone()
            modal = res['total'] or 0
        
        return f"📦 <b>TOTAL MODAL PART (SIKLUS BERJALAN)</b>\n--------------------------\nRp {modal:,.0f}"
    except Exception as e:
        return f"❌ Gagal cek modal: {str(e)}"

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
            query = 'SELECT *, rowid as id_servis FROM servis WHERE "No. WA" LIKE ? AND "Device" LIKE ? ORDER BY rowid DESC LIMIT 1'
            res = conn.execute(query, (search_wa, search_dev)).fetchone()
        
        if not res:
            return "Maaf Kak, data dengan Nama/WA tersebut belum ditemukan di sistem kami. Pastikan penulisan sudah benar ya Kak. 😊"
        
        status = res['Status'] or 'Proses'
        device = res['Device'] or 'Device'
        kerusakan = res['Analisa Kerusakan'] or '-'
        perbaikan = res['Tindakan Perbaikan'] or '-'
        
        teks = (f"👋 <b>Halo Kak {res['Nama User']}!</b>\n\n"
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
        return f"❌ Maaf, sedang ada gangguan sistem: {str(e)}"

def ai_rekap_harian(mode="total"):
    """Fungsi rekap: bisa 'hari_ini' atau 'total'"""
    try:
        with db_session() as conn:
            if mode == "hari_ini":
                tgl_skrg = datetime.now().strftime("%Y-%m-%d")
                query = "SELECT LOWER(TRIM(Status)) as stts, COUNT(*) as jumlah FROM servis WHERE \"Tanggal Masuk\" = ? GROUP BY stts"
                res = conn.execute(query, (tgl_skrg,)).fetchall()
                judul = f"📊 <b>REKAP UNIT MASUK HARI INI ({tgl_skrg})</b>"
                nb = "<i>NB: Data ini sesuai dengan Tabel Dashboard Hari Ini.</i>"
            else:
                query = "SELECT LOWER(TRIM(Status)) as stts, COUNT(*) as jumlah FROM servis GROUP BY stts"
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
        return f"❌ Gagal rekap: {str(e)}"

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
            db = pymysql.connect(host=os.getenv('MYSQL_HOST', 'localhost'), user=os.getenv('MYSQL_USER', 'root'), password=os.getenv('MYSQL_PASSWORD', ''), database=os.getenv('MYSQL_DB', 'db_ais_systems'), cursorclass=pymysql.cursors.DictCursor)
            cur = db.cursor()
            
            # --- FIX: Multi-word search agar lebih akurat ---
            words = query.split()
            if not words:
                res = []
            else:
                where_clauses = []
                params = []
                for w in words:
                    where_clauses.append("(kategori LIKE %s OR merek LIKE %s OR jenis_barang LIKE %s OR jenis_device LIKE %s)")
                    params.extend([f"%{w}%", f"%{w}%", f"%{w}%", f"%{w}%"])
                
                sql = f"SELECT * FROM data_sparepart WHERE {' AND '.join(where_clauses)} LIMIT 10"
                cur.execute(sql, params)
                res = cur.fetchall()
            db.close()
            
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
    if ALLOWED_TELEGRAM_IDS and user_id not in ALLOWED_TELEGRAM_IDS: return
    if await cek_proses_tambah_unit_telegram(update): return

    try:
        # Gunakan AIS Engine untuk logika respons
        jawaban = AISBotLogic.proses_pesan_manajer(user_text)
        await update.message.reply_text(jawaban, parse_mode='HTML')
    except Exception as e:
        print(f"[ERROR MANAJER]: {str(e)}")
        await update.message.reply_text(f"🤖 Manajer Error: {str(e)}")

async def handle_message_akuntan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if ALLOWED_TELEGRAM_IDS and user_id not in ALLOWED_TELEGRAM_IDS: return
    if await cek_proses_tambah_unit_telegram(update): return

    try:
        # Gunakan AIS Engine untuk logika respons
        jawaban = AISBotLogic.proses_pesan_akuntan(user_text)
        await update.message.reply_text(jawaban, parse_mode='HTML')
    except Exception as e:
        print(f"[ERROR AKUNTAN]: {str(e)}")
        await update.message.reply_text(f"🤖 Akuntan Error: {str(e)}")

async def handle_message_cs(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if await cek_proses_tambah_unit_telegram(update): return
    await update.message.reply_text("🔎 Sedang mengecek data sparepart... Mohon tunggu ya Bos.")
    jawaban = ai_cek_sparepart(update.message.text)
    await update.message.reply_text(jawaban, parse_mode='HTML')

def run_bot(token, handler_func, name):
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


# --- PORTAL PEMBAYARAN SATU PINTU ---
@app.route('/robot_ais/chat', methods=['POST'])
def robot_ais_chat():
    user_text = request.json.get('message', '')
    if not user_text:
        return jsonify({"status": "error", "message": "Pesan kosong."})
    
    try:
        from engine.db_tools import query_sqlite, query_mysql, SCHEMA_PROMPT
        base_prompt = "Tugas: Kamu adalah neng Ais, AI Asisten dari Sukabumi Flasher. Kamu membantu memantau operasional toko. Jawab singkat, ramah, dan suportif layaknya asisten cerdas.\n"
        
        # 1. COBA GEMINI CLOUD TERLEBIH DAHULU (CEPAT)
        try:
            if 'client_gemini' in globals() and client_gemini:
                chat = client_gemini.chats.create(
                    model='gemini-flash-latest',
                    config={
                        "tools": [query_sqlite, query_mysql, ai_tambah_servis],
                        "system_instruction": base_prompt + SCHEMA_PROMPT,
                        "temperature": 0.2
                    }
                )
                response_gemini = chat.send_message(user_text)
                return jsonify({"status": "success", "text": response_gemini.text})
            else:
                raise Exception("Client Gemini tidak aktif atau tidak ditemukan.")
        except Exception as err_gemini:
            print(f"[INFO] Gemini Cloud gagal/limit ({err_gemini}). Mengalihkan ke Ollama Localhost...")
            
            # 2. JIKA GAGAL (KARENA LIMIT/KONEKSI), GUNAKAN OLLAMA LOCALHOST (CADANGAN)
            try:
                import ollama
            except ImportError:
                import subprocess, sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
                import ollama
                
            messages = [
                {"role": "system", "content": base_prompt + SCHEMA_PROMPT},
                {"role": "user", "content": user_text}
            ]
            
            # Panggil Ollama dengan tools
            response = ollama.chat(
                model='gemma4',
                messages=messages,
                tools=[query_sqlite, query_mysql, ai_tambah_servis]
            )
            
            # Jika Ollama memutuskan untuk memanggil tool (query database)
            if response.message.tool_calls:
                # Tambahkan respons awal ke history
                messages.append({
                    'role': response.message.role,
                    'content': response.message.content or "",
                    'tool_calls': [
                        {
                            'function': {
                                'name': t.function.name,
                                'arguments': t.function.arguments
                            }
                        } for t in response.message.tool_calls
                    ]
                })
                
                for tool in response.message.tool_calls:
                    tool_name = tool.function.name
                    args = tool.function.arguments
                    
                    result = "Fungsi tidak dikenali"
                    try:
                        if tool_name == 'query_sqlite':
                            result = query_sqlite(**args)
                        elif tool_name == 'query_mysql':
                            result = query_mysql(**args)
                        elif tool_name == 'ai_tambah_servis':
                            result = ai_tambah_servis(**args)
                    except Exception as ex:
                        result = f"Error DB Tool: {ex}"
                    
                    # Masukkan hasil database ke pesan untuk dibaca Gemma
                    messages.append({
                        "role": "tool",
                        "content": str(result),
                        "name": tool_name
                    })
                    
                # Minta Gemma merangkum jawaban akhir berdasarkan hasil database
                final_response = ollama.chat(
                    model='gemma4',
                    messages=messages
                )
                reply = final_response.message.content
            else:
                reply = response.message.content
                
            return jsonify({"status": "success", "text": reply})
            
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"[ROBOT AIS ERROR]: {err_msg}")
        return jsonify({"status": "error", "message": f"Error System: {str(e)}"})



# ==============================================================================
# 10. APP RUNNER (if __name__ == '__main__')
# ==============================================================================

if __name__ == '__main__':
    init_db()  # Initialize database tables once
    import shutil
    import os
    from datetime import datetime
    try:
        os.makedirs('backups/startup_backups', exist_ok=True)
        waktu = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy('sukabumi_flasher.db', f'backups/startup_backups/sukabumi_flasher_backup_{waktu}.db')
        print(f"[INFO] Auto-Backup SQLite berhasil dibuat: {waktu}")
    except Exception as e:
        print(f"[WARNING] Gagal membuat auto-backup: {e}")
    with app.app_context():
        get_db()
    
    # Jalankan Bot di background thread
    # threading.Thread(target=run_bot, args=(TOKEN_MANAJER, handle_message_manajer, "MANAJER"), daemon=True).start()
    threading.Thread(target=run_bot, args=(TOKEN_AKUNTAN, handle_message_akuntan, "AKUNTAN"), daemon=True).start()
    threading.Thread(target=run_bot, args=(TOKEN_CS, handle_message_cs, "CS"), daemon=True).start()
    threading.Thread(target=run_bot, args=(TOKEN_SPAREPART, handle_message_sparepart, "SPAREPART"), daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)


