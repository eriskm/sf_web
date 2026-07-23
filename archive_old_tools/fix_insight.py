with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('{{ jml_masuk }}', '{{ insight_masuk }}')
html = html.replace('{{ jml_selesai }}', '{{ insight_selesai }}')
html = html.replace('{{ jml_cash }}', '{{ insight_cash }}')
html = html.replace('{{ jml_pending }}', '{{ insight_pending }}')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Insights Fixed!")
