with open('static/dashboard.css', 'r', encoding='utf-8') as f:
    content = f.read()

if 'The following is an <EPHEMERAL_MESSAGE>' in content:
    content = content.split('The following is an <EPHEMERAL_MESSAGE>')[0]
    
with open('static/dashboard.css', 'w', encoding='utf-8') as f:
    f.write(content.strip())
