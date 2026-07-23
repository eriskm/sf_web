import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

bad_snippet = '''// Visual feedback: Ubah kursor jadi loading saat submit form (proses kirim telegram)
document.addEventListener('submit', function() {
    document.body.style.cursor = 'wait';
        btn.innerText = '? Sedang Proses...';
    });
});'''

good_snippet = '''// Visual feedback: Ubah kursor jadi loading saat submit form (proses kirim telegram)
document.addEventListener('submit', function() {
    document.body.style.cursor = 'wait';
    // Cari semua tombol submit dan kasih efek loading
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(btn => {
        btn.style.opacity = '0.7';
        btn.innerText = '? Sedang Proses...';
    });
});'''

if bad_snippet in html:
    html = html.replace(bad_snippet, good_snippet)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed!")
else:
    print("Not found!")
