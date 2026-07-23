import re

with open('e:/SFS PROJECK/SF_WEB/templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS adjustments: add --bg-card and dark mode vars
css_insert = '''        :root {
            --navy-dark: #0F172A;
            --navy-light: #1E293B;
            --blue-primary: #3B82F6;
            --green-profit: #10B981;
            --red-expense: #F43F5E;
            --orange-ops: #F59E0B;
            --purple-secondary: #8B5CF6;
            --bg-soft: #F8FAFC;
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --card-radius: 16px;
            --bg-card: #ffffff;
            --border-soft: #e2e8f0;
            --border-light: rgba(0,0,0,0.05);
        }

        [data-theme="dark"] {
            --bg-soft: #0b111e;
            --text-dark: #f8fafc;
            --text-muted: #94a3b8;
            --bg-card: #131b2c;
            --border-soft: #1e293b;
            --border-light: rgba(255,255,255,0.05);
            --navy-dark: #1e293b;
            --navy-light: #334155;
        }'''

# Replace the original :root block
content = re.sub(r':root\s*\{[^}]*\}', css_insert, content, count=1)

# Add theme toggling JS in the head
js_script = '''
    <script>
        // Init theme from localStorage
        if (localStorage.getItem('theme') === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            if (current === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            }
        }
    </script>
</head>'''
content = content.replace('</head>', js_script)

# Add toggle button in header
header_find = '<div style="color: #94A3B8; font-size: 1.3em; margin-right: 5px;">☀️</div>'
toggle_btn = '<button onclick="toggleTheme()" style="background: transparent; border: none; font-size: 1.3em; margin-right: 5px; cursor: pointer;" title="Toggle Mode">🌗</button>'
content = content.replace(header_find, toggle_btn)

# Replace hardcoded colors with variables
content = re.sub(r'background:\s*white;?', 'background: var(--bg-card);', content, flags=re.IGNORECASE)
content = re.sub(r'background:\s*#ffffff;?', 'background: var(--bg-card);', content, flags=re.IGNORECASE)
content = re.sub(r'background:\s*#F8FAFC;?', 'background: var(--bg-soft);', content, flags=re.IGNORECASE)
content = re.sub(r'background:\s*#f8fafc;?', 'background: var(--bg-soft);', content, flags=re.IGNORECASE)
content = re.sub(r'color:\s*#0F172A;?', 'color: var(--text-dark);', content, flags=re.IGNORECASE)
content = re.sub(r'color:\s*#0f172a;?', 'color: var(--text-dark);', content, flags=re.IGNORECASE)
content = re.sub(r'color:\s*#64748B;?', 'color: var(--text-muted);', content, flags=re.IGNORECASE)
content = re.sub(r'color:\s*#64748b;?', 'color: var(--text-muted);', content, flags=re.IGNORECASE)
content = re.sub(r'border:\s*1px\s*solid\s*#e2e8f0;?', 'border: 1px solid var(--border-soft);', content, flags=re.IGNORECASE)
content = re.sub(r'border:\s*1px\s*solid\s*#E2E8F0;?', 'border: 1px solid var(--border-soft);', content, flags=re.IGNORECASE)
content = re.sub(r'border:\s*1px\s*solid\s*#f0f0f0;?', 'border: 1px solid var(--border-soft);', content, flags=re.IGNORECASE)
content = re.sub(r'border:\s*1px\s*solid\s*#F1F5F9;?', 'border: 1px solid var(--border-soft);', content, flags=re.IGNORECASE)
content = re.sub(r'border-bottom:\s*1px\s*solid\s*#e2e8f0;?', 'border-bottom: 1px solid var(--border-soft);', content, flags=re.IGNORECASE)

with open('e:/SFS PROJECK/SF_WEB/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced styles successfully")
