import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

target_pat = re.compile(
    r'<div style="font-size: 1\.6em; font-weight: 800; color: var\(--dark\); font-family: \'Poppins\', sans-serif; line-height: 1\.1;">Rp \{\{ "\{:,\}"\.format\(g_hari\) \}\}</div>\s*'
    r'<div style="font-size: 0\.85em; color: #ef4444; font-weight: 600; margin-top: 4px; margin-bottom: 8px;">\s*'
    r'\{% set kurang = g_hari - total_laba_kotor %\}\s*'
    r'\{% if kurang > 0 %\}\s*'
    r'Kurang Rp \{\{ "\{:,\}"\.format\(kurang\) \}\} lagi\s*'
    r'\{% else %\}\s*'
    r'<span style="color: #10B981;">Target Tercapai! \?\?</span>\s*'
    r'\{% endif %\}\s*'
    r'</div>\s*'
    r'<div style="width: 100%; background: #E2E8F0; border-radius: 4px; height: 6px; overflow: hidden;">\s*'
    r'<div style="height: 100%; background: var\(--primary\); width: \{\{ persen_total if persen_total <= 100 else 100 \}\}%; border-radius: 4px; transition: width 1s ease-in-out;"></div>\s*'
    r'</div>'
)

replacement = """<div style="font-size: 1.6em; font-weight: 800; color: var(--dark); font-family: 'Poppins', sans-serif; line-height: 1.1; margin-bottom: 8px;">Rp {{ "{:,}".format(g_hari) }}</div>
                            <div style="width: 100%; background: #E2E8F0; border-radius: 4px; height: 6px; overflow: hidden;">
                                <div style="height: 100%; background: var(--primary); width: {{ persen_total if persen_total <= 100 else 100 }}%; border-radius: 4px; transition: width 1s ease-in-out;"></div>
                            </div>
                            <div style="font-size: 0.85em; color: var(--dark); font-weight: 600; margin-top: 8px;">
                                {% set kurang = g_hari - total_laba_kotor %}
                                {% if kurang > 0 %}
                                  Kurang <span style="color: #ef4444;">Rp {{ "{:,}".format(kurang) }}</span> lagi
                                {% else %}
                                  <span style="color: #10B981;">Target Tercapai! ??</span>
                                {% endif %}
                            </div>"""

if target_pat.search(html):
    html = target_pat.sub(replacement, html, 1)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Repositioned successfully!")
else:
    print("Could not match the target block.")

