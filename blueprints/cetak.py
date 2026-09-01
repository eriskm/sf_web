import os
import threading
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

from engine.kalkulator import AISKalkulator
from extensions import get_db, db_session
from helpers import ai_tambah_servis, kirim_laporan_telegram
from services.bookkeeping import calculate_system_balance
from utils import (
    generate_internal_access_token,
    login_required,
    permission_required,
    verify_internal_access_token,
)

try:
    from html2image import Html2Image
except ImportError:
    Html2Image = None


cetak_bp = Blueprint('cetak', __name__)


def _renderer_output_dir():
    output_dir = os.path.join(current_app.root_path, 'static', 'nota_digital')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def _render_html_image(html_content, filename):
    if Html2Image is None:
        raise RuntimeError('Dependency html2image belum tersedia.')
    renderer = Html2Image(output_path=_renderer_output_dir())
    renderer.screenshot(html_str=html_content, save_as=filename)


def _dashboard_snapshot_url():
    base_url = os.getenv('INTERNAL_BASE_URL', 'http://127.0.0.1:5000').rstrip('/')
    token = generate_internal_access_token('dashboard')
    from urllib.parse import quote
    return f"{base_url}{url_for('dashboard.dashboard')}?bot={quote(token)}"


def _capture_dashboard_report(prefix, report_type):
    if Html2Image is None:
        raise RuntimeError('Dependency html2image belum tersedia.')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{prefix}_{timestamp}.png'
    renderer = Html2Image(
        output_path=_renderer_output_dir(),
        custom_flags=[
            '--headless=new',
            '--disable-gpu',
            '--window-size=1050,720',
            '--default-background-color=ffffffff',
        ],
    )
    renderer.screenshot(url=_dashboard_snapshot_url(), save_as=filename)
    report_path = os.path.join(_renderer_output_dir(), filename)
    threading.Thread(
        target=kirim_laporan_telegram,
        args=(report_path, report_type),
        daemon=True,
    ).start()
    return report_path

# 8. NOTA, CETAK & ENGINE RENDER (Cetak Termal, WA Bridge)
# ==============================================================================

@cetak_bp.route('/milestone_preview')
def milestone_preview():
    # Akses khusus bot
    if not verify_internal_access_token(request.args.get('bot'), 'milestone'):
        return "Akses Ditolak", 403
        
    conn = get_db()
    laba_servis = conn.execute("SELECT SUM(laba_kotor) FROM servis WHERE status='Cash' AND (COALESCE(modal_part, 0) > 0 OR COALESCE(modal_jasa, 0) > 0 OR COALESCE(lain_lain, 0) > 0)").fetchone()[0] or 0
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
    return render_template('milestone_view.html', 
                           laba_kotor=laba_kotor, gaji=gaji, ops=ops, 
                           total_beban=total_beban, laba_bersih=laba_bersih,
                           p_gaji=p_gaji, p_ops=p_ops, 
                           status_text=status_text, status_class=status_class)

@cetak_bp.route('/cetak_nota/<int:id>')
@login_required
def cetak_nota(id):
    
    conn = get_db()
    s = conn.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    if not s:
        return "Data tidak ditemukan", 404
    
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

@cetak_bp.route('/cetak_penerimaan/<int:id>')
@login_required
def cetak_penerimaan(id):
    conn = get_db()
    s = conn.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    if not s:
        return "Data tidak ditemukan", 404
    tgl_cetak = datetime.now().strftime('%d/%m/%Y')
    jam_cetak = datetime.now().strftime('%H:%M')
    return render_template('nota_penerimaan_termal.html', s=s, tgl_cetak=tgl_cetak, jam_cetak=jam_cetak)

