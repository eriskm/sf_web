import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need to find the START of ACTION & INSIGHT ROW
start_marker = '<!-- ACTION & INSIGHT ROW -->'
# We need to find the START of CHARTS AREA
end_marker = '<!-- CHARTS AREA (Old Charts Repurposed) -->'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Cannot find markers!")
    exit(1)

# Now, we will completely replace everything between start_idx and end_idx with pristine HTML!
# This HTML will have min-width: 250px; and proper nesting.

pristine_html = """<!-- ACTION & INSIGHT ROW -->
              <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
                  
                  <!-- AKSI CEPAT CONTAINER -->
                  <div style="flex: 1; min-width: 250px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 15px 20px; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03);">
                      <div style="font-size: 0.85em; font-weight: 800; color: var(--dark); text-transform: uppercase; margin-bottom: 20px; letter-spacing: 0.5px;">AKSI CEPAT</div>
                      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                          <!-- Service Baru -->
                          <a href="/tambah" style="flex: 1; min-width: 90px; border-radius: 16px; padding: 16px 8px; background: #fff; border: 1px solid #f0f0f0; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; text-decoration: none; text-align: center; transition: 0.2s; box-shadow: 0 2px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 15px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 10px rgba(0,0,0,0.02)';">
                              <div style="background: linear-gradient(135deg, #F3E8FF, #F5F3FF); color: #7E22CE; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(126, 34, 206, 0.15);">
                                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                              </div>
                              <div style="font-size: 0.8em; font-weight: 700; color: #1E293B; margin-bottom: 6px;">Service Baru</div>
                              <div style="font-size: 0.65em; color: #64748B; font-weight: 500; padding: 0 4px; line-height: 1.3;">Buat transaksi<br>service baru</div>
                          </a>
                          
                          {% if 'keuangan' in session.get('permissions', '') %}
                          <!-- Input Kas -->
                          <div onclick="bukaPopupKas()" style="flex: 1; min-width: 90px; border-radius: 16px; padding: 16px 8px; background: #fff; border: 1px solid #f0f0f0; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; cursor: pointer; text-align: center; transition: 0.2s; box-shadow: 0 2px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 15px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 10px rgba(0,0,0,0.02)';">
                              <div style="background: linear-gradient(135deg, #DCFCE7, #ECFDF5); color: #15803D; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(21, 128, 61, 0.15);">
                                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line><rect x="6" y="14" width="2" height="2"></rect><rect x="10" y="14" width="2" height="2"></rect><rect x="14" y="14" width="2" height="2"></rect></svg>
                              </div>
                              <div style="font-size: 0.8em; font-weight: 700; color: #166534; margin-bottom: 6px;">Input Kas</div>
                              <div style="font-size: 0.65em; color: #64748B; font-weight: 500; padding: 0 4px; line-height: 1.3;">Catat pemasukan<br>kas harian</div>
                          </div>

                          <!-- Input Beban -->
                          <a href="/beban" style="flex: 1; min-width: 90px; border-radius: 16px; padding: 16px 8px; background: #fff; border: 1px solid #f0f0f0; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; text-decoration: none; text-align: center; transition: 0.2s; box-shadow: 0 2px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 15px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 10px rgba(0,0,0,0.02)';">
                              <div style="background: linear-gradient(135deg, #FFEDD5, #FFF7ED); color: #C2410C; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(194, 65, 12, 0.15);">
                                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="2"></circle><line x1="12" y1="11" x2="12" y2="11.01"></line></svg>
                              </div>
                              <div style="font-size: 0.8em; font-weight: 700; color: #9A3412; margin-bottom: 6px;">Input Beban</div>
                              <div style="font-size: 0.65em; color: #64748B; font-weight: 500; padding: 0 4px; line-height: 1.3;">Catat pengeluaran<br>operasional</div>
                          </a>
                          {% endif %}

                          {% if 'sparepart' in session.get('permissions', '') %}
                          <!-- Sparepart -->
                          <div onclick="bukaPopupSparepart()" style="flex: 1; min-width: 90px; border-radius: 16px; padding: 16px 8px; background: #fff; border: 1px solid #f0f0f0; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; cursor: pointer; text-align: center; transition: 0.2s; box-shadow: 0 2px 10px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 15px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 10px rgba(0,0,0,0.02)';">
                              <div style="background: linear-gradient(135deg, #DBEAFE, #EFF6FF); color: #1D4ED8; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(29, 78, 216, 0.15);">
                                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                              </div>
                              <div style="font-size: 0.8em; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">Sparepart</div>
                              <div style="font-size: 0.65em; color: #64748B; font-weight: 500; padding: 0 4px; line-height: 1.3;">Kelola data<br>sparepart</div>
                          </div>
                          {% endif %}
                      </div>
                  </div>

                  <!-- INSIGHT HARI INI CONTAINER -->
                  <div style="flex: 1; min-width: 250px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 15px 20px; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03);">
                      <div style="font-size: 0.85em; font-weight: 800; color: var(--dark); text-transform: uppercase; margin-bottom: 20px; letter-spacing: 0.5px;">INSIGHT HARI INI</div>
                      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                          <!-- Masuk -->
                          <div style="flex: 1; min-width: 80px; border-radius: 12px; padding: 12px 8px; background: #F5F8FF; border: 1px solid #E5EDFF; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px; text-align: center;">
                              <div style="font-size: 0.75em; font-weight: 700; color: #2563EB; margin-bottom: 4px;">Unit Masuk</div>
                              <div style="color: #2563EB; margin-bottom: 8px;">
                                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="12" y1="2" x2="12" y2="8"></line><polyline points="9 5 12 8 15 5"></polyline></svg>
                              </div>
                              <div style="font-size: 1.2em; font-weight: 800; color: #1E3A8A;">{{ jml_masuk }}</div>
                          </div>

                          <!-- Selesai -->
                          <div style="flex: 1; min-width: 80px; border-radius: 12px; padding: 12px 8px; background: #ECFDF5; border: 1px solid #D1FAE5; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px; text-align: center;">
                              <div style="font-size: 0.75em; font-weight: 700; color: #059669; margin-bottom: 4px;">Unit Selesai</div>
                              <div style="color: #059669; margin-bottom: 8px;">
                                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                              </div>
                              <div style="font-size: 1.2em; font-weight: 800; color: #064E3B;">{{ jml_selesai }}</div>
                          </div>

                          <!-- Cash -->
                          <div style="flex: 1; min-width: 80px; border-radius: 12px; padding: 12px 8px; background: #FFFBEB; border: 1px solid #FEF3C7; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px; text-align: center;">
                              <div style="font-size: 0.75em; font-weight: 700; color: #D97706; margin-bottom: 4px;">Unit Cash</div>
                              <div style="color: #D97706; margin-bottom: 8px;">
                                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="2"></circle><path d="M6 12h.01M18 12h.01"></path></svg>
                              </div>
                              <div style="font-size: 1.2em; font-weight: 800; color: #78350F;">{{ jml_cash }}</div>
                          </div>

                          <!-- Pending -->
                          <div style="flex: 1; min-width: 80px; border-radius: 12px; padding: 12px 8px; background: #FEF2F2; border: 1px solid #FEE2E2; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100px; text-align: center;">
                              <div style="font-size: 0.75em; font-weight: 700; color: #DC2626; margin-bottom: 4px;">Unit Pending</div>
                              <div style="color: #DC2626; margin-bottom: 8px;">
                                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                              </div>
                              <div style="font-size: 1.2em; font-weight: 800; color: #7F1D1D;">{{ jml_pending }}</div>
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
              \n"""

html = html[:start_idx] + pristine_html + html[end_idx:]

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Pristine rewrite successful!")
