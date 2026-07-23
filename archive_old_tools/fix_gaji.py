import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = r'<div style="font-size: 1.6em; font-weight: 800; color: var\(--dark\); font-family: \'Poppins\', sans-serif; line-height: 1.1; margin-bottom: 8px;">Rp {{ "\{:,\}".format\(g_hari\) }}</div>'

replacement = """<div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1;">Rp {{ "{:,}".format(g_hari) }}</div>
                          <div style="font-size: 0.85em; color: #ef4444; font-weight: 600; margin-top: 4px; margin-bottom: 8px;">
                              {% set kurang = g_hari - total_laba_kotor %}
                              {% if kurang > 0 %}
                                Kurang Rp {{ "{:,}".format(kurang) }} lagi
                              {% else %}
                                <span style="color: #10B981;">Target Tercapai! ??</span>
                              {% endif %}
                          </div>"""

html = re.sub(target, replacement, html)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Added Kurang Rp lagi!")
