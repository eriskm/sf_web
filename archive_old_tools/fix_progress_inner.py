import re

with open('static/dashboard.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace fixed width and height in .progress-inner with scalable properties
css = re.sub(
    r'\.progress-inner\s*\{\s*width:\s*80px;\s*height:\s*80px;',
    '.progress-inner {\n    width: calc(100% - 12px);\n    height: calc(100% - 12px);',
    css
)

with open('static/dashboard.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated dashboard.css!")
