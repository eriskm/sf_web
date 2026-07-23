import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# AKSI CEPAT CONTAINER min-width
html = html.replace('min-width: 500px;', 'min-width: 350px;')
# Padding of the containers
html = html.replace('padding: 24px; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03);', 'padding: 15px 20px; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.03);')

# Aksi Cepat Inner Cards
html = html.replace('min-width: 120px; border-radius: 16px; padding: 20px 10px;', 'min-width: 80px; border-radius: 12px; padding: 12px 8px;')
html = html.replace('width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;', 'width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;')
html = html.replace('font-size: 0.9em; font-weight: 700; color: var(--dark); margin-bottom: 6px;', 'font-size: 0.8em; font-weight: 700; color: var(--dark); margin-bottom: 4px;')
html = html.replace('font-size: 0.7em; color: var(--gray); font-weight: 500; padding: 0 10px; line-height: 1.3;', 'font-size: 0.65em; color: var(--gray); font-weight: 500; padding: 0 5px; line-height: 1.2;')

# Aksi Cepat SVG sizes
html = re.sub(r'svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2\.5"', r'svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"', html)

# Insight Hari Ini Inner Cards
html = html.replace('min-width: 100px; border-radius: 16px; padding: 20px 10px;', 'min-width: 80px; border-radius: 12px; padding: 12px 8px;')
html = html.replace('margin-bottom: 12px;', 'margin-bottom: 8px;')
html = html.replace('font-size: 0.8em; font-weight: 700;', 'font-size: 0.75em; font-weight: 700;')
html = html.replace('font-size: 1.8em; font-weight: 800;', 'font-size: 1.6em; font-weight: 800;')
html = html.replace('margin-top: 6px;', 'margin-top: 4px;')
html = html.replace('margin-bottom: 8px;', 'margin-bottom: 4px;')

# Insight SVG sizes
html = re.sub(r'svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2\.5"', r'svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"', html)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Resized completely!")
