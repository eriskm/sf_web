import os
import requests

def test_kirim():
    tok = '8670230633:AAF91XoMmWQtEM2yN3nF-sLwpTJPJ-XqEiY'
    cid = '-1003724043513'
    path_lengkap = os.path.join('static', 'nota_digital', 'Laporan_Tutup_20260723_161403.png')
    pesan = 'Testing sendPhoto'
    
    url = f"https://api.telegram.org/bot{tok}/sendPhoto"
    try:
        with open(path_lengkap, 'rb') as img_file:
            payload = {'chat_id': cid, 'caption': pesan, 'parse_mode': 'Markdown'}
            files = {'photo': img_file}
            response = requests.post(url, data=payload, files=files, timeout=15)
            if response.status_code == 200:
                print(f"[OK] Sukses! {response.text[:50]}")
            else:
                print(f"[ERROR] Error: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

test_kirim()
