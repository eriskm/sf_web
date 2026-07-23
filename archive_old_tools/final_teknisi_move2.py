import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's extract the entire TEKNISI TERBAIK block using regex.
pattern = re.compile(r'<!-- TEKNISI TERBAIK -->\s*<div>\s*<div style="font-weight: 700.*?</div>\s*</div>\s*</div>\s*</div>', re.DOTALL)
match = pattern.search(html)

if match:
    tek_html = match.group(0)
    # Remove it from html
    html = html[:match.start()] + html[match.end():]
    
    # Now find where ACTION & INSIGHT ROW ends.
    # We explicitly know it ends with:
    #                 </div>
    #             </div>\n
    # because of our previous script.
    
    # Actually, we can just inject 	ek_html before the LAST </div> of the ACTION & INSIGHT ROW.
    # To do this safely, we search for <!-- INSIGHT HARI INI CONTAINER --> and find its corresponding </div>.
    # But wait, my previous script hardcoded:
    # """                  ...
    #               </div>
    #               <!-- TEKNISI TERBAIK -->"""
    
    # So if we removed TEKNISI TERBAIK, the html now has:
    # </div>\n              <!-- CHARTS AREA (Old Charts Repurposed) -->
    
    # Let's just find <!-- CHARTS AREA (Old Charts Repurposed) -->
    # The </div> before it is the end of ACTION & INSIGHT ROW.
    
    chart_idx = html.find('<!-- CHARTS AREA')
    if chart_idx != -1:
        # Go backwards from chart_idx to find the </div>
        div_idx = html.rfind('</div>', 0, chart_idx)
        if div_idx != -1:
            # We want to insert 	ek_html right BEFORE this </div>.
            html = html[:div_idx] + '  ' + tek_html + '\n              ' + html[div_idx:]
            
            with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("Successfully moved TEKNISI TERBAIK!")
        else:
            print("Could not find </div> before CHARTS AREA")
    else:
        print("Could not find CHARTS AREA")
else:
    print("Could not match TEKNISI TERBAIK block!")
