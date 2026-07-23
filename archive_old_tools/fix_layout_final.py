import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's extract the contents of AKSI CEPAT CONTAINER and INSIGHT HARI INI CONTAINER
# First, remove INSIGHT HARI INI entirely from where it is right now.
insight_block_pattern = re.compile(r'<!-- INSIGHT HARI INI CONTAINER -->.*?</div>\s*</div>\s*</div>\s*(?=</div>|\s*<!-- TEKNISI TERBAIK|<!--)', re.DOTALL)
insight_match = insight_block_pattern.search(html)

if insight_match:
    insight_content = insight_match.group(0)
    html = html[:insight_match.start()] + html[insight_match.end():]
    print("Found and removed existing Insight block.")
else:
    # Let's try a simpler regex
    insight_block_pattern = re.compile(r'<!-- INSIGHT HARI INI CONTAINER -->.*?(?=\s*<!-- TEKNISI TERBAIK)', re.DOTALL)
    insight_match = insight_block_pattern.search(html)
    if insight_match:
        insight_content = insight_match.group(0)
        html = html[:insight_match.start()] + html[insight_match.end():]
        print("Found and removed existing Insight block (simple).")
    else:
        print("Could not find Insight block to remove! Will use predefined one.")
        insight_content = ""

if insight_content:
    # Ensure insight_content has exactly closing divs. 
    # It starts with <!-- INSIGHT... and should end with 3 divs? No, 2 divs. 
    # Let's just use the exact HTML we know works.
    pass

insight_html = """<!-- INSIGHT HARI INI CONTAINER -->
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
                  </div>"""

# Now we find the end of AKSI CEPAT CONTAINER.
# It ends with:
#                           {% endif %}
#                       </div>
#                   </div>
#                   </div>
# OR something similar. We need to inject insight_html right after the closing of AKSI CEPAT.

# Let's locate the exact start of ACTION & INSIGHT ROW
row_start = html.find('<!-- ACTION & INSIGHT ROW -->')
if row_start != -1:
    # Find the end of this row. Wait, if I just replace everything from ACTION & INSIGHT ROW down to TEKNISI TERBAIK
    # I can cleanly rebuild it.
    
    # We need to extract the inner content of AKSI CEPAT CONTAINER to preserve it.
    aksi_cepat_pattern = re.compile(r'<!-- AKSI CEPAT CONTAINER -->(.*?)</div>\s*</div>', re.DOTALL)
    aksi_match = aksi_cepat_pattern.search(html, row_start)
    if aksi_match:
        aksi_html = '<!-- AKSI CEPAT CONTAINER -->' + aksi_match.group(1) + '</div>\n                  </div>'
        
        # Now rebuild the entire section
        rebuilt = f"""<!-- ACTION & INSIGHT ROW -->
              <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
                  {aksi_html}
                  {insight_html}
              </div>
              """
        
        # Replace the whole chunk from ACTION & INSIGHT ROW to right before TEKNISI TERBAIK
        end_idx = html.find('<!-- TEKNISI TERBAIK -->')
        # Wait, there might be stray </div>s before TEKNISI TERBAIK now.
        # Let's just find the first <div that contains TEKNISI TERBAIK
        tek_start = html.find('<!-- TEKNISI TERBAIK -->')
        
        # We replace html[row_start:tek_start] with rebuilt.
        # BUT we must make sure we don't leave stray closing tags.
        # Actually, it's safer to just regex replace from <!-- ACTION & INSIGHT ROW --> to <!-- TEKNISI TERBAIK -->
        html = re.sub(r'<!-- ACTION & INSIGHT ROW -->.*?<!-- TEKNISI TERBAIK -->', rebuilt + '<!-- TEKNISI TERBAIK -->', html, flags=re.DOTALL)
        
        with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Successfully rebuilt the ACTION & INSIGHT ROW!")
    else:
        print("Could not find AKSI CEPAT CONTAINER inside the row.")
else:
    print("Could not find ACTION & INSIGHT ROW")

