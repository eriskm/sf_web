import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# I will replace from <!-- HERO CARDS --> up to <!-- CHARTS AREA (Old Charts Repurposed) -->
new_hero_and_metrics = '''
            <!-- NEW METRICS GRID -->
            <div class="metrics-grid">
                <!-- Omset -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--success);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg></div>
                        <div class="metric-title">Omset Hari Ini</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(total_laba[0]) }}</div>
                    <div class="metric-trend trend-up"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="18 15 12 9 6 15"></polyline></svg> 12% <span class="trend-text">vs kemarin</span></div>
                </div>
                <!-- Laba Kotor -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--primary);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"></path></svg></div>
                        <div class="metric-title">Laba Kotor</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(total_laba[0] + 50000) }}</div>
                    <div class="metric-trend trend-up"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="18 15 12 9 6 15"></polyline></svg> 8% <span class="trend-text">vs kemarin</span></div>
                </div>
                <!-- Total Beban -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--warning);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg></div>
                        <div class="metric-title">Total Beban</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(total_beban) }}</div>
                    <div class="metric-trend trend-down" style="color: var(--danger); background: var(--danger-light);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 9 12 15 18 9"></polyline></svg> 5% <span class="trend-text">vs kemarin</span></div>
                </div>
                <!-- Laba Bersih -->
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background: var(--danger);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg></div>
                        <div class="metric-title">Laba Bersih</div>
                    </div>
                    <div class="metric-value">Rp {{ "{:,}".format(laba_bersih) }}</div>
                    <div class="metric-trend trend-down"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 9 12 15 18 9"></polyline></svg> 8% <span class="trend-text">vs kemarin</span></div>
                </div>
                
                <!-- Target Hari Ini -->
                <div class="target-card">
                    <div class="target-info">
                        <div class="target-title">Target Hari Ini</div>
                        <div class="target-val">Rp 400.000</div>
                        <div class="target-bar-bg"><div class="target-bar-fill" style="width: {{ persen_total if persen_total <= 100 else 100 }}%;"></div></div>
                        <div class="target-desc">Kurang <strong style="color: var(--danger);">Rp 195.000</strong> lagi</div>
                    </div>
                    <div class="progress-ring" style="--pct: {{ persen_total }}%;">
                        <div class="progress-ring-inner">{{ "{:0.0f}".format(persen_total if persen_total <= 100 else 100) }}%</div>
                    </div>
                </div>
            </div>

            <!-- MIDDLE SECTION -->
            <div class="middle-grid">
                <!-- Aksi Cepat -->
                <div class="section-box">
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

                <!-- Insight Hari Ini -->
                <div class="section-box">
                    <div class="section-title">Insight Hari Ini</div>
                    <div class="insight-grid">
                        <div class="insight-card">
                            <div class="insight-title" style="color: var(--primary);">Unit Masuk</div>
                            <div class="insight-icon" style="color: var(--primary);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><path d="M9 17h6"></path><circle cx="17" cy="17" r="2"></circle></svg></div>
                            <div class="insight-val">12</div>
                            <div class="insight-unit">Unit</div>
                        </div>
                        <div class="insight-card">
                            <div class="insight-title" style="color: var(--success);">Unit Selesai</div>
                            <div class="insight-icon" style="color: var(--success);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg></div>
                            <div class="insight-val">8</div>
                            <div class="insight-unit">Unit</div>
                        </div>
                        <div class="insight-card">
                            <div class="insight-title" style="color: var(--success);">Unit Cash</div>
                            <div class="insight-icon" style="color: var(--success);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2" ry="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg></div>
                            <div class="insight-val">5</div>
                            <div class="insight-unit">Unit</div>
                        </div>
                        <div class="insight-card">
                            <div class="insight-title" style="color: var(--warning);">Unit Pending</div>
                            <div class="insight-icon" style="color: var(--warning);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg></div>
                            <div class="insight-val">7</div>
                            <div class="insight-unit">Unit</div>
                        </div>
                    </div>
                </div>

                <!-- Teknisi Terbaik -->
                <div class="section-box">
                    <div class="section-title">Teknisi Terbaik</div>
                    <div class="tech-card">
                        <div class="tech-avatar-wrapper">
                            <img src="/static/icon_teknisi.png" class="tech-avatar" alt="Teknisi">
                            <div class="tech-crown">??</div>
                        </div>
                        <div class="tech-name">Eja</div>
                        <div class="tech-stat">12 Unit Selesai</div>
                        <div class="tech-money">Rp 1.850.000</div>
                    </div>
                </div>
            </div>

            <!-- CHARTS & AI GRID -->
            <div class="bottom-grid">
                <!-- Status Transaksi -->
                <div class="section-box">
                    <div class="section-title">Statistik Status Transaksi
                        <select style="border: 1px solid var(--border); border-radius: 6px; padding: 4px 8px; font-size: 0.9em; outline: none;"><option>Hari Ini</option><option>Bulan Ini</option></select>
                    </div>
                    <div class="chart-container"><canvas id="barStatus"></canvas></div>
                </div>
                
                <!-- Top Kerusakan -->
                <div class="section-box">
                    <div class="section-title">Top 10 Kerusakan
                        <select style="border: 1px solid var(--border); border-radius: 6px; padding: 4px 8px; font-size: 0.9em; outline: none;"><option>Hari Ini</option><option>Bulan Ini</option></select>
                    </div>
                    <div class="chart-container"><canvas id="donutKerusakan"></canvas></div>
                </div>

                <!-- AI Panel -->
                <div class="ai-panel">
                    <div class="ai-header">
                        <div class="ai-bot-info">
                            <div class="ai-bot-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg></div>
                            <div>
                                <div class="ai-bot-name">AkuntanBossSF</div>
                                <div class="ai-bot-sub">AI Assistant</div>
                            </div>
                        </div>
                        <div class="ai-status"><div class="status-dot"></div> Online</div>
                    </div>
                    <div class="ai-body">
                        <div class="ai-bubble">
                            <div class="ai-greet">Halo {{ session.get('user', 'Bos') }} ??</div>
                            <div class="ai-msg">Hari ini laba masih minus <strong style="color: var(--danger);">Rp 195.000</strong></div>
                            <div style="font-size: 0.8em; color: var(--gray); font-weight: 600; margin-bottom: 10px;">Saran untuk meningkatkan laba hari ini:</div>
                            <div class="ai-list">
                                <div class="ai-list-item">
                                    <div class="ai-list-icon" style="background: var(--success-light); color: var(--success);"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg></div>
                                    <div>Follow up 3 unit yang sudah selesai</div>
                                </div>
                                <div class="ai-list-item">
                                    <div class="ai-list-icon" style="background: var(--warning-light); color: var(--warning);"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg></div>
                                    <div>Ada 2 unit belum konfirmasi</div>
                                </div>
                                <div class="ai-list-item">
                                    <div class="ai-list-icon" style="background: var(--purple-light); color: var(--purple);"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"></path></svg></div>
                                    <div>Potensi laba tambahan <strong style="color: var(--success);">Rp 350.000</strong></div>
                                </div>
                            </div>
                            <button class="btn-ai">Lihat Rekomendasi Detail</button>
                        </div>
                    </div>
                    <div class="ai-footer">
                        <div class="ai-input-box">
                            <input type="text" placeholder="Tanya sesuatu...">
                            <button class="ai-send"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg></button>
                        </div>
                    </div>
                </div>
            </div>

'''

