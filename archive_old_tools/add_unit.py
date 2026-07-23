with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Masuk
html = html.replace(
    '<div style="font-size: 1.2em; font-weight: 800; color: #1E3A8A;">{{ insight_masuk }}</div>',
    '<div style="font-size: 1.2em; font-weight: 800; color: #1E3A8A; line-height: 1;">{{ insight_masuk }}</div>\n                                <div style="font-size: 0.65em; font-weight: 700; color: #1E3A8A; opacity: 0.7; margin-top: 2px;">UNIT</div>'
)

# 2. Selesai
html = html.replace(
    '<div style="font-size: 1.2em; font-weight: 800; color: #064E3B;">{{ insight_selesai }}</div>',
    '<div style="font-size: 1.2em; font-weight: 800; color: #064E3B; line-height: 1;">{{ insight_selesai }}</div>\n                                <div style="font-size: 0.65em; font-weight: 700; color: #064E3B; opacity: 0.7; margin-top: 2px;">UNIT</div>'
)

# 3. Cash
html = html.replace(
    '<div style="font-size: 1.2em; font-weight: 800; color: #78350F;">{{ insight_cash }}</div>',
    '<div style="font-size: 1.2em; font-weight: 800; color: #78350F; line-height: 1;">{{ insight_cash }}</div>\n                                <div style="font-size: 0.65em; font-weight: 700; color: #78350F; opacity: 0.7; margin-top: 2px;">UNIT</div>'
)

# 4. Pending
html = html.replace(
    '<div style="font-size: 1.2em; font-weight: 800; color: #7F1D1D;">{{ insight_pending }}</div>',
    '<div style="font-size: 1.2em; font-weight: 800; color: #7F1D1D; line-height: 1;">{{ insight_pending }}</div>\n                                <div style="font-size: 0.65em; font-weight: 700; color: #7F1D1D; opacity: 0.7; margin-top: 2px;">UNIT</div>'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Added unit tags!")
