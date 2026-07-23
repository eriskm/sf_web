import requests
import json

token = '8604967039:AAFbBMb5sMGulDDbGKMAvLsL4Q9uc_cTQvk'
try:
    resp = requests.get(f'https://api.telegram.org/bot{token}/getUpdates')
    data = resp.json()
    if data.get('ok'):
        for update in data.get('result', []):
            msg = update.get('message') or update.get('channel_post')
            if msg:
                chat = msg.get('chat', {})
                first = chat.get('first_name', '')
                last = chat.get('last_name', '')
                title = chat.get('title', '')
                cid = chat.get('id')
                print(f"Name: {first} {last} {title} --> ID: {cid}")
    else:
        print('Error:', data)
except Exception as e:
    print('Exception:', e)
