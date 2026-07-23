with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_dashboard = False
dashboard_start = 0
dashboard_end = 0

for i, line in enumerate(lines):
    if line.startswith('def dashboard():'):
        in_dashboard = True
        dashboard_start = i
    if in_dashboard and 'return render_template' in line:
        dashboard_end = i
        break

print(f"Dashboard bounds: {dashboard_start} to {dashboard_end}")

removed = 0
for i in range(dashboard_end - 1, dashboard_start, -1):
    if 'conn.close()' in lines[i]:
        del lines[i]
        removed += 1
        dashboard_end -= 1

lines.insert(dashboard_end, '    conn.close()\n')
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Removed {removed} conn.close() calls")
