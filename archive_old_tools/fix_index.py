import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    error = request.args.get('error')
    conn.close()
    return render_template('login.html', error=error)'''

replacement = '''def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    error = request.args.get('error')
    return render_template('login.html', error=error)'''

if target in content:
    content = content.replace(target, replacement)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed index route!")
else:
    print("Target not found! Let me try regex.")
    
    # regex fallback
    pattern = re.compile(r'def index\(\):\s+if \'user\' in session: return redirect\(url_for\(\'dashboard\'\)\)\s+error = request.args.get\(\'error\'\)\s+conn\.close\(\)\s+return render_template\(\'login\.html\', error=error\)')
    match = pattern.search(content)
    if match:
        content = content[:match.start()] + replacement + content[match.end():]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed index route via regex!")

