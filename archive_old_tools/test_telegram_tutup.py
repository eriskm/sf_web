from app import app
import json

client = app.test_client()
response = client.post('/telegram_tutup_buku')
print("STATUS CODE:", response.status_code)
print("RESPONSE:", response.data.decode('utf-8'))
