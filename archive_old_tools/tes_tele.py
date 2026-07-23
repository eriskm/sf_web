import requests

# Masukkan data rahasia lo di sini (Sama kayak tadi)
TOKEN = '8670230633:AAF91XoMmWQtEM2yN3nF-sLwpTJPJ-XqEiY' 
CHAT_ID = '-1003724043513'

# Teks pengantar yang elegan ala AIS Technologies
pesan = (
    "🏢 *LAPORAN SIKLUS 16.00 - Sukabumi Flasher*\n\n"
    "Selamat sore Tim & Manajemen,\n"
    "Bersama ini kami lampirkan rekap otomatis Buku Kas & Alokasi Bagi Hasil (Aliran Kas) untuk siklus cut-off pukul 16:00 WIB hari ini.\n\n"
    "Semangat!"
)

# PERHATIKAN: URL-nya sekarang pakai 'sendPhoto', bukan 'sendMessage'
url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

# Nama file gambar yang mau lo jadikan kelinci percobaan (pastikan file-nya ada di folder lo)
path_gambar_tes = 'tes.png' 

try:
    print("Membungkus gambar dan bersiap mengirim...")
    with open(path_gambar_tes, 'rb') as img_file:
        payload = {
            'chat_id': CHAT_ID,
            'caption': pesan,
            'parse_mode': 'Markdown'
        }
        files = {
            'photo': img_file
        }
        
        response = requests.post(url, data=payload, files=files)
        
        if response.status_code == 200:
            print("✅ MANTAP BRO! Gambar sukses mendarat di Telegram!")
        else:
            print(f"❌ GAGAL: {response.text}")
            
except FileNotFoundError:
    print(f"❌ BRO! File gambar '{path_gambar_tes}' nggak ketemu. Cek lagi nama dan lokasinya.")
except Exception as e:
    print(f"❌ Error: {e}")