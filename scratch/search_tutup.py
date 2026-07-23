import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/search_results.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        if re.search(r'tutup', line, re.IGNORECASE) or re.search(r'arsip', line, re.IGNORECASE):
            out.write(f'{i+1}: {line.strip()}\n')
