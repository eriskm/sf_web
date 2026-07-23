import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Match the ACTION & INSIGHT ROW up to its closing tag right before TEKNISI TERBAIK
# It looks like:
#               </div>
#               <!-- TEKNISI TERBAIK -->
#
# Let's find exactly </div>\n              <!-- TEKNISI TERBAIK -->
# We want to replace it with   <!-- TEKNISI TERBAIK --> (removing the </div>)
# AND then we need to add the </div> after the Teknisi block.

tek_start = html.find('<!-- TEKNISI TERBAIK -->')

# Let's just use regex to move the block.
# We want to find:
# </div>\s*<!-- TEKNISI TERBAIK -->(.*?)Rp \{\{ "{:,}".format\(teknisi_terbaik\['revenue'\] or 0\) \}\}</div>\s*</div>\s*</div>\s*</div>
# and replace it with:
# <!-- TEKNISI TERBAIK -->\1Rp {{ "{:,}".format(teknisi_terbaik['revenue'] or 0) }}</div>\n                          </div>\n                      </div>\n                  </div>\n              </div> <!-- Closes ACTION & INSIGHT ROW -->

pattern = re.compile(r'(</div>)\s*(<!-- TEKNISI TERBAIK -->\s*<div>.*?Rp \{\{ "\{:\,\}".format\(teknisi_terbaik\[\'revenue\'\] or 0\) \}\}</div>\s*</div>\s*</div>\s*</div>)', re.DOTALL)
match = pattern.search(html)
if match:
    # Match group 1 is </div>
    # Match group 2 is the entire TEKNISI TERBAIK block (which has 3 closing divs of its own)
    
    # Wait! The original block ends with:
    # </div> (line 1)
    # </div> (line 2)
    # </div> (line 3)
    # </div> (line 4) -- this one might NOT be part of Teknisi Terbaik! Let's be safe.
    
    # Actually, the easiest way:
    # Replace </div>\n              <!-- TEKNISI TERBAIK --> with               <!-- TEKNISI TERBAIK -->
    html = html.replace('</div>\n              <!-- TEKNISI TERBAIK -->', '              <!-- TEKNISI TERBAIK -->')
    
    # Then find the end of Teknisi Terbaik and append </div>
    # The end of Teknisi Terbaik is exactly:
    tek_end_str = """                              <div style="font-size: 24px; font-weight: 800; color: #22C55E; font-family: 'Poppins', sans-serif; line-height: 1;">Rp {{ "{:,}".format(teknisi_terbaik['revenue'] or 0) }}</div>
                          </div>
                      </div>
                  </div>"""
    
    replacement_end = tek_end_str + "\n              </div> <!-- END OF ACTION & INSIGHT ROW -->"
    
    if tek_end_str in html:
        html = html.replace(tek_end_str, replacement_end)
        with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Moved TEKNISI TERBAIK into the flex row!")
    else:
        print("Could not find the end of Teknisi Terbaik string")
else:
    print("Could not find the matching pattern for Teknisi Terbaik relocation.")
