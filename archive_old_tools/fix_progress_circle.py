import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

css_code = '''
        .progress-circle {
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 50%;
            background: conic-gradient(var(--success) var(--percent, 0%), #E2E8F0 0);
            position: relative;
        }
        .progress-circle::before {
            content: "";
            position: absolute;
            inset: 6px;
            background: #fff;
            border-radius: 50%;
        }
        .progress-inner {
            position: relative;
            z-index: 1;
            font-weight: bold;
            color: var(--dark);
        }
'''

if '.progress-circle {' not in html:
    html = html.replace('/* Helper Utilities */', css_code + '\n        /* Helper Utilities */')
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added progress-circle CSS!")
else:
    # If it is there but broken, replace it
    html = re.sub(r'\.progress-circle\s*\{[^\}]*\}', css_code, html, count=1)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed progress-circle CSS!")