@cetak_bp.route('/generate_nota_image/<int:id>')
@login_required
def generate_nota_image(id):
    conn = get_db()
    s = conn.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    if not s:
        return "Data tidak ditemukan", 404
    
    garansi = request.args.get('garansi', 'Tanpa Garansi')
    tgl_akhir = request.args.get('tgl_akhir', '-')
    tgl_sekarang = datetime.now().strftime('%d/%m/%Y')
    jam_sekarang = datetime.now().strftime('%H:%M')

    invoice_no = f"SF-{datetime.now().strftime('%y%m%d')}-{id:03d}"
    
    imei_sn = '-'
    teknisi = s.get('teknisi') if s.get('teknisi') else 'Tim SF'
    kondisi_awal = s.get('analisa_kerusakan') if s.get('analisa_kerusakan') else '-'
    tindakan = s.get('tindakan_perbaikan') if s.get('tindakan_perbaikan') else '-'
    
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
        _render_html_image(html_content, filename)
        import time
        return url_for('static', filename=f'nota_digital/{filename}', v=int(time.time()))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "Gagal membuat gambar nota.", 500

@cetak_bp.route('/generate_penerimaan_image/<int:id>')
@login_required
def generate_penerimaan_image(id):
    conn = get_db()
    s = conn.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    if not s:
        return "Data tidak ditemukan", 404
    
    tgl_sekarang = datetime.now().strftime('%d/%m/%Y')
    jam_sekarang = datetime.now().strftime('%H:%M')

    try:
        est_val = int(s['estimasi_biaya']) if s['estimasi_biaya'] else 0
    except:
        est_val = 0
        
    try:
        dp_val = int(s['dp']) if 'dp' in s and s['dp'] else 0
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
        _render_html_image(html_content, filename)
        import time
        return url_for('static', filename=f'nota_digital/{filename}', v=int(time.time()))
    except Exception as e:
        print(f"Error Generate Penerimaan: {e}")
        return "Gagal membuat gambar nota penerimaan.", 500

@cetak_bp.route('/nota_bridge/<int:id>')
@login_required
def nota_bridge(id):
    
    conn = get_db()
    s = conn.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    
    if not s: return "Data tidak ditemukan", 404
    
    type_nota = request.args.get('type', 'penerimaan')
    garansi = request.args.get('garansi', '')
    tgl_akhir = request.args.get('tgl_akhir', '')
    
    # Siapkan URL Gambar & Print
    if type_nota == 'penerimaan':
        img_url = url_for('cetak.generate_penerimaan_image', id=id)
        print_url = url_for('cetak.cetak_penerimaan', id=id)
        tgl = datetime.now().strftime('%d/%m/%Y')
        jam = datetime.now().strftime('%H:%M')
        keluhan = s['analisa_kerusakan'] or s['tindakan_perbaikan'] or '-'
        is_klaim = (s['status'] in ['Garansi', 'Klaim Garansi'])
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
            f"Status : *{'🛡️ Klaim Garansi' if is_klaim else s['status']}*\n\n"
            f"Pelanggan : *{s['nama_user']}*\n\n"
            f"Device : *{s['device']}*\n\n"
            f"Keluhan/Klaim : *{keluhan}*{chk_wa}\n\n"
            f"*Keterangan:*\n"
            f"{ket_teks}\n"
            f"*PERHATIAN:*\n"
            f"• Nota ini bukan bukti pembayaran."
        )
    else:
        img_url = url_for('cetak.generate_nota_image', id=id, garansi=garansi, tgl_akhir=tgl_akhir)
        print_url = url_for('cetak.cetak_nota', id=id, garansi=garansi)
        teks_wa = (
            f"Halo Kak *{s['nama_user']}* 👋\n\n"
            f"Terima kasih telah mempercayakan perbaikan *{s['device']}* kepada *Sukabumi Flasher*.\n\n"
            f"Sebagai bentuk komitmen kami terhadap kualitas layanan, \n"
            f"kami lampirkan *Nota Garansi Digital* sebagai bukti garansi sekaligus riwayat servis perangkat Anda.\n\n"
            f"Mohon simpan nota ini dengan baik. \n"
            f"Apabila selama masa garansi terdapat kendala yang berkaitan dengan hasil servis, jangan ragu untuk menghubungi kami. Tim kami akan dengan senang hati membantu.\n\n"
            f"Terima kasih atas kepercayaan yang telah diberikan kepada Sukabumi Flasher. Semoga perangkat Anda selalu berfungsi dengan baik dan nyaman digunakan.\n\n"
            f"Salam hangat,\n"
            f"*Sukabumi Flasher* 🙏"
        )

    # Bersihkan nomor WA
    no_wa = s['no_wa'].replace(' ', '').replace('-', '').replace('+', '')
    if no_wa.startswith('0'): no_wa = '62' + no_wa[1:]

    return render_template('bridge_nota.html', 
                           id=id, 
                           type=type_nota, 
                           img_url=img_url, 
                           print_url=print_url, 
                           no_wa=no_wa, 
                           teks_wa=teks_wa)

