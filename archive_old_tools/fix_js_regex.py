import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need to replace everything from // 1. Ambil screenshot kondisi akhir hari ini
# up to the end of the catch block inside kirimDataKas

start_marker = "// 1. Ambil screenshot kondisi akhir hari ini"
end_marker = "alert(\"Terjadi kesalahan saat tutup kas: \" + error.message);\n        });"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_marker)
    new_js = '''// 1. Ambil screenshot kondisi akhir hari ini (Tutup Buku) & kirim Telegram
        // Kita gunakan .catch() agar jika Telegram error/timeout, eksekusi database TETAP BERJALAN!
        fetch('/telegram_tutup_buku', { method: 'POST' })
        .catch(e => {
            console.warn("Peringatan: Telegram Tutup Buku error, namun eksekusi database tetap dilanjutkan.", e);
        })
        .finally(() => {
            // 2. Eksekusi semua logika database (mindahin arsip, hapus data lama, set kas baru)
            fetch('/eksekusi_db', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uang_fisik: uangFisik, total_saldo: totalSaldo })
            })
            .then(response => {
                if(!response.ok) throw new Error("Gagal eksekusi database");
                return response.text();
            })
            .then(msgDB => {
                window.msgDB = msgDB;
                // 3. Ambil screenshot kondisi awal besok (Buka Buku) & kirim Telegram
                return fetch('/telegram_buka_buku', { method: 'POST' })
                    .catch(e => console.warn("Peringatan: Telegram Buka Buku error.", e));
            })
            .then(() => {
                document.body.style.cursor = 'default';
                alert("Siklus Selesai Sepenuhnya!\\n\\n" + window.msgDB + "\\n\\nJika ada notifikasi Telegram gagal, harap abaikan, data aman.");
                location.reload(); 
            })
            .catch(error => {
                document.body.style.cursor = 'default';
                console.error('Error:', error);
                alert("Terjadi kesalahan sistem saat Eksekusi DB: " + error.message);
            });
        });'''
    html = html[:start_idx] + new_js + html[end_idx:]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Replaced!")
else:
    print("Markers not found!")
