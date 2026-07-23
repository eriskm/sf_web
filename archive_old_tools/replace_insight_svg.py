import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Unit Masuk SVG
masuk_old = r'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-1"></path><polygon points="12 15 17 21 7 21 12 15"></polygon></svg>'
masuk_new = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="12" y1="2" x2="12" y2="8"></line><polyline points="9 5 12 8 15 5"></polyline></svg>'

# 2. Unit Selesai SVG
selesai_old = r'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
selesai_new = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="8 12 11 15 16 9"></polyline></svg>'

# 3. Unit Cash SVG
cash_old = r'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="2"></circle><path d="M6 12h.01M18 12h.01"></path></svg>'
cash_new = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"></path><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"></path><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"></path></svg>'

# 4. Unit Pending SVG
pending_old = r'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
pending_new = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'

# Also increase margin-bottom to make it look nicer with bigger icon
html = html.replace('<div style="color: #2563EB; margin-bottom: 4px;">', '<div style="color: #2563EB; margin-bottom: 8px;">')
html = html.replace('<div style="color: #16A34A; margin-bottom: 4px;">', '<div style="color: #16A34A; margin-bottom: 8px;">')
html = html.replace('<div style="color: #059669; margin-bottom: 4px;">', '<div style="color: #059669; margin-bottom: 8px;">')
html = html.replace('<div style="color: #EA580C; margin-bottom: 4px;">', '<div style="color: #EA580C; margin-bottom: 8px;">')

html = html.replace(masuk_old, masuk_new)
html = html.replace(selesai_old, selesai_new)
html = html.replace(cash_old, cash_new)
html = html.replace(pending_old, pending_new)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Icons replaced!")
