# Panduan Instalasi SF_WEB V2

SF_WEB V2 memakai Flask dan MySQL/MariaDB. SQLite hanya tersimpan sebagai data legacy dan tidak dipakai oleh runtime V2.

## 1. Persiapan

Pasang komponen berikut:

- Python 3.9 atau lebih baru (64-bit direkomendasikan).
- MySQL atau MariaDB beserta `mysqldump` untuk backup.
- Google Chrome/Chromium untuk pembuatan nota dan laporan gambar.
- Ollama hanya bila fitur asisten lokal akan digunakan.

## 2. Konfigurasi lingkungan

1. Salin `.env.example` menjadi `.env`.
2. Isi `FLASK_SECRET_KEY` dengan nilai acak minimal 32 karakter.
3. Isi `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, dan `MYSQL_DB` dengan akun database khusus aplikasi. Hindari akun `root` untuk operasional.
4. Jika bot Telegram dipakai, isi token yang diperlukan dan `ALLOWED_TELEGRAM_IDS`. Bot sengaja tidak akan berjalan bila whitelist kosong.
5. Gunakan `SESSION_COOKIE_SECURE=true` hanya ketika aplikasi dilayani melalui HTTPS. Untuk akses HTTP lokal, biarkan `false` dan batasi jaringan ke perangkat tepercaya.

Jangan menyimpan `.env` di Git atau membagikan isinya melalui chat/screenshot.

## 3. Instalasi Python

Jalankan `SETUP_PC_BARU.bat`, atau dari terminal di folder proyek:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Pastikan database V2 sudah dibuat atau dipulihkan dari backup MySQL sebelum aplikasi dijalankan.

## 4. Menjalankan aplikasi

1. Pastikan service MySQL/MariaDB aktif.
2. Jalankan `jalankan_web_v2.bat`.
3. Buka `http://127.0.0.1:5000` dari komputer server.
4. Login menggunakan akun administrator yang sudah ada di database. Sistem tidak menyediakan kredensial default di dokumentasi.

Untuk bot Telegram, jalankan `jalankan_bot.bat` setelah token dan whitelist selesai dikonfigurasi.

## 5. Backup

- Backup manual: jalankan `BACKUP_DATABASE.bat`.
- Backup terjadwal: jalankan `SETUP_AUTO_BACKUP.bat` sebagai Administrator satu kali.
- File dump disimpan di folder `backups/`; maksimal 15 backup terbaru dipertahankan.
- Periksa `backups/backup.log` secara berkala untuk memastikan backup terjadwal berhasil.

Sebelum update aplikasi atau perubahan skema, buat backup dan pastikan file SQL tidak kosong.

## 6. Pemeriksaan setelah instalasi

```powershell
.\.venv\Scripts\python.exe config_app.py
.\.venv\Scripts\python.exe smoke_test.py
```

`smoke_test.py` hanya menjalankan request GET. Exit code `2` berarti database tidak dapat dihubungi.

## Catatan keamanan

- Ganti atau rotasi token yang pernah muncul di source code atau riwayat lama.
- Jangan membuka port 5000 ke internet langsung; gunakan reverse proxy HTTPS bila memerlukan akses dari luar LAN.
- Menu pembayaran, keuangan, user, dan tutup buku tetap harus dibatasi berdasarkan role/permission.