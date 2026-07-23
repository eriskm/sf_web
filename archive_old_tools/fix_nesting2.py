import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the extra </div> before INSIGHT HARI INI
html = re.sub(
    r'(</div>\s*</div>\s*)(<!-- INSIGHT HARI INI CONTAINER -->)',
    r'</div>\n                  \2',
    html,
    flags=re.DOTALL
)

# Add the closing </div> before TEKNISI TERBAIK
html = re.sub(
    r'(</div>\s*)(<!-- TEKNISI TERBAIK -->)',
    r'\1</div>\n              \2',
    html,
    flags=re.DOTALL
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed nesting with regex!")
