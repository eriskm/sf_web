with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Fix the milestone return indentation and put conn.close() properly inside the if block
for i, line in enumerate(lines):
    if 'return render_template(\'milestone_view.html\'' in line:
        # Move conn.close() inside the block if it's currently outside
        if 'conn.close()' in lines[i-1]:
            lines[i-1] = '        conn.close()\n'
        break

# 2. Add conn.close() to the very end of dashboard(), right before the final return render_template('dashboard.html'
for i, line in enumerate(lines):
    if 'return render_template(\'dashboard.html\'' in line:
        # Check if conn.close() is already there
        if 'conn.close()' not in lines[i-1] and 'conn.close()' not in lines[i-2]:
            lines.insert(i, '    conn.close()\n')
        break

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("app.py fixed!")
