with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

if 'The following is an <EPHEMERAL_MESSAGE>' in content:
    content = content.split('The following is an <EPHEMERAL_MESSAGE>')[0]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print("Fixed HTML")
else:
    print("HTML OK")
