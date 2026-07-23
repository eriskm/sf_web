import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the block I added
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if '# 7.8 HITUNG INSIGHT HARI INI & TEKNISI TERBAIK' in line:
        start_idx = i
    if 'return render_template(' in line and start_idx != -1:
        end_idx = i - 1
        break

if start_idx == -1:
    print('Block not found')
    sys.exit(1)

block = lines[start_idx:end_idx]

# Remove the block from its current location
del lines[start_idx:end_idx]

# Find conn.close() which is inside dashboard() right before 7.5 AMBIL DATA ARSIP
insert_idx = -1
for i, line in enumerate(lines):
    if '# 7.5 AMBIL DATA ARSIP DARI MySQL' in line:
        insert_idx = i - 2
        break

if insert_idx == -1:
    print('Insert point not found')
    sys.exit(1)

# Insert the block
for line in reversed(block):
    lines.insert(insert_idx, line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fix applied successfully!")