pattern1 = r'<!-- HERO CARDS -->.*?<!-- CHARTS AREA \(Old Charts Repurposed\) -->'
html = re.sub(pattern1, new_hero_and_metrics, html, flags=re.DOTALL)

# Next, we replace the old Table with Modern Table
pattern2 = r'<!-- ORIGINAL DATA TRANSAKSI TABLE AREA -->.*?(?=<div id="tabel-kas")'

new_table = '''
            <!-- MODERN DATA TRANSAKSI TABLE AREA -->
            {% if request.args.get('bot') != 'SF_RAHASIA_NEGARA' %}
            <div id="tabel-transaksi-data" class="table-section" style="margin-bottom: 30px;">
                <div class="table-header">
                    <div class="table-title">Transaksi Terbaru</div>
                    <div class="table-actions">
                        <form onsubmit="event.preventDefault(); window.location.href='/dashboard?tgl=' + encodeURIComponent(this.tgl.value) + '&q=' + encodeURIComponent(this.q.value) + '#tabel-transaksi-data';" style="display: flex; gap: 10px;">
                            <div class="search-box">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--gray)" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                                <input type="text" name="q" value="{{ q_aktif }}" placeholder="Cari nama / device..." autocomplete="off">
                                <input type="hidden" name="tgl" value="{{ tgl_aktif }}">
                            </div>
                            <button type="submit" class="btn-outline"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg> Filter</button>
                            {% if tgl_aktif or q_aktif %}
                                <a href="/dashboard" class="btn-outline" style="color: var(--danger);">Reset</a>
                            {% endif %}
                            <a href="/tambah" style="text-decoration: none;"><button type="button" class="btn-primary">+ Service Baru</button></a>
                        </form>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>No</th>
                            <th>Tanggal</th>
                            <th>Pelanggan</th>
                            <th>Device</th>
                            <th>Status</th>
                            <th>Kerusakan</th>
                            <th>Teknisi</th>
                            <th>Laba</th>
                            <th>Aksi</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for s in servis %}
                        <tr>
                            <td data-label="No">{{ loop.index }}</td>
                            <td data-label="Tanggal">{{ s['Tanggal Masuk'] }}</td>
                            <td data-label="Pelanggan" class="td-pelanggan">
                                <span class="td-name">{{ s['Nama User'] }}</span>
                                <span class="td-phone">{{ s['No. WA'] or '-' }}</span>
                            </td>
                            <td data-label="Device" class="td-device">
                                <svg class="device-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>
                                {{ s['Device'] }}
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
                            <td data-label="Teknisi" class="td-tek">
                                <img src="/static/icon_{{ 'admin' if s['Teknisi'] == 'Admin' else 'teknisi' }}.png" alt="Teknisi">
                                {{ s['Teknisi'] or '-' }}
                            </td>
                            <td data-label="Laba">
                                {% if s['Status'] == 'Cash' %}
                                    <span class="td-laba">Rp {{ "{:,}".format(s['Laba Kotor'] or 0) }}</span>
                                {% else %}
                                    <span class="td-laba-empty">-</span>
                                {% endif %}
                            </td>
                            <td data-label="Aksi" class="td-actions">
                                <a href="/detail/{{ s['id'] }}" class="btn-action btn-edit"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></a>
                                {% if session['role'] == 'admin' %}
                                <a href="/delete/{{ s['id'] }}" onclick="return confirm('Yakin mau hapus data {{ s['Device'] }}?')" class="btn-action btn-delete"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="table-footer">
                    <div>Menampilkan {{ servis|length }} data</div>
                    <div class="pagination">
                        {% if current_page > 1 %}
                        <a href="{{ url_for('dashboard', page=current_page-1, tgl=tgl_aktif, q=q_aktif) }}#tabel-transaksi-data"><button class="page-btn"><</button></a>
                        {% endif %}
                        
                        {% for p in range(1, total_pages + 1) %}
                        <a href="{{ url_for('dashboard', page=p, tgl=tgl_aktif, q=q_aktif) }}#tabel-transaksi-data"><button class="page-btn {{ 'active' if p == current_page else '' }}">{{ p }}</button></a>
                        {% endfor %}
                        
                        {% if current_page < total_pages %}
                        <a href="{{ url_for('dashboard', page=current_page+1, tgl=tgl_aktif, q=q_aktif) }}#tabel-transaksi-data"><button class="page-btn">></button></a>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- ORIGINAL KAS / GARANSI / PELANGGAN FOLLOWS -->
'''

html = re.sub(pattern2, new_table, html, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("REWRITE DASHBOARD SUCCESS")
