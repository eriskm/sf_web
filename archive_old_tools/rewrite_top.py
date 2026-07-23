import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'<!-- OVERLAY UNTUK MOBILE SIDEBAR -->.*?<div class="content-body">'

new_top = '''<!-- OVERLAY UNTUK MOBILE SIDEBAR -->
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
                
                <button class="btn-icon" onclick="document.getElementById('notifDropdown').classList.toggle('show')">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                    {% if sla_notifications %}
                    <span class="notif-dot">{{ sla_notifications|length }}</span>
                    {% endif %}
                    
                    <div id="notifDropdown" style="display: none; position: absolute; right: 0; top: 45px; width: 320px; background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-radius: 12px; border: 1px solid var(--border); z-index: 9999; text-align: left; cursor: default;">
                        <div style="padding: 15px; border-bottom: 1px solid var(--border); font-weight: 800; color: var(--dark); display: flex; justify-content: space-between; align-items: center;">
                            Notifikasi (SLA)
                            <span style="font-size: 0.8em; font-weight: 500; background: var(--danger-light); color: var(--danger); padding: 2px 8px; border-radius: 20px;">{{ sla_notifications|length }} Unread</span>
                        </div>
                        <div style="max-height: 400px; overflow-y: auto;">
                            {% if sla_notifications %}
                                {% for notif in sla_notifications %}
                                <div style="padding: 15px; border-bottom: 1px solid var(--border); transition: background 0.2s;" onmouseover="this.style.background='var(--gray-light)'" onmouseout="this.style.background='transparent'">
                                    <div style="display: flex; gap: 10px; align-items: flex-start;">
                                        <div style="font-size: 1.2em;">{{ notif.badge }}</div>
                                        <div style="flex: 1;">
                                            <div style="font-weight: 600; color: var(--dark); font-size: 0.9em; margin-bottom: 2px;">{{ notif.title }}</div>
                                            <div style="font-size: 0.8em; color: var(--gray); margin-bottom: 8px;">{{ notif.desc }}</div>
                                            {% if notif.level == 'happy_call' %}
                                            <a href="{{ notif.wa_link }}" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; font-size: 0.75em; background: var(--success-light); color: var(--success); padding: 4px 10px; border-radius: 6px; text-decoration: none; font-weight: 600;">
                                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg> Happy Call WA
                                            </a>
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                                {% endfor %}
                            {% else %}
                                <div style="padding: 30px 15px; text-align: center; color: var(--gray); font-size: 0.9em;">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--border)" stroke-width="2" style="margin-bottom: 10px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                                    <div>Semua aman! Tidak ada notifikasi keterlambatan.</div>
                                </div>
                            {% endif %}
                        </div>
                    </div>
                </button>
            </div>
        </header>

        <script>
            // Date formatter for Topbar
            const dateOpts = { day: 'numeric', month: 'short', year: 'numeric' };
            document.getElementById('currentDate').innerText = new Date().toLocaleDateString('id-ID', dateOpts);
            
            // Close dropdown if clicked outside
            document.addEventListener('click', function(event) {
                var dropdown = document.getElementById('notifDropdown');
                if (dropdown && event.target.closest('.btn-icon') === null && !dropdown.contains(event.target)) {
                    dropdown.classList.remove('show');
                }
            });
        </script>

        <div class="content-body">'''

html = re.sub(pattern, new_top, html, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("REWRITE TOP SUCCESS")
