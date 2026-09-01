import threading
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, session, url_for

from extensions import db_session, get_db
from helpers import cek_dan_kirim_milestone, kirim_notif_kas_masuk, kirim_notif_unit_baru
from utils import admin_required, login_required, permission_required


ALLOWED_STATUSES = {
    'Analisa', 'Konfirmasi', 'Wait Part', 'Repair', 'Done', 'Cash',
    'Garansi', 'Klaim Garansi', 'Selesai Klaim', 'Garansi Void',
    'Cancel', 'Failed', 'Refund',
}
INITIAL_STATUSES = {'Analisa', 'Konfirmasi', 'Wait Part', 'Repair', 'Garansi'}

def _non_negative_int(raw_value, field_name):
    if raw_value is None or str(raw_value).strip() == '':
        return 0
    normalized = str(raw_value).strip().replace('Rp', '').replace('.', '').replace(',', '')
    try:
        value = int(normalized)
    except ValueError as exc:
        raise ValueError(f'{field_name} harus berupa angka.') from exc
    if value < 0:
        raise ValueError(f'{field_name} tidak boleh negatif.')
    return value

def _technician_names():
    rows = get_db().execute(
        '''SELECT COALESCE(NULLIF(nama_lengkap, ''), username) AS nama
           FROM users
           WHERE LOWER(role) = 'teknisi'
             AND (status IS NULL OR status != 'Nonaktif')
           ORDER BY nama'''
    ).fetchall()
    return [row['nama'] for row in rows if row.get('nama')]

def _sweetalert_error(title, text):
    return f"""
    <html><head><script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script></head>
    <body style="background:#0b1120; color:white;">
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        Swal.fire({{
            icon: 'error',
            title: '{title}',
            text: '{text}',
            background: '#1e293b',
            color: '#f8fafc',
            confirmButtonColor: '#3b82f6'
        }}).then(function() {{
            window.history.back();
        }});
    }});
    </script>
    </body></html>
    """

servis_bp = Blueprint("servis", __name__)

# 6. TRANSAKSI SERVIS (Input, Update, Detail, Delete)
# ==============================================================================

