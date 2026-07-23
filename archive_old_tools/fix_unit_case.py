with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('>UNIT</div>', '>Unit</div>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("UNIT changed to Unit!")
