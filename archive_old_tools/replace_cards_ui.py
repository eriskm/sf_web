import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the entire content body section from <!-- FINANCIAL CARDS ROW --> down to the end of <!-- ACTION & INSIGHT ROW --> and replace it.

start_marker = '<!-- FINANCIAL CARDS ROW -->'
end_marker = '<!-- TEKNISI TERBAIK -->'
start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('Markers not found')
else:
    new_html = '''<!-- FINANCIAL CARDS ROW -->
            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
                <!-- Omset -->
                <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 20px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 15px;">
                    <div style="width: 60px; height: 60px; border-radius: 16px; background: #10B981; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3);">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: var(--gray); font-weight: 600; margin-bottom: 2px;">Omset Hari Ini</div>
                        <div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(total_penjualan) }}</div>
                    </div>
                </div>

                <!-- Total Laba Kotor -->
                <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 20px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 15px;">
                    <div style="width: 60px; height: 60px; border-radius: 16px; background: #3B82F6; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"></path><path d="M16 21v-5a4 4 0 0 0-4-4h-4"></path></svg>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: var(--gray); font-weight: 600; margin-bottom: 2px;">Laba Kotor</div>
                        <div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(total_laba_kotor) }}</div>
                    </div>
                </div>

                <!-- Total Beban -->
                <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 20px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 15px;">
                    <div style="width: 60px; height: 60px; border-radius: 16px; background: #F59E0B; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 8px 16px rgba(245, 158, 11, 0.3);">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: var(--gray); font-weight: 600; margin-bottom: 2px;">Total Beban</div>
                        <div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(g_hari + o_hari) }}</div>
                    </div>
                </div>

                <!-- Laba Bersih -->
                <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 20px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 15px;">
                    <div style="width: 60px; height: 60px; border-radius: 16px; background: #EF4444; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 8px 16px rgba(239, 68, 68, 0.3);">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"></polyline><polyline points="16 17 22 17 22 11"></polyline></svg>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: var(--gray); font-weight: 600; margin-bottom: 2px;">Laba Bersih</div>
                        <div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(laba_bersih) }}</div>
                    </div>
                </div>

                <!-- Target Gaji (CTS) - Keeping original format with donut chart but matching height -->
                <div style="flex: 1; min-width: 260px; border-radius: 20px; padding: 20px 24px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; justify-content: space-between;">
                    <div style="flex: 1; padding-right: 15px;">
                        <div style="font-size: 0.9em; color: var(--gray); font-weight: 600; margin-bottom: 2px; display:flex; align-items:center; gap:6px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                            Target Gaji (CTS)
                        </div>
                        <div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(g_hari) }}</div>
                    </div>
                    <div class="progress-circle" style="--percent: {{ persen_total }}%; width: 60px; height: 60px; font-size: 1.1em; border-width: 6px;">
                        <div class="progress-inner poppins" style="font-size: 0.35em;">{{ "{:0.1f}".format(persen_total if persen_total <= 100 else 100) }}%</div>
                    </div>
                </div>
            </div>

            <!-- ACTION & INSIGHT ROW -->
            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
                <!-- AKSI CEPAT CONTAINER -->
                <div style="flex: 1; min-width: 500px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 24px; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03);">
                    <div style="font-size: 0.85em; font-weight: 800; color: var(--dark); text-transform: uppercase; margin-bottom: 20px; letter-spacing: 0.5px;">AKSI CEPAT</div>
                    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                        <a href="/tambah" style="flex: 1; min-width: 120px; border-radius: 16px; padding: 20px 10px; background: #fff; border: 1px solid #eee; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; text-decoration: none; text-align: center; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.02)';">
                            <div style="background: #F3E8FF; color: #9333EA; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                            </div>
                            <div style="font-size: 0.9em; font-weight: 700; color: var(--dark); margin-bottom: 6px;">Service Baru</div>
                            <div style="font-size: 0.7em; color: var(--gray); font-weight: 500; padding: 0 10px; line-height: 1.3;">Buat transaksi service baru</div>
                        </a>
                        
                        {% if 'keuangan' in session.get('permissions', '') %}
                        <div onclick="bukaPopupKas()" style="flex: 1; min-width: 120px; border-radius: 16px; padding: 20px 10px; background: #fff; border: 1px solid #eee; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; cursor: pointer; text-align: center; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.02)';">
                            <div style="background: #DCFCE7; color: #16A34A; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg>
                            </div>
                            <div style="font-size: 0.9em; font-weight: 700; color: var(--dark); margin-bottom: 6px;">Input Kas</div>
                            <div style="font-size: 0.7em; color: var(--gray); font-weight: 500; padding: 0 10px; line-height: 1.3;">Catat pemasukan kas harian</div>
                        </div>

                        <a href="/beban" style="flex: 1; min-width: 120px; border-radius: 16px; padding: 20px 10px; background: #fff; border: 1px solid #eee; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; text-decoration: none; text-align: center; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.02)';">
                            <div style="background: #FFEDD5; color: #EA580C; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="2"></circle></svg>
                            </div>
                            <div style="font-size: 0.9em; font-weight: 700; color: var(--dark); margin-bottom: 6px;">Input Beban</div>
                            <div style="font-size: 0.7em; color: var(--gray); font-weight: 500; padding: 0 10px; line-height: 1.3;">Catat pengeluaran operasional</div>
                        </a>
                        {% endif %}

                        {% if 'sparepart' in session.get('permissions', '') %}
                        <div onclick="bukaPopupSparepart()" style="flex: 1; min-width: 120px; border-radius: 16px; padding: 20px 10px; background: #fff; border: 1px solid #eee; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; cursor: pointer; text-align: center; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.02)';">
                            <div style="background: #DBEAFE; color: #2563EB; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                            </div>
                            <div style="font-size: 0.9em; font-weight: 700; color: var(--dark); margin-bottom: 6px;">Sparepart</div>
                            <div style="font-size: 0.7em; color: var(--gray); font-weight: 500; padding: 0 10px; line-height: 1.3;">Kelola data sparepart</div>
                        </div>
                        {% endif %}
                    </div>
                </div>

                <!-- INSIGHT HARI INI CONTAINER -->
                <div style="flex: 1; min-width: 500px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 24px; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03);">
                    <div style="font-size: 0.85em; font-weight: 800; color: var(--dark); text-transform: uppercase; margin-bottom: 20px; letter-spacing: 0.5px;">INSIGHT HARI INI</div>
                    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                        <!-- Masuk -->
                        <div style="flex: 1; min-width: 100px; border-radius: 16px; padding: 20px 10px; background: #F5F8FF; border: 1px solid #E5EDFF; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                            <div style="font-size: 0.8em; font-weight: 700; color: #2563EB; margin-bottom: 12px;">Unit Masuk</div>
                            <div style="color: #2563EB; margin-bottom: 8px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 17H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-1"></path><polygon points="12 15 17 21 7 21 12 15"></polygon></svg>
                            </div>
                            <div style="font-size: 1.8em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1;">{{ insight_masuk }}</div>
                            <div style="font-size: 0.75em; color: var(--gray); font-weight: 600; margin-top: 6px;">Unit</div>
                        </div>

                        <!-- Selesai -->
                        <div style="flex: 1; min-width: 100px; border-radius: 16px; padding: 20px 10px; background: #F0FDF4; border: 1px solid #DCFCE7; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                            <div style="font-size: 0.8em; font-weight: 700; color: #16A34A; margin-bottom: 12px;">Unit Selesai</div>
                            <div style="color: #16A34A; margin-bottom: 8px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                            </div>
                            <div style="font-size: 1.8em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1;">{{ insight_selesai }}</div>
                            <div style="font-size: 0.75em; color: var(--gray); font-weight: 600; margin-top: 6px;">Unit</div>
                        </div>

                        <!-- Cash -->
                        <div style="flex: 1; min-width: 100px; border-radius: 16px; padding: 20px 10px; background: #ECFDF5; border: 1px solid #D1FAE5; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                            <div style="font-size: 0.8em; font-weight: 700; color: #059669; margin-bottom: 12px;">Unit Cash</div>
                            <div style="color: #059669; margin-bottom: 8px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="2"></circle><path d="M6 12h.01M18 12h.01"></path></svg>
                            </div>
                            <div style="font-size: 1.8em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1;">{{ insight_cash }}</div>
                            <div style="font-size: 0.75em; color: var(--gray); font-weight: 600; margin-top: 6px;">Unit</div>
                        </div>

                        <!-- Pending -->
                        <div style="flex: 1; min-width: 100px; border-radius: 16px; padding: 20px 10px; background: #FFF7ED; border: 1px solid #FFEDD5; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                            <div style="font-size: 0.8em; font-weight: 700; color: #EA580C; margin-bottom: 12px;">Unit Pending</div>
                            <div style="color: #EA580C; margin-bottom: 8px;">
                                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                            </div>
                            <div style="font-size: 1.8em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1;">{{ insight_pending }}</div>
                            <div style="font-size: 0.75em; color: var(--gray); font-weight: 600; margin-top: 6px;">Unit</div>
                        </div>
                    </div>
                </div>
            </div>
            '''
    
    content = content[:start_idx] + new_html + '\n            ' + content[end_idx:]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced successfully")
