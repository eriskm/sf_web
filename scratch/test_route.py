from app import app
import json

client = app.test_client()
response = client.post('/eksekusi_db', json={
    'uang_fisik': 100000,
    'total_saldo': 500000
})
print("STATUS CODE:", response.status_code)
print("RESPONSE:", response.data.decode('utf-8'))
