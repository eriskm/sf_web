import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_js = '''        // 1. Ambil screenshot kondisi akhir hari ini (Tutup Buku) & kirim Telegram
        fetch('/telegram_tutup_buku', { method: 'POST' })
        .then(response => {
            if(!response.ok) throw new Error("Gagal kirim Telegram Tutup Buku");
            return response.text();
        })
        .then(() => {
            // 2. Eksekusi semua logika database (mindahin arsip, hapus data lama, set kas baru)
            return fetch('/eksekusi_db', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uang_fisik: uangFisik, total_saldo: totalSaldo })
            });
        })
        .then(response => {
            if(!response.ok) throw new Error("Gagal Eksekusi Database Tutup Kas");
            return response.text();
        })
        .then(msgDB => {
            window.msgDB = msgDB;
            // 3. Ambil screenshot kondisi awal besok (Buka Buku) & kirim Telegram
            return fetch('/telegram_buka_buku', { method: 'POST' });
        })
        .then(response => {
            if(!response.ok) throw new Error("Gagal kirim Telegram Buka Buku");
            return response.text();
        })
        .then(() => {
            document.body.style.cursor = 'default';
            alert("Siklus Selesai Sepenuhnya!\\n\\n" + window.msgDB + "\\nLaporan Tutup & Buka Buku berhasil dikirim ke Telegram.");
            location.reload(); 
        })
        .catch(error => {
            document.body.style.cursor = 'default';
            console.error('Error:', error);
            alert("Terjadi kesalahan saat tutup kas: " + error.message);
        });'''

new_js = '''        // 1. Kirim Telegram Tutup Buku (Jangan biarkan error memblokir reset DB)
        fetch('/telegram_tutup_buku', { method: 'POST' })
        .catch(e => console.warn("Telegram Tutup Buku error/timeout (diabaikan)", e))
        .finally(() => {
            // 2. Eksekusi logika database
            fetch('/eksekusi_db', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uang_fisik: uangFisik, total_saldo: totalSaldo })
            })
            .then(response => {
                if(!response.ok) throw new Error("Gagal Eksekusi Database Tutup Kas");
                return response.text();
            })
            .then(msgDB => {
                window.msgDB = msgDB;
                // 3. Kirim Telegram Buka Buku
                return fetch('/telegram_buka_buku', { method: 'POST' })
                    .catch(e => console.warn("Telegram Buka Buku error (diabaikan)", e));
            })
            .then(() => {
                document.body.style.cursor = 'default';
                alert("Siklus Selesai!\\n\\n" + window.msgDB);
                location.reload(); 
            })
            .catch(error => {
                document.body.style.cursor = 'default';
                console.error('Error DB:', error);
                alert("Terjadi kesalahan sistem saat Eksekusi DB: " + error.message);
            });
        });'''

if old_js in html:
    html = html.replace(old_js, new_js)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("JS Fixed!")
else:
    print("Old JS not found!")
