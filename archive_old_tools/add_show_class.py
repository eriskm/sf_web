import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

css_code = """
        /* UTILITY CLASSES */
        .show { display: block !important; }
"""

if '.show { display: block !important; }' not in html:
    html = html.replace('<style>', '<style>' + css_code)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added .show class!")
else:
    print(".show already exists!")
