import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = r'<!-- FINANCIAL CARDS ROW -->\s*<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">'
end_marker = r'<!-- Target Gaji \(CTS\) - Keeping original format with donut chart but matching height -->'

# Find the indices
start_match = re.search(start_marker, html)
end_match = re.search(end_marker, html)

if start_match and end_match:
    # We want to replace everything from the END of start_match to the START of end_match
    start_idx = start_match.end()
    end_idx = end_match.start()
    
    premium_cards = """
                  <!-- Omset Hari Ini -->
                  <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 24px 20px; background: #ffffff; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 16px; transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 10px 25px -5px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px -3px rgba(0,0,0,0.03)';">
                      <div style="width: 64px; height: 64px; border-radius: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: white; background: linear-gradient(135deg, #22c55e, #16a34a); box-shadow: 0 10px 20px -5px rgba(34, 197, 94, 0.5);">
                          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5">
                              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
                              <polyline points="16 7 22 7 22 13"></polyline>
                          </svg>
                      </div>
                      <div style="display: flex; flex-direction: column; gap: 4px;">
                          <div style="color: #64748b; font-size: 13px; font-weight: 600;">Omset Hari Ini</div>
                          <div style="color: #0f172a; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; font-family: 'Inter', 'Poppins', sans-serif;">Rp {{ "{:,}".format(total_penjualan) }}</div>
                          <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                              <span style="padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; background-color: #dcfce7; color: #16a34a;">+12%</span>
                              <span style="color: #94a3b8; font-size: 12px; font-weight: 500;">vs kemarin</span>
                          </div>
                      </div>
                  </div>

                  <!-- Laba Kotor -->
                  <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 24px 20px; background: #ffffff; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 16px; transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 10px 25px -5px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px -3px rgba(0,0,0,0.03)';">
                      <div style="width: 64px; height: 64px; border-radius: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: white; background: linear-gradient(135deg, #3b82f6, #2563eb); box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.5);">
                          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5">
                              <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path>
                              <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path>
                              <path d="M18 12a2 2 0 0 0 0 4h4v-4Z"></path>
                          </svg>
                      </div>
                      <div style="display: flex; flex-direction: column; gap: 4px;">
                          <div style="color: #64748b; font-size: 13px; font-weight: 600;">Laba Kotor</div>
                          <div style="color: #0f172a; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; font-family: 'Inter', 'Poppins', sans-serif;">Rp {{ "{:,}".format(total_laba_kotor) }}</div>
                          <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                              <span style="padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; background-color: #dcfce7; color: #16a34a;">+8%</span>
                              <span style="color: #94a3b8; font-size: 12px; font-weight: 500;">vs kemarin</span>
                          </div>
                      </div>
                  </div>

                  <!-- Total Beban -->
                  <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 24px 20px; background: #ffffff; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 16px; transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 10px 25px -5px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px -3px rgba(0,0,0,0.03)';">
                      <div style="width: 64px; height: 64px; border-radius: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: white; background: linear-gradient(135deg, #f97316, #ea580c); box-shadow: 0 10px 20px -5px rgba(249, 115, 22, 0.5);">
                          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5">
                              <path d="M8 21h8a2 2 0 0 0 2-2v-4a6 6 0 0 0-12 0v4a2 2 0 0 0 2 2z"></path>
                              <path d="M12 15a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"></path>
                              <path d="M10.8 5.2a1 1 0 0 1 2.4 0l1.8 2.8H9l1.8-2.8z"></path>
                          </svg>
                      </div>
                      <div style="display: flex; flex-direction: column; gap: 4px;">
                          <div style="color: #64748b; font-size: 13px; font-weight: 600;">Total Beban</div>
                          <div style="color: #0f172a; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; font-family: 'Inter', 'Poppins', sans-serif;">Rp {{ "{:,}".format(g_hari + o_hari) }}</div>
                          <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                              <span style="padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; background-color: #fee2e2; color: #dc2626;">+5%</span>
                              <span style="color: #94a3b8; font-size: 12px; font-weight: 500;">vs kemarin</span>
                          </div>
                      </div>
                  </div>

                  <!-- Laba Bersih -->
                  <div style="flex: 1; min-width: 240px; border-radius: 20px; padding: 24px 20px; background: #ffffff; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 16px; transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 10px 25px -5px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px -3px rgba(0,0,0,0.03)';">
                      <div style="width: 64px; height: 64px; border-radius: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: white; background: linear-gradient(135deg, #ef4444, #dc2626); box-shadow: 0 10px 20px -5px rgba(239, 68, 68, 0.5);">
                          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5">
                              <polyline points="22 17 13.5 8.5 8.5 13.5 2 7"></polyline>
                              <polyline points="16 17 22 17 22 11"></polyline>
                          </svg>
                      </div>
                      <div style="display: flex; flex-direction: column; gap: 4px;">
                          <div style="color: #64748b; font-size: 13px; font-weight: 600;">Laba Bersih</div>
                          <div style="color: #0f172a; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; font-family: 'Inter', 'Poppins', sans-serif;">Rp {{ "{:,}".format(laba_bersih) }}</div>
                          <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                              <span style="padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; background-color: #fee2e2; color: #dc2626;">-8%</span>
                              <span style="color: #94a3b8; font-size: 12px; font-weight: 500;">vs kemarin</span>
                          </div>
                      </div>
                  </div>

                  """

    new_html = html[:start_idx] + "\n" + premium_cards + "                " + html[end_idx:]
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Cards correctly reinserted!")
else:
    print("Failed to find markers!")

