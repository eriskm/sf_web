import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need to extract the entire TEKNISI TERBAIK block and move it inside the flex row.
# TEKNISI TERBAIK ends with:
#                           </div>
#                       </div>
#                   </div>
#               </div>
#           </div>
#       </div> <!-- This closes main-content? -->

# Actually, let's just find the closing tag of ACTION & INSIGHT ROW.
# Since I explicitly set it earlier:
#             </div>
#             <!-- TEKNISI TERBAIK -->

pattern = re.compile(r'              </div>\n              <!-- TEKNISI TERBAIK -->', re.DOTALL)
if pattern.search(html):
    # Simply swap them! Put the closing div AFTER TEKNISI TERBAIK block.
    # But wait, how long is TEKNISI TERBAIK?
    # It ends with </div> \n </div> \n </div>
    pass

# Better to extract TEKNISI TERBAIK block
tek_pattern = re.compile(r'<!-- TEKNISI TERBAIK -->\s*<div>\s*<div style="font-weight: 700.*?</div>\s*</div>\s*</div>\s*</div>', re.DOTALL)
tek_match = tek_pattern.search(html)

if tek_match:
    tek_html = tek_match.group(0)
    # Remove from current location
    html = html[:tek_match.start()] + html[tek_match.end():]
    
    # Now insert it right before the last closing div of ACTION & INSIGHT ROW
    # Wait, the ACTION & INSIGHT ROW is currently closed right before where TEKNISI TERBAIK used to be!
    # Because they are adjacent:
    # </div>
    # <!-- TEKNISI TERBAIK -->
    
    # If they are adjacent, moving the </div> from before TEKNISI to after TEKNISI is all we need!
    # Let's find:
    adj_pattern = re.compile(r'(\s+)</div>\s*<!-- TEKNISI TERBAIK -->(.*?)</div>\s*</div>\s*</div>\s*</div>', re.DOTALL)
    
    # Wait, let's just do it cleanly by finding INSIGHT HARI INI's end, and the row's end.
    
    # Let's just find <!-- TEKNISI TERBAIK --> and move it into the row.
    
    html = html.replace('</div>\n              <!-- TEKNISI TERBAIK -->', '  <!-- TEKNISI TERBAIK -->')
    
    # But now we need to add the closing div AFTER Teknisi Terbaik!
    # The TEKNISI TERBAIK block has a root <div>.
    # Let's just find the end of the TEKNISI TERBAIK root div.
    # We can match Top of the Day to Rp {{ ... }} </div> </div> </div>
    
    # Instead of regex guessing, let's use string operations:
    
