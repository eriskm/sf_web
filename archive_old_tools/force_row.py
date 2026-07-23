import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = '<!-- ACTION & INSIGHT ROW -->'
end_marker = '<!-- CHARTS AREA (Old Charts Repurposed) -->'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx != -1 and end_idx != -1:
    section_html = html[start_idx:end_idx]
    
    # Extract the 3 blocks from inside section_html
    # 1. AKSI CEPAT
    aksi_match = re.search(r'(<!-- AKSI CEPAT CONTAINER -->.*?)(?=<!-- INSIGHT HARI INI CONTAINER -->|<!-- TEKNISI TERBAIK -->|$)', section_html, re.DOTALL)
    aksi_html = aksi_match.group(1).strip() if aksi_match else ""
    
    # Since my previous script messed up the divs, let's just clean up aksi_html so it has exactly 2 closing divs at the end.
    # It should have:
    #                     </div>
    #                 </div>
    # Let's strip trailing divs and manually add them.
    aksi_html = re.sub(r'(</div>\s*)*$', '', aksi_html) + '\n                      </div>\n                  </div>'
    
    # Change min-width: 350px to min-width: 250px so it fits side-by-side
    aksi_html = aksi_html.replace('min-width: 350px;', 'min-width: 250px;')

    # 2. INSIGHT HARI INI
    insight_match = re.search(r'(<!-- INSIGHT HARI INI CONTAINER -->.*?)(?=<!-- TEKNISI TERBAIK -->|<!-- AKSI CEPAT CONTAINER -->|$)', section_html, re.DOTALL)
    insight_html = insight_match.group(1).strip() if insight_match else ""
    insight_html = re.sub(r'(</div>\s*)*$', '', insight_html) + '\n                      </div>\n                  </div>'
    insight_html = insight_html.replace('min-width: 350px;', 'min-width: 250px;')

    # 3. TEKNISI TERBAIK
    tek_match = re.search(r'(<!-- TEKNISI TERBAIK -->.*)', section_html, re.DOTALL)
    tek_html = tek_match.group(1).strip() if tek_match else ""
    # Remove any trailing loose divs from tek_html
    tek_html = re.sub(r'(</div>\s*)*$', '', tek_html) + '\n                          </div>\n                      </div>\n                  </div>\n              </div>'

    # Now manually construct the row perfectly:
    new_section = f"""<!-- ACTION & INSIGHT ROW -->
              <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
                  
                  {aksi_html}

                  {insight_html}

                  {tek_html}

              </div>
              
              """

    # Replace the old section
    html = html[:start_idx] + new_section + html[end_idx:]

    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Rebuilt row perfectly with Python!")
else:
    print("Could not find start or end markers.")
