import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
start = content.find('async def handle_message_akuntan')
end = content.find('async def handle_message_cs')
if start != -1 and end != -1:
    with open('scratch/akuntan.txt', 'w', encoding='utf-8') as out:
        out.write(content[start:end])
