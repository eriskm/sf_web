import urllib.request
import urllib.parse
import json

tok = '8670230633:AAF91XoMmWQtEM2yN3nF-sLwpTJPJ-XqEiY'
print("Token:", tok)

try:
    req = urllib.request.Request(f'https://api.telegram.org/bot{tok}/getMe')
    with urllib.request.urlopen(req) as response:
        print('getMe:', response.read().decode('utf-8'))
except Exception as e:
    print('getMe error:', e)

pesan = (
    "🏢 *LAPORAN TUTUP BUKU SIKLUS 16.00*\n"
    "----------------------------------------\n"
    "Selamat sore Tim & Manajemen,\n\n"
    "Siklus operasional hari ini telah ditutup. Bersama ini kami lampirkan rekap otomatis Buku Kas & Alokasi Bagi Hasil (Aliran Kas) sebagai bentuk transparansi dan pertanggungjawaban.\n\n"
    "Terima kasih atas dedikasi dan kerja keras seluruh tim hari ini. Istirahat yang cukup dan tetap semangat! 💪\n"
    "----------------------------------------\n"
    "*SUKABUMI FLASHER*"
)

data = urllib.parse.urlencode({'chat_id': '-1003724043513', 'text': pesan, 'parse_mode': 'Markdown'}).encode('utf-8')
try:
    req = urllib.request.Request(f'https://api.telegram.org/bot{tok}/sendMessage', data=data)
    with urllib.request.urlopen(req) as response:
        print('sendMessage test:', response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code)
    print('Reason:', e.reason)
    print('Error message:', e.read().decode('utf-8'))
except Exception as e:
    print('sendMessage error:', e)