@cetak_bp.route('/wa_selesai/<int:id>')
@login_required
def wa_selesai(id):
    conn = get_db()
    s = conn.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    
    if not s: return redirect(url_for('dashboard.dashboard'))
    
    no_wa = s['no_wa'] or ''
    no_wa = no_wa.replace(' ', '').replace('-', '').replace('+', '')
    if no_wa.startswith('0'): no_wa = '62' + no_wa[1:]
    
    nama = s['nama_user']
    device = s['device']
    
    teks = f"Halo kak *{nama}* 👋\n\nInfo dari *Sukabumi Flasher*, unit *{device}* kakak sudah *Selesai* diperbaiki dan sudah bisa diambil di toko ya kak. ✅\n\nTerima kasih! 🙏"
    
    import urllib.parse
    teks_encoded = urllib.parse.quote(teks)
    
    return redirect(f"https://api.whatsapp.com/send?phone={no_wa}&text={teks_encoded}")

@cetak_bp.route('/engine')
@permission_required('keuangan')
def engine_dashboard():
    """Halaman Visual Utama AIS Engine (Command Center)"""
    
    # Ambil data live dari Engine
    data = AISKalkulator.hitung_laba_hari_ini()
    bagi_hasil = AISKalkulator.hitung_bagi_hasil(data['laba_bersih'])
    milestone = AISKalkulator.cek_milestone()
    
    return render_template('engine_dashboard.html', 
                           data=data, 
                           bagi_hasil=bagi_hasil, 
                           milestone=milestone)

@cetak_bp.route('/preview-teknisi')
@login_required
def preview_teknisi():
    return render_template('preview_teknisi_terbaik.html')

@cetak_bp.route('/preview-header')
@login_required
def preview_header():
    return render_template('preview_header_options.html')



# ==============================================================================
# 9. TELEGRAM BOT & BACKGROUND WORKER (Telebot, Milestone)
# ==============================================================================

@cetak_bp.route('/telegram_tutup_buku', methods=['POST'])
@permission_required('tutup_buku')
def telegram_tutup_buku():
    try:
        _capture_dashboard_report('Laporan_Tutup', 'TUTUP')
        return 'Pengiriman laporan tutup buku dijadwalkan', 202
    except RuntimeError as exc:
        current_app.logger.warning("Layanan laporan tidak tersedia: %s", exc)
        return "Layanan laporan tidak tersedia.", 503
    except Exception as exc:
        print(f'[REPORT] Gagal membuat laporan tutup buku: {exc}')
        return 'Gagal membuat laporan tutup buku.', 500

