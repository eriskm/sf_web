from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
try:
    template = env.get_template('dashboard.html')
    print("Template parsed successfully. No Jinja syntax errors.")
except Exception as e:
    print("Jinja Syntax Error:", str(e))
