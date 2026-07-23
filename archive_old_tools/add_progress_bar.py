import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We want to replace the Rp text line in Target Gaji to include the progress bar underneath it.
# The current HTML looks like:
# <div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(g_hari) }}</div>
#                       </div>

target_str = """<div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(g_hari) }}</div>"""

replacement_str = """<div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1; margin-bottom: 8px;">Rp {{ "{:,}".format(g_hari) }}</div>
                          <div style="width: 100%; background: #E2E8F0; border-radius: 4px; height: 6px; overflow: hidden;">
                              <div style="height: 100%; background: var(--primary); width: {{ persen_total if persen_total <= 100 else 100 }}%; border-radius: 4px; transition: width 1s ease-in-out;"></div>
                          </div>"""

if target_str in html:
    html = html.replace(target_str, replacement_str)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully added progress bar!")
else:
    print("Could not find the target string. The layout might have been altered.")
