import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Omset
omset_icon = '<div style="background: rgba(0,0,0,0.03); padding: 8px; border-radius: 10px; color: var(--dark); display: flex;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg></div>'
content = content.replace(
    '<div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Omset Hari Ini</div>',
    f'<div style="display: flex; justify-content: space-between; align-items: flex-start;"><div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Omset Hari Ini</div>{omset_icon}</div>'
)

# 2. Total Laba Kotor
laba_kotor_icon = '<div style="background: rgba(40,167,69,0.1); padding: 8px; border-radius: 10px; color: var(--success); display: flex;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg></div>'
content = content.replace(
    '<div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Total Laba Kotor</div>',
    f'<div style="display: flex; justify-content: space-between; align-items: flex-start;"><div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Total Laba Kotor</div>{laba_kotor_icon}</div>'
)

# 3. Total Beban
beban_icon = '<div style="background: rgba(255,193,7,0.1); padding: 8px; border-radius: 10px; color: var(--warning); display: flex;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg></div>'
content = content.replace(
    '<div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Total Beban</div>',
    f'<div style="display: flex; justify-content: space-between; align-items: flex-start;"><div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Total Beban</div>{beban_icon}</div>'
)

# 4. Laba Bersih
laba_bersih_icon = '<div style="background: rgba(0,123,255,0.1); padding: 8px; border-radius: 10px; color: var(--primary); display: flex;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg></div>'
content = content.replace(
    '<div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Laba Bersih</div>',
    f'<div style="display: flex; justify-content: space-between; align-items: flex-start;"><div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase;">Laba Bersih</div>{laba_bersih_icon}</div>'
)

# 5. Target Gaji
target_icon = '<div style="background: rgba(0,0,0,0.03); padding: 8px; border-radius: 10px; color: var(--dark); display: inline-flex; margin-bottom: 5px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg></div>'
content = content.replace(
    '<div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase; margin-bottom: 5px;">Target Gaji (CTS)</div>',
    f'{target_icon}<div style="font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase; margin-bottom: 5px;">Target Gaji (CTS)</div>'
)

# Insight Hari Ini Icons
masuk_icon = '<div style="background: rgba(0,123,255,0.1); color: var(--primary); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></div>'
content = content.replace(
    '<div style="font-size: 2.2em; font-weight: 800; color: var(--primary); font-family: \'Poppins\', sans-serif;">{{ insight_masuk }}</div>',
    f'{masuk_icon}<div style="font-size: 2em; font-weight: 800; color: var(--primary); font-family: \'Poppins\', sans-serif;">{{{{ insight_masuk }}}}</div>'
)

selesai_icon = '<div style="background: rgba(40,167,69,0.1); color: var(--success); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg></div>'
content = content.replace(
    '<div style="font-size: 2.2em; font-weight: 800; color: var(--success); font-family: \'Poppins\', sans-serif;">{{ insight_selesai }}</div>',
    f'{selesai_icon}<div style="font-size: 2em; font-weight: 800; color: var(--success); font-family: \'Poppins\', sans-serif;">{{{{ insight_selesai }}}}</div>'
)

cash_icon = '<div style="background: rgba(255,193,7,0.1); color: var(--warning); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"></rect><circle cx="12" cy="12" r="2"></circle><path d="M6 12h.01M18 12h.01"></path></svg></div>'
content = content.replace(
    '<div style="font-size: 2.2em; font-weight: 800; color: var(--warning); font-family: \'Poppins\', sans-serif;">{{ insight_cash }}</div>',
    f'{cash_icon}<div style="font-size: 2em; font-weight: 800; color: var(--warning); font-family: \'Poppins\', sans-serif;">{{{{ insight_cash }}}}</div>'
)

pending_icon = '<div style="background: rgba(220,53,69,0.1); color: var(--danger); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg></div>'
content = content.replace(
    '<div style="font-size: 2.2em; font-weight: 800; color: var(--danger); font-family: \'Poppins\', sans-serif;">{{ insight_pending }}</div>',
    f'{pending_icon}<div style="font-size: 2em; font-weight: 800; color: var(--danger); font-family: \'Poppins\', sans-serif;">{{{{ insight_pending }}}}</div>'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Icons added successfully!')
