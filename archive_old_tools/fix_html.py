import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need to replace the entire top section up to <div id="tabel-kas" with the correct data variables.
# First, let's extract the top Jinja part just in case.

correct_top = '''<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <title>Dashboard SF - Filter Mode</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Inter:wght@400;500;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='dashboard.css') }}">
    <style>
        /* KHUSUS BOT TELEGRAM */
        {% if request.args.get('bot') == 'SF_RAHASIA_NEGARA' %}
        .sidebar, .topbar, .hero-grid, .quick-actions, .charts-area, .metrics-grid, .action-grid { display: none !important; }
        .main-content { margin-left: 0 !important; }
        .content-body { padding: 20px !important; }
        {% endif %}
    </style>
</head>
<body>
    {% set total_laba = [0] %}
    {% for s in servis %}
        {% if s['Status'] == 'Cash' and s['Laba Kotor'] %}
            {% if total_laba.append(total_laba.pop() + s['Laba Kotor']) %}{% endif %}
        {% endif %}
    {% endfor %}

    {% set total_beban = g_hari + o_hari %}
    {% set laba_bersih = total_laba[0] - total_beban %}
    {% set persen_total = (total_laba[0] / total_beban * 100) if total_beban > 0 else 0 %}

    <!-- OVERLAY UNTUK MOBILE SIDEBAR -->
    <div class="overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

    <!-- SIDEBAR -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-logo">SF</div>
            <div class="sidebar-title">SUKABUMI<br>FLASHER</div>
        </div>
        
        <div class="sidebar-user">
            {% set role_label = session.get('role', 'User')|title %}
            {% if session.get('role') == 'admin' %}
                {% set avatar_img = '/static/icon_admin.png' %}
            {% elif session.get('role') == 'kasir' %}
                {% set avatar_img = '/static/icon_kasir.png' %}
            {% elif session.get('role') == 'teknisi' %}
                {% set avatar_img = '/static/icon_teknisi.png' %}
            {% else %}
                {% set avatar_img = 'https://api.dicebear.com/7.x/adventurer-neutral/svg?seed=' ~ session.get('user', 'User') ~ '&backgroundColor=e2e8f0' %}
            {% endif %}
            <img src="{{ avatar_img }}" alt="Avatar">
            <div class="sidebar-user-info">
                <div class="sidebar-user-name">{{ session.get('user', 'User')|title }} <span class="user-role-badge">{{ role_label }}</span></div>
                <div class="sidebar-user-desc">Sukabumi Flasher</div>
            </div>
        </div>
        
        <div class="sidebar-menu">
            <a href="/dashboard" class="menu-item active">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                Dashboard
            </a>
            <a href="#tabel-transaksi-data" class="menu-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Transaksi
            </a>
            <a href="#tabel-pelanggan" class="menu-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                Pelanggan
            </a>
            <a href="#tabel-garansi" class="menu-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                Garansi
            </a>
            <a href="#tabel-sparepart" class="menu-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                Sparepart
            </a>
            {% if 'keuangan' in session.get('permissions', '') %}
            <a href="#tabel-kas" class="menu-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M2 12h4l2-9 5 18 3-10h4"></path></svg>
                Keuangan
            </a>
            <a href="#tabel-kas" class="menu-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Laporan
            </a>
            {% endif %}
            
            {% if 'users' in session.get('permissions', '') %}
            <div class="menu-label">Admin Area</div>
            <a href="/users" class="menu-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                Kelola Akun
            </a>
            {% endif %}
        </div>
        
        <div class="sidebar-footer">
            <a href="/logout" class="menu-item" style="color: var(--danger); width: 100%;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                Keluar
            </a>
        </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-content">
        <!-- TOPBAR -->
        <header class="topbar">
            <div style="display: flex; align-items: center; gap: 15px;">
                <button class="hamburger-btn" onclick="toggleSidebar()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                </button>
                <div class="topbar-left">
                    <h2>Dashboard</h2>
                    <p>Selamat datang kembali, {{ session.get('user', 'Bos')|title }} ??</p>
                </div>
            </div>
            
            <div class="topbar-right">
                <div class="date-badge">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                    <span id="currentDate"></span>
                </div>
                
                <button class="btn-icon" id="themeToggle" title="Toggle Mode">
                    <svg id="themeIconLight" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                    <svg id="themeIconDark" style="display: none;" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                </button>
            </div>
        </header>
        
        <script>
            const dateOpts = { day: 'numeric', month: 'short', year: 'numeric' };
            document.getElementById('currentDate').innerText = new Date().toLocaleDateString('id-ID', dateOpts);
        </script>

        <div class="content-body">
            
            <!-- METRICS GRID (Replacing Hero) -->
            <div class="metrics-grid">
                <!-- Laba Kotor (Replacing Omset for real data alignment) -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--success);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg></div>
                        <div class="metric-title">TOTAL LABA KOTOR</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(total_laba[0]) }}</div>
                </div>
                <!-- Beban Gaji -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--danger);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"></path></svg></div>
                        <div class="metric-title">BEBAN GAJI</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(g_hari) }}</div>
                </div>
                <!-- Beban Ops -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--warning);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg></div>
                        <div class="metric-title">BEBAN OPS</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(o_hari) }}</div>
                </div>
                <!-- Laba Bersih -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--primary);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg></div>
                        <div class="metric-title">LABA BERSIH</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(laba_bersih) }}</div>
                </div>
            </div>

            <!-- AKSI CEPAT GRID -->
            <div class="section-box" style="margin-bottom: 30px;">
                <div class="section-title">Aksi Cepat</div>
                <div class="action-grid">
                    <a href="/tambah" class="action-btn">
                        <div class="action-icon" style="color: var(--purple); background: var(--purple-light);">+</div>
                        <div>
                            <div class="action-text">Service Baru</div>
                            <div class="action-sub">Buat transaksi</div>
                        </div>
                    </a>
                    {% if 'keuangan' in session.get('permissions', '') %}
                    <div onclick="bukaPopupKas()" class="action-btn">
                        <div class="action-icon" style="color: var(--success); background: var(--success-light);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2" ry="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg></div>
                        <div>
                            <div class="action-text">Input Kas</div>
                            <div class="action-sub">Pemasukan harian</div>
                        </div>
                    </div>
                    <a href="/beban" class="action-btn">
                        <div class="action-icon" style="color: var(--warning); background: var(--warning-light);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg></div>
                        <div>
                            <div class="action-text">Input Beban</div>
                            <div class="action-sub">Catat pengeluaran</div>
                        </div>
                    </a>
                    {% endif %}
                    {% if 'sparepart' in session.get('permissions', '') %}
                    <div onclick="bukaPopupSparepart()" class="action-btn">
                        <div class="action-icon" style="color: var(--primary); background: var(--primary-light);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg></div>
                        <div>
                            <div class="action-text">Sparepart</div>
                            <div class="action-sub">Kelola data</div>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- CHARTS AREA -->
            <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                <div class="section-box" style="flex: 2;">
                    <div class="section-title">Statistik Status Transaksi</div>
                    <div class="chart-container" style="height: 250px; position: relative;"><canvas id="barStatus"></canvas></div>
                </div>
                <div class="section-box" style="flex: 1;">
                    <div class="section-title">Top 10 Kerusakan</div>
                    <div class="chart-container" style="height: 250px; position: relative;"><canvas id="donutKerusakan"></canvas></div>
                </div>
            </div>

            <!-- MODERN DATA TRANSAKSI TABLE AREA -->
            {% if request.args.get('bot') != 'SF_RAHASIA_NEGARA' %}
            <div id="tabel-transaksi-data" class="table-section" style="margin-bottom: 30px; border-radius: 16px; border: 1px solid var(--border); background: white;">
                <div class="table-header" style="padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border);">
                    <div class="table-title" style="font-weight: 700;">Transaksi Terbaru</div>
                    <div class="table-actions">
                        <form onsubmit="event.preventDefault(); window.location.href='/dashboard?tgl=' + encodeURIComponent(this.tgl.value) + '&q=' + encodeURIComponent(this.q.value) + '#tabel-transaksi-data';" style="display: flex; gap: 10px;">
                            <input type="date" name="tgl" value="{{ tgl_aktif }}" style="padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.85em;">
                            <div class="search-box" style="display: flex; align-items: center; border: 1px solid var(--border); padding: 8px 12px; border-radius: 8px; font-size: 0.85em;">
                                <input type="text" name="q" value="{{ q_aktif }}" placeholder="Cari nama / device..." autocomplete="off" style="border:none; outline:none;">
                            </div>
                            <button type="submit" class="btn-outline">?? Filter</button>
                            {% if tgl_aktif or q_aktif %}
                                <a href="/dashboard" class="btn-outline" style="color: var(--danger); text-decoration: none;">Reset</a>
                            {% endif %}
                            <a href="/tambah" style="text-decoration: none;"><button type="button" class="btn-primary" style="background: var(--success); border: none; color: white; padding: 8px 15px; border-radius: 8px; cursor: pointer;">+ Service Baru</button></a>
                        </form>
                    </div>
                </div>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>No</th>
                            <th>Tanggal</th>
                            <th>Device</th>
                            <th>User / WA</th>
                            <th>Status</th>
                            <th>Kerusakan</th>
                            <th>Perbaikan</th>
                            <th>Teknisi</th>
                            <th>Laba</th>
                            <th>Aksi</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for s in servis %}
                        <tr style="border-bottom: 1px solid var(--border);">
                            <td data-label="No">{{ loop.index }}</td>
                            <td data-label="Tanggal">{{ s['Tanggal Masuk'] }}</td>
                            <td data-label="Device" class="td-device">
                                <svg class="device-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 5px;"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>
                                {{ s['Device'] }}
                            </td>
                            <td data-label="User / WA" class="td-pelanggan">
                                <span class="td-name">{{ s['Nama User'] }}</span><br>
                                <span class="td-phone" style="font-size: 0.85em; color: var(--success);">{{ s['No. WA'] or '-' }}</span>
                            </td>
                            <td data-label="Status">
                                <span class="badge {% if s['Status'] == 'Cash' %}status-cash
                                            {% elif s['Status'] == 'Analisa' %}status-analisa
                                            {% elif s['Status'] == 'Konfirmasi' %}status-konfirmasi
                                            {% elif s['Status'] == 'Wait Part' %}status-wait
                                            {% elif s['Status'] == 'Repair' %}status-repair
                                            {% elif s['Status'] == 'Done' %}status-done
                                            {% elif s['Status'] == 'Failed' %}status-cancel
                                            {% elif s['Status'] == 'Garansi' %}status-done
                                            {% elif s['Status'] == 'Refund' %}status-cancel
                                            {% elif s['Status'] == 'Cancel' %}status-cancel
                                            {% endif %}">{{ s['Status'] }}</span>
                            </td>
                            <td data-label="Kerusakan" style="font-size: 0.85em; color: var(--gray);">{{ s['Analisa Kerusakan'] or '-' }}</td>
                            <td data-label="Perbaikan" style="font-size: 0.85em; color: var(--primary); font-weight: bold;">{{ s['Tindakan Perbaikan'] or '-' }}</td>
                            <td data-label="Teknisi" class="td-tek">
                                <img src="/static/icon_{{ 'admin' if s['Teknisi'] == 'Admin' else 'teknisi' }}.png" alt="Teknisi" style="width: 24px; height: 24px; border-radius: 50%; vertical-align: middle;">
                                {{ s['Teknisi'] or '-' }}
                            </td>
                            <td data-label="Laba">
                                {% if s['Status'] == 'Cash' %}
                                    <span class="td-laba" style="color: var(--success); font-weight: bold;">Rp {{ "{:,}".format(s['Laba Kotor'] or 0) }}</span>
                                {% else %}
                                    <span class="td-laba-empty" style="color: var(--gray);">Rp 0</span>
                                {% endif %}
                            </td>
                            <td data-label="Aksi" class="td-actions" style="display: flex; gap: 5px;">
                                <a href="/detail/{{ s['id'] }}" class="btn-action btn-edit" style="color: var(--primary); text-decoration: none; border: 1px solid var(--border); padding: 5px; border-radius: 6px;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></a>
                                {% if session['role'] == 'admin' %}
                                <a href="/delete/{{ s['id'] }}" onclick="return confirm('Yakin mau hapus data {{ s['Device'] }}?')" class="btn-action btn-delete" style="color: var(--danger); text-decoration: none; border: 1px solid var(--border); padding: 5px; border-radius: 6px;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="table-footer" style="padding: 15px 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 0.8em; color: var(--gray); font-weight: 500;">
                    <div>Menampilkan {{ servis|length }} data</div>
                    <div class="pagination" style="display: flex; gap: 5px;">
                        {% if current_page > 1 %}
                        <a href="{{ url_for('dashboard', page=current_page-1, tgl=tgl_aktif, q=q_aktif) }}#tabel-transaksi-data"><button class="page-btn" style="border:none; background:transparent; cursor:pointer;"><</button></a>
                        {% endif %}
                        
                        {% for p in range(1, total_pages + 1) %}
                        <a href="{{ url_for('dashboard', page=p, tgl=tgl_aktif, q=q_aktif) }}#tabel-transaksi-data"><button class="page-btn" style="border:none; cursor:pointer; padding: 5px 10px; border-radius: 6px; {{ 'background: var(--primary); color: white;' if p == current_page else 'background: transparent;' }}">{{ p }}</button></a>
                        {% endfor %}
                        
                        {% if current_page < total_pages %}
                        <a href="{{ url_for('dashboard', page=current_page+1, tgl=tgl_aktif, q=q_aktif) }}#tabel-transaksi-data"><button class="page-btn" style="border:none; background:transparent; cursor:pointer;">></button></a>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endif %}
'''

# Find the end of the original <head> down to the top of <div id="tabel-kas"
pattern = r'<!DOCTYPE html>.*?<div id="tabel-kas"'
html = re.sub(pattern, correct_top + '<div id="tabel-kas"', html, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("RESTORE AND FIX DONE!")
