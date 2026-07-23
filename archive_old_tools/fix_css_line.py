with open('static/dashboard.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

if '<line_number>:' in lines[0]:
    lines = lines[1:]

with open('static/dashboard.css', 'w', encoding='utf-8') as f:
    f.write(''.join(lines))
