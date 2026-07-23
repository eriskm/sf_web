import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# For Aksi Cepat cards, remove the description div or hide it, and fix height to make it proportional
html = html.replace(
    'Buat transaksi service baru</div>',
    'Buat transaksi service baru</div>'.replace('font-size: 0.65em;', 'font-size: 0.65em; display: none;')
)
html = html.replace(
    'Catat pemasukan kas harian</div>',
    'Catat pemasukan kas harian</div>'.replace('font-size: 0.65em;', 'font-size: 0.65em; display: none;')
)
html = html.replace(
    'Catat pengeluaran operasional</div>',
    'Catat pengeluaran operasional</div>'.replace('font-size: 0.65em;', 'font-size: 0.65em; display: none;')
)
html = html.replace(
    'Kelola data sparepart</div>',
    'Kelola data sparepart</div>'.replace('font-size: 0.65em;', 'font-size: 0.65em; display: none;')
)

# Set height to 95px and justify-content center for Aksi Cepat cards
# The style starts with: flex: 1; min-width: 80px; border-radius: 12px; padding: 12px 8px; background: #fff;
# Let's just do a regex replace for the Aksi Cepat anchor and div tags
html = re.sub(
    r'(style="flex: 1; min-width: 80px; border-radius: 12px; padding: 12px 8px; background: #fff; border: 1px solid #eee; display: flex; flex-direction: column; align-items: center; justify-content: )flex-start(;.*?")',
    r'\1center; height: 100px\2',
    html
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Fixed proportions!')
