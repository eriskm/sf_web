import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Define the start and end markers of the block to replace
start_marker = '<!-- HERO CARDS -->'
end_marker = '<!-- CHARTS AREA (Old Charts Repurposed) -->'

new_block = '''<!-- FINANCIAL CARDS ROW -->
            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
                <!-- Omset -->
                <div style="flex: 1; min-width: 200px; height: 120px; border-radius: 20px; padding: 24px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Omset Hari Ini</div>
                    <div style="font-size: 1.8em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif;">Rp {{ "{:,}".format(total_penjualan) }}</div>
                </div>

                <!-- Total Laba -->
                <div style="flex: 1; min-width: 200px; height: 120px; border-radius: 20px; padding: 24px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Total Laba Kotor</div>
                    <div style="font-size: 1.8em; font-weight: 800; color: var(--success); font-family: 'Poppins', sans-serif;">Rp {{ "{:,}".format(total_laba_kotor) }}</div>
                </div>

                <!-- Total Beban -->
                <div style="flex: 1; min-width: 200px; height: 120px; border-radius: 20px; padding: 24px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Total Beban</div>
                    <div style="font-size: 1.8em; font-weight: 800; color: var(--warning); font-family: 'Poppins', sans-serif;">Rp {{ "{:,}".format(g_hari + o_hari) }}</div>
                </div>

                <!-- Laba Bersih -->
                <div style="flex: 1; min-width: 200px; height: 120px; border-radius: 20px; padding: 24px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Laba Bersih</div>
                    <div style="font-size: 1.8em; font-weight: 800; color: var(--primary); font-family: 'Poppins', sans-serif;">Rp {{ "{:,}".format(laba_bersih) }}</div>
                </div>

                <!-- Target Gaji (CTS) -->
                <div style="flex: 1; min-width: 260px; height: 120px; border-radius: 20px; padding: 15px 24px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; justify-content: space-between;">
                    <div style="flex: 1; padding-right: 15px;">
                        <div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase; margin-bottom: 5px;">Target Gaji (CTS)</div>
                        <div style="font-size: 1.4em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif;">Rp {{ "{:,}".format(g_hari) }}</div>
                    </div>
                    <div class="progress-circle" style="--percent: {{ persen_total }}%; width: 70px; height: 70px; font-size: 1.2em; border-width: 8px;">
                        <div class="progress-inner poppins" style="font-size: 0.35em;">{{ "{:0.1f}".format(persen_total if persen_total <= 100 else 100) }}%</div>
                    </div>
                </div>
            </div>

            <!-- ACTION & INSIGHT ROW -->
            <div style="display: flex; gap: 30px; flex-wrap: wrap; margin-bottom: 30px;">
                <!-- AKSI CEPAT -->
                <div>
                    <div style="font-weight: 700; margin-bottom: 15px; font-size: 1.1em; color: var(--dark);">Aksi Cepat</div>
                    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                        <a href="/tambah" style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; color: var(--dark); text-align: center; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="background: var(--purple-light); color: var(--purple); width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                            </div>
                            <div style="font-size: 0.85em; font-weight: 600; line-height: 1.2;">Service<br>Baru</div>
                        </a>
                        
                        {% if 'keuangan' in session.get('permissions', '') %}
                        <div onclick="bukaPopupKas()" style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; color: var(--dark); text-align: center; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="background: var(--success-light); color: var(--success); width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2" ry="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg>
                            </div>
                            <div style="font-size: 0.85em; font-weight: 600; line-height: 1.2;">Input<br>Kas</div>
                        </div>

                        <a href="/beban" style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; color: var(--dark); text-align: center; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="background: var(--danger-light); color: var(--danger); width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                            </div>
                            <div style="font-size: 0.85em; font-weight: 600; line-height: 1.2;">Input<br>Beban</div>
                        </a>
                        {% endif %}

                        {% if 'sparepart' in session.get('permissions', '') %}
                        <div onclick="bukaPopupSparepart()" style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; color: var(--dark); text-align: center; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="background: var(--primary-light); color: var(--primary); width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                            </div>
                            <div style="font-size: 0.85em; font-weight: 600; line-height: 1.2;">Input<br>Part</div>
                        </div>
                        {% endif %}
                    </div>
                </div>

                <!-- INSIGHT HARI INI -->
                <div>
                    <div style="font-weight: 700; margin-bottom: 15px; font-size: 1.1em; color: var(--dark);">Insight Hari Ini</div>
                    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                        <div style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
                            <div style="font-size: 2.2em; font-weight: 800; color: var(--primary); font-family: 'Poppins', sans-serif;">{{ insight_masuk }}</div>
                            <div style="font-size: 0.8em; color: var(--gray); font-weight: 600; line-height: 1.2; margin-top: 5px;">Unit<br>Masuk</div>
                        </div>
                        <div style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
                            <div style="font-size: 2.2em; font-weight: 800; color: var(--success); font-family: 'Poppins', sans-serif;">{{ insight_selesai }}</div>
                            <div style="font-size: 0.8em; color: var(--gray); font-weight: 600; line-height: 1.2; margin-top: 5px;">Unit<br>Selesai</div>
                        </div>
                        <div style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
                            <div style="font-size: 2.2em; font-weight: 800; color: var(--warning); font-family: 'Poppins', sans-serif;">{{ insight_cash }}</div>
                            <div style="font-size: 0.8em; color: var(--gray); font-weight: 600; line-height: 1.2; margin-top: 5px;">Unit<br>Cash</div>
                        </div>
                        <div style="width: 110px; height: 120px; border-radius: 16px; padding: 16px; background: var(--card-bg); border: 1px solid var(--border); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
                            <div style="font-size: 2.2em; font-weight: 800; color: var(--danger); font-family: 'Poppins', sans-serif;">{{ insight_pending }}</div>
                            <div style="font-size: 0.8em; color: var(--gray); font-weight: 600; line-height: 1.2; margin-top: 5px;">Unit<br>Pending</div>
                        </div>
                    </div>
                </div>

                <!-- TEKNISI TERBAIK -->
                <div>
                    <div style="font-weight: 700; margin-bottom: 15px; font-size: 1.1em; color: var(--dark);">Teknisi Terbaik</div>
                    <div style="width: 280px; height: 175px; border-radius: 20px; padding: 24px; background: linear-gradient(135deg, #1e293b, #0f172a); color: white; border: 1px solid var(--border); position: relative; overflow: hidden; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);">
                        <!-- Dekorasi -->
                        <div style="position: absolute; right: -20px; top: -20px; opacity: 0.1;">
                            <svg width="150" height="150" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                        </div>
                        
                        <div style="display: flex; align-items: flex-start; gap: 15px; position: relative; z-index: 2;">
                            <!-- Avatar -->
                            <div style="width: 72px; height: 72px; border-radius: 50%; border: 3px solid #FBBF24; overflow: hidden; background: white; flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
                                <img src="https://api.dicebear.com/7.x/adventurer-neutral/svg?seed={{ teknisi_terbaik['nama'] }}&backgroundColor=e2e8f0" alt="Avatar" style="width: 100%; height: 100%; object-fit: cover;">
                            </div>
                            <div>
                                <!-- Crown & Title -->
                                <div style="display: flex; align-items: center; gap: 5px; color: #FBBF24; margin-bottom: 2px;">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"></path></svg>
                                    <span style="font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">Top of the Day</span>
                                </div>
                                <div style="font-size: 24px; font-weight: 700; line-height: 1.1; margin-bottom: 4px;">{{ teknisi_terbaik['nama'] }}</div>
                                <div style="font-size: 14px; color: #94a3b8;">{{ teknisi_terbaik['jobs'] }} Unit Selesai</div>
                            </div>
                        </div>
                        
                        <div style="position: relative; z-index: 2; display: flex; align-items: flex-end; justify-content: space-between;">
                            <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Total Revenue</div>
                            <div style="font-size: 24px; font-weight: 800; color: #22C55E; font-family: 'Poppins', sans-serif; line-height: 1;">Rp {{ "{:,}".format(teknisi_terbaik['revenue'] or 0) }}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- CHARTS AREA (Old Charts Repurposed) -->'''

try:
    start_idx = html.index(start_marker)
    end_idx = html.index(end_marker)
    final_html = html[:start_idx] + new_block + html[end_idx + len(end_marker):]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("HTML successfully replaced!")
except Exception as e:
    print(f"Error: {e}")
