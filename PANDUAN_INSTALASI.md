# 🚀 Panduan Instalasi Sukabumi Flasher Management System

Ikuti langkah-langkah di bawah ini untuk memasang software di komputer toko:

## 1. Persiapan Software Pendukung
Pastikan komputer kamu sudah terpasang:
*   **Python 3.10 atau versi terbaru**: [Download di sini](https://www.python.org/downloads/) (⚠️ **PENTING**: Saat instal, centang pilihan **"Add Python to PATH"**).
*   **XAMPP**: Untuk database MySQL (Lemari Baja). Pastikan Apache dan MySQL sudah dalam posisi **START**.
*   **Google Chrome**: Diperlukan oleh sistem untuk membuat Nota Digital otomatis.

## 2. Instalasi Library (Hanya Sekali)
Buka folder **SF_WEB**, klik kanan di area kosong, pilih **"Open in Terminal"** atau **"Open Command Window Here"**, lalu ketik perintah ini:
```bash
pip install -r requirements.txt
```
Tunggu sampai proses selesai. Ini akan mendownload semua bahan yang dibutuhkan.

## 3. Cara Menjalankan Software
Untuk menjalankan program setiap hari:
1.  Buka XAMPP dan klik **Start** pada Apache & MySQL.
2.  Buka folder **SF_WEB**.
3.  Klik dua kali file **`jalankan.bat`**.
4.  Akan muncul jendela hitam (CMD), jangan ditutup selama program dipakai.
5.  Buka browser (Chrome/Edge), lalu ketik alamat ini:
    `http://127.0.0.1:5000`

## 4. Akun Login Default
*   **Username**: `admin`
*   **Password**: `admin123`
*(Bisa diganti di menu Kelola Akun setelah login)*

---
### 💡 Tips Operasional:
*   **Nota Digital**: Gambar nota akan tersimpan otomatis di folder `static/nota_digital/`.
*   **Database**: Backup file `sukabumi_flasher.db` secara berkala ke Flashdisk atau Cloud untuk keamanan data harian.
*   **WhatsApp**: Pastikan aplikasi WhatsApp Desktop sudah terbuka dan login agar fitur kirim laporan lancar.

**Selamat Menggunakan, Semoga Sukabumi Flasher Makin Jaya!** 📱🔥🦾
