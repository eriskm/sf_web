import sys
from app import app
app.testing = True
client = app.test_client()

with client.session_transaction() as sess:
    sess['user'] = 'admin'
    sess['permissions'] = 'keuangan,sparepart'

try:
    response = client.get('/dashboard')
    print("Status:", response.status_code)
    if response.status_code == 500:
        print("Data:", response.data.decode('utf-8')[-2000:])
except Exception as e:
    print("EXCEPTION CAUGHT:", e)
    import traceback
    traceback.print_exc()