@cetak_bp.route('/eksekusi_db', methods=['POST'])
@permission_required('tutup_buku')
def eksekusi_db():
    if session.get('role') != 'admin':
        return "Akses ditolak: Hanya admin yang boleh melakukan tutup buku", 403
        
    try:
        data = request.get_json(silent=True) or {}
        uang_fisik_raw = data.get('uang_fisik')
        if uang_fisik_raw is None or uang_fisik_raw == '':
            return "Waduh, nominal uang fisik kosong bro!", 400
        uang_fisik = int(uang_fisik_raw)
        if uang_fisik < 0:
            return "Nominal uang fisik tidak boleh negatif.", 400

        # Gunakan SATU transaksi MySQL murni
        with db_session() as conn:
            total_saldo, laba_bersih = calculate_system_balance(conn, lock=True)
            cycle_date = datetime.now().strftime('%Y-%m-%d')
            last_cycle = conn.execute(
                'SELECT tanggal FROM kas_utama ORDER BY id DESC LIMIT 1 FOR UPDATE'
            ).fetchone()
            if last_cycle and str(last_cycle.get('tanggal') or '').startswith(cycle_date):
                return 'Tutup buku untuk hari ini sudah pernah dijalankan.', 409

            if uang_fisik > total_saldo:
                return "Uang fisik melebihi saldo sistem; tutup buku dibatalkan.", 400
            kas_aset_baru = total_saldo - uang_fisik
            data_harian = conn.execute("SELECT * FROM servis FOR UPDATE").fetchall()

            # 1. Pindah Arsip
            counter = 0
            for row in data_harian:
                stts_raw = row.get('status')
                if not stts_raw: continue
                stts = str(stts_raw).strip().lower()

                if stts in ['cash', 'cancel', 'selesai klaim', 'garansi void', 'refund']:
                    no_id = row.get('id')
                    nama  = row.get('nama_user')
                    wa    = row.get('no_wa')
                    unit  = row.get('device')
                    aksi  = row.get('tindakan_perbaikan')
                    biaya = row.get('harga_jual')

                    sql_arsip = """INSERT INTO arsip_pelanggan 
                                   (nama_user, no_wa, device, tindakan, harga_jual, status_final) 
                                   VALUES (%s, %s, %s, %s, %s, %s)"""
                    cur_arsip = conn.execute(sql_arsip, (nama, wa, unit, aksi, biaya, stts.upper()))
                    
                    if stts == 'cash':
                        id_arsip = cur_arsip.lastrowid
                        m_garansi_raw = row.get('masa_garansi') or "1 Bulan"
                        try:
                            m_garansi_num = int(m_garansi_raw.split()[0])
                        except:
                            m_garansi_num = 1
                        
                        sql_garansi = """INSERT INTO arsip_garansi 
                                         (id_arsip, nama_user, device, tgl_mulai, tgl_akhir) 
                                         VALUES (%s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s MONTH))"""
                        conn.execute(sql_garansi, (id_arsip, nama, unit, m_garansi_num))
                        
                    # Copy ke arsip_servis
                    try:
                        kerusakan_val = row.get('analisa_kerusakan') or ''
                        m_part_val = row.get('modal_part') or 0
                        m_jasa_val = row.get('modal_jasa') or 0
                        laba_val = row.get('laba_kotor') or 0
                        tek_val = row.get('teknisi') or ''
                        kelengkapan_val = row.get('kelengkapan') or '-'
                        kondisi_val = row.get('kondisi_fisik') or '-'
                        tgl_masuk_val = row.get('tanggal_masuk') or ''
                        tgl_keluar_val = datetime.now().strftime('%Y-%m-%d')
                        conn.execute("""
                            INSERT INTO arsip_servis (
                                tanggal_masuk, tanggal_keluar, nama_user, wa, device, 
                                kerusakan, tindakan, modal_part, modal_jasa, harga_jual, 
                                laba_kotor, teknisi, kelengkapan, kondisi_fisik
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (tgl_masuk_val, tgl_keluar_val, nama, wa, unit, kerusakan_val, aksi, m_part_val, m_jasa_val, biaya, laba_val, tek_val, kelengkapan_val, kondisi_val))
                    except Exception as ex_arsip:
                        print(f"Error arsip lokal: {ex_arsip}")
                        raise Exception(f"Gagal memindahkan ke arsip lokal: {ex_arsip}")

                    conn.execute("DELETE FROM servis WHERE id = %s", (no_id,))
                    counter += 1

            # 2. Update Master Kas
            master_cursor = conn.execute("UPDATE master_kas SET kas_kecil_laci = %s, kas_aset_pengelola = %s ORDER BY id_kas DESC LIMIT 1", (uang_fisik, kas_aset_baru))
            if master_cursor.rowcount == 0:
                conn.execute(
                    "INSERT INTO master_kas (kas_kecil_laci, kas_aset_pengelola) VALUES (%s, %s)",
                    (uang_fisik, kas_aset_baru),
                )
            
            # 3. Reset Papan Tulis
            conn.execute("DELETE FROM transaksi_tambahan")
            tgl_hari_ini = datetime.now().strftime("%Y-%m-%d")
            conn.execute("""
                INSERT INTO transaksi_tambahan (tanggal, uraian, jenis, nominal) 
                VALUES (%s, 'MODAL KAS KECIL (LACI)', 'Masuk', %s)
            """, (tgl_hari_ini, uang_fisik))

            conn.execute(
                """INSERT INTO kas_utama (tanggal, saldo_awal, saldo_akhir, total_laba_bersih)
                   VALUES (%s, %s, %s, %s)""",
                (cycle_date, kas_aset_baru, kas_aset_baru, laba_bersih),
            )

        return f"Siklus Selesai! {counter} data diarsip. Kas terkunci.", 200

    except Exception as e:
        print(f"ERROR DB: {str(e)}") 
        return "Gagal mengeksekusi tutup buku.", 500
@cetak_bp.route('/telegram_buka_buku', methods=['POST'])
@permission_required('tutup_buku')
def telegram_buka_buku():
    try:
        _capture_dashboard_report('Laporan_Buka', 'BUKA')
        return 'Pengiriman laporan buka buku dijadwalkan', 202
    except RuntimeError as exc:
        current_app.logger.warning("Layanan laporan tidak tersedia: %s", exc)
        return "Layanan laporan tidak tersedia.", 503
    except Exception as exc:
        print(f'[REPORT] Gagal membuat laporan buka buku: {exc}')
        return 'Gagal membuat laporan buka buku.', 500

@cetak_bp.route('/robot_ais/chat', methods=['POST'])
@permission_required('keuangan')
def robot_ais_chat():
    payload = request.get_json(silent=True) or {}
    user_text = str(payload.get('message', '')).strip()
    if not user_text:
        return jsonify({"status": "error", "message": "Pesan kosong."})
    
    try:
        from engine.db_tools import query_mysql, SCHEMA_PROMPT
        base_prompt = "Tugas: Kamu adalah neng Ais, AI Asisten dari Sukabumi Flasher. Kamu membantu memantau operasional toko. Jawab singkat, ramah, dan suportif layaknya asisten cerdas.\n"

        client_gemini = None
        api_key = os.getenv('GEMINI_API_KEY', '').strip()
        if api_key:
            try:
                from google import genai
                client_gemini = genai.Client(api_key=api_key)
            except Exception as init_error:
                print(f"[AI] Gemini tidak dapat diinisialisasi: {init_error}")
        
        # 1. COBA GEMINI CLOUD TERLEBIH DAHULU (CEPAT)
        try:
            if client_gemini:
                chat = client_gemini.chats.create(
                    model='gemini-flash-latest',
                    config={
                        "tools": [query_mysql, ai_tambah_servis],
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
                return jsonify({"status": "error", "message": "Ollama belum terpasang pada server."}), 503
                
            messages = [
                {"role": "system", "content": base_prompt + SCHEMA_PROMPT},
                {"role": "user", "content": user_text}
            ]
            
            # Panggil Ollama dengan tools
            response = ollama.chat(
                model='gemma4',
                messages=messages,
                tools=[query_mysql, ai_tambah_servis]
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
                        if tool_name == 'query_mysql':
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
        return jsonify({"status": "error", "message": "Layanan AI sedang bermasalah."}), 500



# ==============================================================================
# 10. APP RUNNER (if __name__ == '__main__')
# ==============================================================================



