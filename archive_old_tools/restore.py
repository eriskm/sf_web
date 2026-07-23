import re

# 1. Restore dashboard.html
with open('dashboard_747.txt', 'r', encoding='utf-8') as f:
    backup_lines = f.readlines()

# We need everything up to but not including <div id="tabel-kas"
top_html = ""
for line in backup_lines:
    if '<div id="tabel-kas"' in line:
        break
    top_html += line

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    current_html = f.read()

# Replace top part
pattern = r'<!DOCTYPE html>.*?<div id="tabel-kas"'
restored_html = re.sub(pattern, top_html + '<div id="tabel-kas"', current_html, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(restored_html)
print("RESTORED dashboard.html")

# 2. Restore dashboard.css
with open('static/dashboard.css', 'r', encoding='utf-8') as f:
    css = f.read()

# My appended css started with /* NEW UI OVERHAUL CSS */
if '/* NEW UI OVERHAUL CSS */' in css:
    css = css.split('/* NEW UI OVERHAUL CSS */')[0]
    with open('static/dashboard.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("RESTORED dashboard.css")

