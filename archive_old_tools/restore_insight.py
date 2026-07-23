import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

insight_html = """                  <!-- INSIGHT HARI INI CONTAINER -->
                  <div style="flex: 1; min-width: 350px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 15px 20px; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03);">
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
"""

# The previous script might have left a malformed end tag sequence, or we just insert it before TEKNISI TERBAIK
if 'INSIGHT HARI INI CONTAINER' not in html:
    html = html.replace('<!-- TEKNISI TERBAIK -->', insight_html + '\n              <!-- TEKNISI TERBAIK -->')
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Restored Insight Hari Ini!")
else:
    print("Insight is already there?!")
