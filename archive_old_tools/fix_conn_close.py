with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'return render_template(' in line:
        insert_idx = i
        break

# Find and remove all conn.close() in dashboard() AFTER line 800 but BEFORE insert_idx
for i in range(insert_idx - 1, 800, -1):
    if 'conn.close()' in lines[i]:
        del lines[i]
        insert_idx -= 1

# Add conn.close() right before return render_template
lines.insert(insert_idx, '    conn.close()\n')

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("conn.close() moved to the very end!")
