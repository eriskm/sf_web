import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix for telegram_tutup_buku
code = re.sub(
    r'(hti_lokal\.screenshot.*?save_as=nama_gambar\))\s*kirim_laporan_telegram\(nama_gambar,\s*\"TUTUP\"\)',
    r'\1\n        import threading\n        threading.Thread(target=kirim_laporan_telegram, args=(nama_gambar, "TUTUP")).start()',
    code,
    flags=re.DOTALL
)

# Fix for telegram_buka_buku
code = re.sub(
    r'(hti_lokal\.screenshot.*?save_as=nama_gambar\))\s*kirim_laporan_telegram\(nama_gambar,\s*\"BUKA\"\)',
    r'\1\n        import threading\n        threading.Thread(target=kirim_laporan_telegram, args=(nama_gambar, "BUKA")).start()',
    code,
    flags=re.DOTALL
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Threads added!")
