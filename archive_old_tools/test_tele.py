import requests

token = '8604967039:AAFbBMb5sMGulDDbGKMAvLsL4Q9uc_cTQvk'
chat_id = '1516667237'
pesan = '? Halo Bos! Bot laporan Sukabumi Flasher sudah berhasil terhubung ke jalur pribadi kamu. Mulai sekarang laporan Servisan Masuk & Cash akan masuk ke sini ya! ??'

url = f'https://api.telegram.org/bot{token}/sendMessage'
payload = {'chat_id': chat_id, 'text': pesan, 'parse_mode': 'Markdown'}
try:
    resp = requests.post(url, data=payload)
    print('Status:', resp.status_code, resp.text)
except Exception as e:
    print('Error:', e)
