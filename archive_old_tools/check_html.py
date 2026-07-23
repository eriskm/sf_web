import re
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<!-- QUICK STATS (Top Row) -->')
end = html.find('<!-- ACTION & INSIGHT ROW -->')
if start != -1 and end != -1:
    print(html[start:end][:2000]) # print first 2000 chars to avoid overwhelming output
else:
    print("Could not find blocks. Printing first 1000 chars of dashboard:")
    print(html[:1000])
