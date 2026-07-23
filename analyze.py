import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

models = re.findall(r'class \w+\(db\.Model\):', content)
print('Models:', models)

blueprints = re.findall(r'\w+ = Blueprint\(.*?\)', content)
print('Blueprints:', blueprints)

todos = re.findall(r'(?i)#.*?todo.*', content)
print('TODOs:', todos)

fixmes = re.findall(r'(?i)#.*?fixme.*', content)
print('FIXMEs:', fixmes)

complex_funcs = []
for match in re.finditer(r'def (\w+)\(.*?\):', content):
    func_name = match.group(1)
    start = match.end()
    # Find next def or end of file roughly
    end = content.find('def ', start)
    if end == -1: end = len(content)
    body = content[start:end]
    if body.count('\n') > 50:
        complex_funcs.append((func_name, body.count('\n')))

print('Complex functions (>50 lines):', sorted(complex_funcs, key=lambda x: x[1], reverse=True)[:10])