@servis_bp.route('/detail/<int:id>')
@permission_required('servis')
def detail(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    
    if row:
        # Bersihkan nama kolom seperti di dashboard
        s_clean = {k.strip(): v for k, v in dict(row).items()}
        s_clean['id'] = row['id']
        return render_template('detail.html', s=s_clean, daftar_teknisi=_technician_names())
    return "Data tidak ditemukan!"

@servis_bp.route('/update/<int:id>', methods=['POST'])
@permission_required('servis')
def update(id):
    
    conn_check = get_db()
    s_old = conn_check.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    if not s_old: return "Data tidak ditemukan", 404
    
    nama = str(request.form.get('nama_user') or '').strip()
    wa = str(request.form.get('no_wa') or '').strip()
    dev = str(request.form.get('device') or '').strip()
    pw = str(request.form.get('password_hp') or '').strip()
    ana = str(request.form.get('analisa') or '').strip()
    tind = str(request.form.get('tindakan') or '').strip()
    stat = str(request.form.get('status') or '').strip()
    garansi_val = str(request.form.get('masa_garansi') or '1 Bulan').strip()
    tek = str(request.form.get('teknisi') or '').strip()
    m_part_raw = request.form.get('modal_part')
    m_jasa_raw = request.form.get('modal_jasa')

    if not nama or not dev:
        return _sweetalert_error('Gagal Menyimpan', 'Nama pelanggan dan device wajib diisi.')
    if stat not in ALLOWED_STATUSES:
        return _sweetalert_error('Gagal Menyimpan', 'Status servis tidak valid.')
    if garansi_val not in {'1 Bulan', '2 Bulan', '3 Bulan', 'Tanpa Garansi'}:
        return _sweetalert_error('Gagal Menyimpan', 'Masa garansi tidak valid.')

    try:
        est = _non_negative_int(request.form.get('estimasi'), 'Estimasi')
        dp = _non_negative_int(request.form.get('dp'), 'DP')
        h_jual = _non_negative_int(request.form.get('harga_jual'), 'Harga jual')
        m_part = _non_negative_int(m_part_raw, 'Modal part')
        m_jasa = _non_negative_int(m_jasa_raw, 'Modal jasa')
        m_lain = _non_negative_int(request.form.get('lain_lain'), 'Biaya lain-lain')
    except ValueError as exc:
        return _sweetalert_error('Gagal Menyimpan', str(exc).replace("'", "\\'"))
    kelengkapan_list = request.form.getlist('kelengkapan[]')
    kondisi_list = request.form.getlist('kondisi[]')
    kelengkapan_str = ', '.join(kelengkapan_list) if kelengkapan_list else '-'
    kondisi_str = ', '.join(kondisi_list) if kondisi_list else '-'
    
    # --- PROTEKSI ROLE (ADMIN vs KASIR vs TEKNISI) ---
    role = session.get('role', 'custom')
    
    # Proteksi Khusus KASIR
    if role == 'kasir':
        if stat == 'Cash' and s_old['status'] not in ['Done', 'Cash']:
            return _sweetalert_error('Akses Kasir Dibatasi', 'Akun Kasir HANYA BISA merubah status ke CASH dari status DONE! Pastikan unit sudah selesai diperbaiki oleh Teknisi terlebih dahulu.')
        if stat == 'Selesai Klaim' and s_old['status'] not in ['Done', 'Garansi', 'Klaim Garansi', 'Selesai Klaim']:
            return _sweetalert_error('Akses Kasir Dibatasi', 'Akun Kasir HANYA BISA merubah status ke SELESAI KLAIM dari status DONE atau GARANSI!')
            
        # Validasi tambahan Kasir: pastikan Teknisi sudah mengisi modal (bukan NULL)
        if stat == 'Cash' and (s_old['modal_part'] is None and s_old['modal_jasa'] is None):
            return _sweetalert_error('Gagal Menyimpan', 'Teknisi belum mengisi Modal Part / Jasa. Minta teknisi melengkapinya sebelum unit ini bisa di-Cash!')
            
        # Pertahankan modal part/jasa lama agar Kasir tidak bisa merubah/menimpa modal toko
        m_part = s_old['modal_part'] or 0
        m_jasa = s_old['modal_jasa'] or 0
        m_lain = s_old['lain_lain'] or 0
        m_part_raw = str(m_part)
        m_jasa_raw = str(m_jasa)
        
    # Proteksi Khusus TEKNISI
    elif role != 'admin':
        if stat in ['Cash', 'Selesai Klaim', 'Refund']:
            return _sweetalert_error('Akses Ditolak', 'Akun Teknisi tidak diizinkan merubah status closing (CASH / SELESAI KLAIM / REFUND)! Proses closing & finansial adalah tugas Kasir atau Admin.')
        # Pertahankan harga jual dan modal agar Teknisi tidak menimpa/merubah data finansial
        h_jual = s_old['harga_jual'] or 0
        m_part = s_old['modal_part'] or 0
        m_jasa = s_old['modal_jasa'] or 0
        m_lain = s_old['lain_lain'] or 0
        m_part_raw = str(m_part)
        m_jasa_raw = str(m_jasa)
    # ------------------------------------------------
    
    # --- VALIDASI ATURAN TOKO ---
    if stat in ['Done', 'Cash', 'Selesai Klaim', 'Refund']:
        if not tind or tind.strip() == '' or tind.strip() == '-':
            return _sweetalert_error('Gagal Menyimpan', 'Ketika status diubah ke Done, Cash, Selesai Klaim, atau Refund, Kolom Tindakan WAJIB diisi dengan benar.')
            
    if stat == 'Done':
        if not tek or tek.strip() == '' or tek.strip() == '-':
            return _sweetalert_error('Gagal Menyimpan', 'Ketika status diubah ke Done, Nama Teknisi penanggung jawab WAJIB dipilih/diisi dengan benar!')

    if stat == 'Cash':
        if not m_part_raw or not m_jasa_raw or m_part_raw.strip() == '' or m_jasa_raw.strip() == '':
            return _sweetalert_error('Gagal Menyimpan', 'Ketika status diubah ke Cash, Kolom Modal Part dan Modal Jasa WAJIB diisi.')
            
    if stat == 'Selesai Klaim':
        h_jual = 0
    # ----------------------------
    
    # 2. Hitung Laba
    laba_final = h_jual - m_part - m_jasa - m_lain if stat == 'Cash' else 0

    try:
        with db_session() as conn:
            cursor = conn.execute('''
                UPDATE servis SET
                    nama_user = %s, no_wa = %s, device = %s, password = %s,
                    analisa_kerusakan = %s, tindakan_perbaikan = %s,
                    estimasi_biaya = %s, dp = %s, harga_jual = %s,
                    modal_part = %s, modal_jasa = %s, lain_lain = %s,
                    laba_kotor = %s, status = %s, masa_garansi = %s,
                    teknisi = %s, kelengkapan = %s, kondisi_fisik = %s,
                    updated_at = %s
                WHERE id = %s
            ''', (
                nama, wa, dev, pw, ana, tind, est, dp, h_jual,
                m_part, m_jasa, m_lain, laba_final, stat, garansi_val,
                tek, kelengkapan_str, kondisi_str,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id,
            ))
            if cursor.rowcount != 1:
                raise LookupError('Unit servis tidak ditemukan saat update.')
        print(f'[OK] Berhasil Update Unit: {dev}')
    except Exception as exc:
        print(f'[ERROR] Gagal Update: {exc}')
        return 'Gagal menyimpan perubahan unit servis.', 500
    # CEK MILESTONE OTOMATIS JIKA STATUS CASH (Balikin ke Background biar kenceng)
    if stat == 'Cash':
        kirim_notif_kas_masuk(dev, nama, h_jual, laba_final, tek)
        threading.Thread(target=cek_dan_kirim_milestone, daemon=True).start()

    if stat == 'Done':
        return redirect(url_for('dashboard.dashboard', wa_done=id))
    elif stat == 'Cash':
        if s_old['status'] != 'Cash':
            return redirect(url_for('dashboard.dashboard', cash_done=id))

    return redirect(url_for('dashboard.dashboard'))

@servis_bp.route('/input_baru')
@permission_required('servis')
def input_baru():
    return render_template('input.html', daftar_teknisi=_technician_names())

@servis_bp.route('/preview')
@login_required
def preview_input():
    return render_template('preview_input.html', daftar_teknisi=_technician_names())

@servis_bp.route('/preview_update')
@login_required
def preview_update():
    return render_template('preview_update.html')



@servis_bp.route('/tambah', methods=['GET', 'POST'])
@permission_required('servis')
def tambah():
    if request.method == 'GET':
        return render_template('input.html', daftar_teknisi=_technician_names())
        
    tgl_hari_ini = datetime.now().strftime('%Y-%m-%d')
    n_user = str(request.form.get('nama_user') or '').strip()
    wa = str(request.form.get('no_wa') or '').strip()
    dev = str(request.form.get('device') or '').strip()
    pw = str(request.form.get('password_hp') or '').strip()
    ana = str(request.form.get('analisa') or '').strip() or '-'
    tindakan = str(request.form.get('tindakan') or '').strip() or '-'
    tek = str(request.form.get('teknisi') or '').strip() or '-'
    status_input = str(request.form.get('status') or 'Analisa').strip()

    if not n_user or not dev:
        return _sweetalert_error('Gagal Menyimpan', 'Nama pelanggan dan device wajib diisi.')
    if status_input not in INITIAL_STATUSES:
        return _sweetalert_error('Gagal Menyimpan', 'Status awal servis tidak valid.')

    try:
        est = _non_negative_int(request.form.get('estimasi'), 'Estimasi')
        dp = _non_negative_int(request.form.get('dp'), 'DP')
    except ValueError as exc:
        return _sweetalert_error('Gagal Menyimpan', str(exc).replace("'", "\\'"))

    kelengkapan_list = request.form.getlist('kelengkapan[]')
    kondisi_list = request.form.getlist('kondisi[]')
    kelengkapan_str = ', '.join(kelengkapan_list) if kelengkapan_list else '-'
    kondisi_str = ', '.join(kondisi_list) if kondisi_list else '-'

    try:
        with db_session() as conn:
            cursor = conn.execute('''
                INSERT INTO servis (
                    tanggal_masuk, device, nama_user, no_wa,
                    password, analisa_kerusakan, tindakan_perbaikan,
                    status, teknisi, estimasi_biaya, dp, updated_at,
                    kelengkapan, kondisi_fisik
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                tgl_hari_ini, dev, n_user, wa, pw, ana, tindakan,
                status_input, tek, est, dp,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                kelengkapan_str, kondisi_str,
            ))
            new_id = cursor.lastrowid
    except Exception as exc:
        print(f'[ERROR] Gagal menyimpan unit baru: {exc}')
        return 'Gagal menyimpan unit servis.', 500

    kirim_notif_unit_baru(dev, ana, tindakan, kelengkapan_str, kondisi_str)
    return redirect(url_for(
        'dashboard.dashboard',
        new_unit_id=new_id,
        new_user=n_user,
        new_dev=dev,
    ))

# FUNGSI HAPUS DATA
@servis_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    with db_session() as conn:
        conn.execute('DELETE FROM servis WHERE id = %s', (id,))
    return redirect(url_for('dashboard.dashboard'))


@servis_bp.route('/simpan_sparepart', methods=['POST'])
@permission_required('sparepart')
def simpan_sparepart():
    
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
        with db_session() as db:
            if id_sparepart:
                db.execute("""
                    UPDATE data_sparepart
                    SET tanggal_masuk=%s, kategori=%s, merek=%s, jenis_barang=%s, jenis_device=%s, qty=%s, harga_beli=%s, harga_jual=%s
                    WHERE id_sparepart=%s
                """, (tgl, kategori, merek, barang, device, qty, beli, jual, id_sparepart))
            else:
                db.execute("""
                    INSERT INTO data_sparepart (tanggal_masuk, kategori, merek, jenis_barang, jenis_device, qty, harga_beli, harga_jual)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (tgl, kategori, merek, barang, device, qty, beli, jual))
    except Exception as e:
        print(f"[ERROR] Gagal simpan sparepart: {e}")
        return "Gagal menyimpan data sparepart.", 500
        
    return redirect(url_for('dashboard.dashboard') + '#tabel-sparepart')

@servis_bp.route('/delete_sparepart/<int:id>', methods=['POST'])
@admin_required
def delete_sparepart(id):
    with db_session() as db:
        db.execute("DELETE FROM data_sparepart WHERE id_sparepart=%s", (id,))
    return redirect(url_for('dashboard.dashboard') + '#tabel-sparepart')

# ==========================================================
#                  AI AGENT TELEGRAM LOGIC
# ==========================================================

PENDING_UNITS = {}
PENDING_LOCK = threading.Lock()



# ==============================================================================
