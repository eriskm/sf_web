from datetime import datetime

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

from extensions import get_db
from utils import login_required, verify_internal_access_token



dashboard_bp = Blueprint("dashboard", __name__)

# 5. DASHBOARD & PENCARIAN (Halaman Utama, API Search)
# ==============================================================================

@dashboard_bp.route('/api/check_update')
@login_required
def check_update():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(updated_at) as last_update FROM servis')
        res = cursor.fetchone()
        
        # We need a UNIX timestamp or a string that the frontend can compare
        # MySQL returns a datetime object for updated_at
        last_update = 0
        if res and res['last_update']:
            import time
            last_update = res['last_update'].timestamp()
            
        return jsonify({"status": "success", "last_update": last_update})
    except Exception:
        current_app.logger.exception("Gagal memeriksa pembaruan dashboard.")
        return jsonify({"status": "error", "message": "Pemeriksaan pembaruan gagal."}), 500

@dashboard_bp.route('/dashboard')
def dashboard():
    internal_access = verify_internal_access_token(request.args.get('bot'), 'dashboard')
    if 'user' not in session and not internal_access:
        return redirect(url_for('auth.index'))
    
    # JIKA MODE MILESTONE (KHUSUS BOT)
    if request.args.get('view') == 'milestone':
        conn = get_db()
        # SYNC LOGIC: Hitung semua Cash yang sudah diisi Modalnya (Siklus Sekarang)
        laba_servis = conn.execute("SELECT SUM(laba_kotor) FROM servis WHERE status='Cash' AND (COALESCE(modal_part, 0) > 0 OR COALESCE(modal_jasa, 0) > 0 OR COALESCE(lain_lain, 0) > 0)").fetchone()[0] or 0
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
        query_conditions.append('tanggal_masuk LIKE %s')
        params.append(f'%{tgl_filter}%')
    if q_filter:
        query_conditions.append('(nama_user LIKE %s OR device LIKE %s)')
        params.append(f'%{q_filter}%')
        params.append(f'%{q_filter}%')
    
    where_clause = ""
    if query_conditions:
        where_clause = "WHERE " + " AND ".join(query_conditions)

    # 2. HITUNG TOTAL DATA & PAGINATION
    total_data = conn.execute(f'SELECT COUNT(*) FROM servis {where_clause}', params).fetchone()[0]
    total_pages = (total_data + per_page - 1) // per_page

    # 3. AMBIL DATA SERVIS UNTUK TABEL UTAMA
    order_logic = "ORDER BY CASE WHEN status = 'Cash' THEN 0 WHEN status = 'Cancel' THEN 1 ELSE 2 END, tanggal_masuk DESC, id DESC"
    query = f'SELECT * FROM servis {where_clause} {order_logic} LIMIT %s OFFSET %s'
    servis_raw = conn.execute(query, params + [per_page, offset]).fetchall()

    # 3.5 AMBIL REKAP STATUS UNTUK DIAGRAM BATANG
    status_counts = conn.execute(f'SELECT status, COUNT(*) as count FROM servis {where_clause} GROUP BY status', params).fetchall()
        
    status_data = {
        'Analisa': 0, 'Konfirmasi': 0, 'Wait Part': 0, 'Repair': 0, 
        'Done': 0, 'Failed': 0, 'Garansi': 0, 'Refund': 0, 
        'Cancel': 0, 'Cash': 0
    }
    for row in status_counts:
        st_raw = row.get('status')
        if st_raw:
            st_key = st_raw.strip().title()
            if st_key in status_data:
                status_data[st_key] += row['count']
            elif st_key == "Wait Part":
                status_data["Wait Part"] += row['count']

    # 3.8 AMBIL DATA AUTOCOMPLETE
    semua_nama = conn.execute('SELECT DISTINCT nama_user FROM servis WHERE nama_user IS NOT NULL').fetchall()
    semua_device = conn.execute('SELECT DISTINCT device FROM servis WHERE device IS NOT NULL').fetchall()
    autocomplete_data = list(set([row['nama_user'] for row in semua_nama] + [row['device'] for row in semua_device]))

    # 3.9 AMBIL STATISTIK JENIS KERUSAKAN DENGAN KATEGORISASI (LEVEL 1)
    kerusakan_raw = conn.execute('''
        SELECT LOWER(TRIM(analisa_kerusakan)) as k_text
        FROM servis 
        WHERE analisa_kerusakan IS NOT NULL AND TRIM(analisa_kerusakan) != ''
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
    s_cash = conn.execute("SELECT * FROM servis WHERE status = 'Cash' AND (COALESCE(modal_part, 0) > 0 OR COALESCE(modal_jasa, 0) > 0 OR COALESCE(lain_lain, 0) > 0)").fetchall()
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
    total_penjualan = sum(s['harga_jual'] or 0 for s in s_cash)
    saldo_berjalan += total_penjualan
    history_kas.append({'uraian': 'TOTAL PENJUALAN SERVICE', 'debit': total_penjualan, 'kredit': 0, 'saldo': saldo_berjalan})

    # Hitung Modal
    t_modal_barang = sum(s['modal_part'] or 0 for s in s_cash)
    t_modal_jasa = sum(s['modal_jasa'] or 0 for s in s_cash)
    t_modal_lain = sum(s['lain_lain'] or 0 for s in s_cash)
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
    insight_masuk = conn.execute('SELECT COUNT(*) FROM servis WHERE tanggal_masuk = %s', (tgl_hari_ini,)).fetchone()[0]
    insight_selesai = conn.execute('SELECT COUNT(*) FROM servis WHERE updated_at LIKE %s AND Status IN ("Done", "Cash")', (f'{tgl_hari_ini}%',)).fetchone()[0]
    insight_cash = conn.execute("SELECT COUNT(*) FROM servis WHERE updated_at LIKE %s AND Status = 'Cash'", (f'{tgl_hari_ini}%',)).fetchone()[0]
    insight_pending = conn.execute('SELECT COUNT(*) FROM servis WHERE status IN ("Analisa", "Konfirmasi", "Wait Part", "Repair")').fetchone()[0]
    
    total_laba_kotor = total_penjualan - total_modal
    
    best_tech_row = conn.execute('''
        SELECT teknisi, SUM(harga_jual) as revenue, COUNT(*) as jobs
        FROM servis
        WHERE updated_at LIKE %s AND Status = 'Cash' AND teknisi IS NOT NULL AND TRIM(teknisi) != ""
        GROUP BY teknisi
        ORDER BY revenue DESC
        LIMIT 1
    ''', (f'{tgl_hari_ini}%',)).fetchone()
    
    if best_tech_row:
        tech_name = best_tech_row['teknisi']
        user_row = conn.execute('SELECT foto_profil FROM users WHERE LOWER(username) = LOWER(%s) OR LOWER(username) LIKE LOWER(%s) LIMIT 1', (tech_name.strip(), f"%{tech_name.strip()}%")).fetchone()
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
        cur_mysql = conn.cursor()

        # 2. Ambil Statistik Sisa Umur Garansi
        cur_mysql.execute("""
            SELECT 
                SUM(CASE WHEN DATEDIFF(tgl_akhir, CURDATE()) <= 30 THEN 1 ELSE 0 END) as sisa_1_bulan,
                SUM(CASE WHEN DATEDIFF(tgl_akhir, CURDATE()) BETWEEN 31 AND 60 THEN 1 ELSE 0 END) as sisa_2_bulan,
                SUM(CASE WHEN DATEDIFF(tgl_akhir, CURDATE()) > 60 THEN 1 ELSE 0 END) as sisa_3_bulan
            FROM arsip_garansi
            WHERE tgl_akhir >= CURDATE()
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
        
        where_g = "WHERE tgl_akhir >= CURDATE()"
        params_g = []
        if q_garansi:
            where_g += " AND (nama_user LIKE %s OR device LIKE %s)"
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
        cur_sla = conn.execute("SELECT * FROM servis WHERE status NOT IN ('Cash', 'Cancel', 'Done', 'Refund') AND updated_at IS NOT NULL")
        now_dt = datetime.now()
        for row in cur_sla.fetchall():
            row_dict = dict(row)
            updated_at = row_dict.get('updated_at')
            if updated_at:
                try:
                    if isinstance(updated_at, datetime):
                        up_dt = updated_at
                    else:
                        up_dt = datetime.fromisoformat(str(updated_at))
                    diff = now_dt - up_dt
                    hours_diff = diff.total_seconds() / 3600
                    
                    wa_number = str(row_dict.get('no_wa') or '')
                    if wa_number and wa_number.startswith('0'):
                        wa_number = '62' + wa_number[1:]
                    wa_link = f"https://wa.me/{wa_number}" if wa_number else "#"
                    
                    dev_name = row_dict.get('device', 'Unknown')
                    
                    if hours_diff >= 168:
                        sla_notifications.append({'level': 'kritis', 'badge': '🚨', 'title': f"[{int(hours_diff//24)} Hari] {dev_name}", 'desc': 'Kritis (Telah diekskalasi)', 'wa_link': wa_link})
                    elif hours_diff >= 72:
                        sla_notifications.append({'level': 'owner', 'badge': '🔴', 'title': f"[72 Jam] {dev_name}", 'desc': 'Eskalasi Admin', 'wa_link': wa_link})
                    elif hours_diff >= 48:
                        sla_notifications.append({'level': 'happy_call', 'badge': '🟠', 'title': f"[48 Jam] {dev_name}", 'desc': 'Happy Call / Customer Update', 'wa_link': wa_link})
                    elif hours_diff >= 24:
                        sla_notifications.append({'level': 'teknisi', 'badge': '🟡', 'title': f"[24 Jam] {dev_name}", 'desc': 'Reminder Teknisi', 'wa_link': wa_link})
                except Exception as e:
                    print(f"Error parsing SLA servis #{row_dict.get('id')}: {e}")
    except Exception as e:
        print("Error SLA notif:", e)

    # 8. RETURN DENGAN NAMA VARIABEL YANG PAS
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
                           internal_access=internal_access,
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

@dashboard_bp.route('/api/search_pelanggan')
@login_required
def search_pelanggan():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2: return jsonify([])
    
    results_map = {}
    import re
    conn = get_db()
    
    # Cari data aktif dan arsip servis pada MySQL.
    try:
        search_term = f'%{q}%'
        query_sql = '''
            SELECT DISTINCT nama, wa FROM (
                SELECT nama_user as nama, no_wa as wa FROM servis WHERE nama_user LIKE %s OR REPLACE(REPLACE(no_wa, '-', ''), ' ', '') LIKE %s
                UNION
                SELECT nama_user as nama, wa as wa FROM arsip_servis WHERE nama_user LIKE %s OR REPLACE(REPLACE(wa, '-', ''), ' ', '') LIKE %s
            ) AS subquery WHERE nama IS NOT NULL AND nama != ''
            ORDER BY nama ASC LIMIT 15
        '''
        rows = conn.execute(query_sql, (search_term, search_term, search_term, search_term)).fetchall()
        for r in rows:
            if r['nama']:
                k = f"{r['nama'].strip().lower()}_{str(r['wa'] or '').strip().lower()}"
                results_map[k] = {'nama': r['nama'].strip(), 'wa': str(r['wa'] or '').strip()}
    except Exception as e:
        print("Error search_pelanggan MySQL:", e)

    # 2. Cari di MySQL (arsip_pelanggan & arsip_garansi)
    try:
        cur_m = conn.cursor()
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
    except Exception as e:
        print("Error search_pelanggan MySQL:", e)
        
    final_results = sorted(list(results_map.values()), key=lambda x: x['nama'].lower())[:15]
    return jsonify(final_results)

@dashboard_bp.route('/api/check_wa')
@login_required
def check_wa():
    wa = request.args.get('wa', '').strip()
    import re
    clean_wa = re.sub(r'[\s\-+]', '', wa)
    if not clean_wa or len(clean_wa) < 5: return jsonify({'found': False})
    
    last_digits = clean_wa[-9:] if len(clean_wa) >= 9 else clean_wa
    search_pattern_sql = f'%{last_digits}%'
    search_pattern_mysql = f'%{last_digits}%'
    
    all_rows = []
    conn = get_db()
    
    # Cari data aktif dan arsip servis pada MySQL.
    try:
        query = '''
            SELECT nama_user as nama, tanggal_masuk as tgl, device as device FROM servis WHERE REPLACE(REPLACE(no_wa, '-', ''), ' ', '') LIKE %s
            UNION ALL
            SELECT nama_user as nama, tanggal_masuk as tgl, device as device FROM arsip_servis WHERE REPLACE(REPLACE(wa, '-', ''), ' ', '') LIKE %s
        '''
        rows = conn.execute(query, (search_pattern_sql, search_pattern_sql)).fetchall()
        for r in rows:
            all_rows.append({'nama': r['nama'], 'tgl': r['tgl'], 'device': r['device']})
    except Exception as e:
        print("Error check_wa MySQL:", e)
        
    # 2. Cari di MySQL (arsip_pelanggan)
    try:
        cur_m = conn.cursor()
        cur_m.execute("""
            SELECT nama_user as nama, device, status_final, id_arsip FROM arsip_pelanggan 
            WHERE REPLACE(REPLACE(no_wa, '-', ''), ' ', '') LIKE %s
            ORDER BY id_arsip DESC
        """, (search_pattern_mysql,))
        rows_m = cur_m.fetchall()
        for r in rows_m:
            all_rows.append({'nama': r['nama'], 'tgl': 'Arsip Selesai', 'device': r['device'], 'id_arsip': r['id_arsip']})
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
