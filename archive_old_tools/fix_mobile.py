with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add a style block right before the FINANCIAL CARDS ROW
style_block = """
<style>
@media (max-width: 768px) {
    .prm-card {
        padding: 16px 15px !important;
        gap: 12px !important;
    }
    .prm-icon {
        width: 48px !important;
        height: 48px !important;
        border-radius: 14px !important;
    }
    .prm-icon svg {
        width: 24px !important;
        height: 24px !important;
    }
    .prm-title {
        font-size: 11px !important;
    }
    .prm-value {
        font-size: 18px !important;
    }
    .prm-badge {
        font-size: 10px !important;
        padding: 2px 8px !important;
    }
}
</style>
<!-- FINANCIAL CARDS ROW -->
"""

html = html.replace('<!-- FINANCIAL CARDS ROW -->', style_block)

# Add classes to the Omset, Laba Kotor, Total Beban, Laba Bersih
# The card wrapper
html = html.replace('min-width: 240px; border-radius: 20px; padding: 24px 20px;', 'min-width: 240px; border-radius: 20px; padding: 24px 20px; " class="prm-card')

# Icon box
html = html.replace('width: 64px; height: 64px; border-radius: 20px; display: flex;', 'width: 64px; height: 64px; border-radius: 20px; display: flex; " class="prm-icon')

# Title
html = html.replace('color: #64748b; font-size: 13px; font-weight: 600;', 'color: #64748b; font-size: 13px; font-weight: 600; " class="prm-title')

# Value
html = html.replace('color: #0f172a; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; font-family: \'Inter\', \'Poppins\', sans-serif;', 'color: #0f172a; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1; font-family: \'Inter\', \'Poppins\', sans-serif; " class="prm-value')

# Badge
html = html.replace('padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;', 'padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; " class="prm-badge')


with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Mobile responsiveness applied!")
