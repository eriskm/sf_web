import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

css_code = """
        /* PROGRESS BAR & CIRCLE */
        .progress-circle {
            position: relative;
            background: conic-gradient(var(--primary) var(--percent), #E2E8F0 0deg);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .progress-circle::before {
            content: '';
            position: absolute;
            inset: 6px;
            background: var(--card-bg);
            border-radius: 50%;
        }
        .progress-inner {
            position: relative;
            z-index: 2;
            font-weight: 800;
            color: var(--dark);
        }
"""

if '.progress-circle' not in html:
    html = html.replace('<style>', '<style>' + css_code)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added CSS!")
else:
    print("CSS already exists!")
