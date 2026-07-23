import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = 'class="progress-inner poppins" style="font-size: 0.35em;"'
replacement = 'class="progress-inner poppins" style="font-size: 0.8em;"'

if target in html:
    html = html.replace(target, replacement)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully increased donut text font size!")
else:
    print("Target string not found.")
