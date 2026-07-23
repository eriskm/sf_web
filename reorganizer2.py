import re

def reorder_app2():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 1. Temukan baris pertama dari @app.route
    first_route_idx = 0
    for i, l in enumerate(lines):
        if l.startswith('@app.route'):
            first_route_idx = i - 1  # include the @app.errorhandler just before it if possible
            if '@app.errorhandler' in lines[i-3]: first_route_idx = i-3
            break

    # 2. Temukan baris di mana bot telegram dimulai
    bot_start_idx = len(lines)
    for i, l in enumerate(lines):
        if l.startswith('def ai_tambah_servis'): # start of bot logic
            bot_start_idx = i
            break

    top_part = lines[:first_route_idx]
    bottom_part = lines[bot_start_idx:]
    routes_part = lines[first_route_idx:bot_start_idx]

    # Pisahkan routes_part menjadi blok-blok fungsi
    blocks = []
    current_block = []
    block_name = ""
    
    for line in routes_part:
        if (line.startswith('@app.') or line.startswith('def ')) and not line.startswith(' '):
            if current_block:
                blocks.append({'name': block_name, 'content': current_block})
            current_block = [line]
            m = re.search(r'def (\w+)\(', line)
            block_name = m.group(1) if m else line.strip()
        else:
            if not current_block:
                current_block = [line]
            else:
                current_block.append(line)
                
            # If we didn't find def yet, try to find it
            if not block_name or block_name.startswith('@app.'):
                m = re.search(r'^def (\w+)\(', line)
                if m: block_name = m.group(1)
                
    if current_block:
        blocks.append({'name': block_name, 'content': current_block})

    categories = {
        '3_AUTH': [], '4_USERS': [], '5_DASHBOARD': [], '6_SERVIS': [], 
        '7_KEUANGAN': [], '8_NOTA': [], '9_BOT_ROUTES': []
    }
    
    cat_map = {
        'index': '3_AUTH', 'logout': '3_AUTH', 'upload_foto_profil': '3_AUTH',
        'manage_users': '4_USERS', 'users_mockup': '4_USERS', 'users_mockup_v1': '4_USERS', 'users_mockup_v2': '4_USERS',
        'add_user': '4_USERS', 'edit_user': '4_USERS', 'reset_password': '4_USERS', 'toggle_status': '4_USERS', 'delete_user': '4_USERS',
        'dashboard': '5_DASHBOARD', 'search_pelanggan': '5_DASHBOARD', 'check_wa': '5_DASHBOARD', 'check_update': '5_DASHBOARD',
        'input_baru': '6_SERVIS', 'preview_input': '6_SERVIS', 'tambah': '6_SERVIS', 'detail': '6_SERVIS', 'update': '6_SERVIS',
        'preview_update': '6_SERVIS', 'delete': '6_SERVIS', 'edit_data': '6_SERVIS', 'simpan_sparepart': '6_SERVIS', 'delete_sparepart': '6_SERVIS',
        'beban': '7_KEUANGAN', 'tambah_beban': '7_KEUANGAN', 'edit_beban': '7_KEUANGAN', 'hapus_beban': '7_KEUANGAN',
        'tambah_tambahan': '7_KEUANGAN', 'hapus_tambahan': '7_KEUANGAN', 'portal_pembayaran': '7_KEUANGAN', 'proses_bayar': '7_KEUANGAN',
        'cetak_nota': '8_NOTA', 'cetak_penerimaan': '8_NOTA', 'generate_nota_image': '8_NOTA', 'generate_penerimaan_image': '8_NOTA',
        'nota_bridge': '8_NOTA', 'wa_selesai': '8_NOTA', 'engine_dashboard': '8_NOTA', 'preview_teknisi': '8_NOTA',
        'preview_header': '8_NOTA', 'milestone_preview': '8_NOTA', 'favicon': '8_NOTA',
        
        'robot_ais_chat': '9_BOT_ROUTES', 'telegram_tutup_buku': '9_BOT_ROUTES', 'telegram_buka_buku': '9_BOT_ROUTES', 'eksekusi_db': '9_BOT_ROUTES'
    }

    for b in blocks:
        if b['name'] in cat_map:
            categories[cat_map[b['name']]].append(b)
        else:
            categories['6_SERVIS'].append(b) # Fallback

    new_lines = []
    
    new_lines.append("# ==============================================================================\n")
    new_lines.append("# 1 & 2. INIT, CONFIG & MIDDLEWARE\n")
    new_lines.append("# ==============================================================================\n")
    new_lines.extend(top_part)
    
    headers = {
        '3_AUTH': "3. AUTENTIKASI & PROFIL (Login, Logout, Profil)",
        '4_USERS': "4. MANAJEMEN USER (Admin Area, CRUD User)",
        '5_DASHBOARD': "5. DASHBOARD & PENCARIAN (Halaman Utama, API Search)",
        '6_SERVIS': "6. TRANSAKSI SERVIS (Input, Update, Detail, Delete)",
        '7_KEUANGAN': "7. KEUANGAN & BEBAN (Beban Harian, Kas Tambahan, Pembayaran)",
        '8_NOTA': "8. NOTA, CETAK & ENGINE RENDER (Cetak Termal, WA Bridge)",
        '9_BOT_ROUTES': "9. RUTE WEBHOOK / TELEGRAM BOT"
    }
    
    for cat in ['3_AUTH', '4_USERS', '5_DASHBOARD', '6_SERVIS', '7_KEUANGAN', '8_NOTA', '9_BOT_ROUTES']:
        new_lines.append(f"\n\n# ==============================================================================\n")
        new_lines.append(f"# {headers[cat]}\n")
        new_lines.append(f"# ==============================================================================\n\n")
        for b in categories[cat]:
            new_lines.extend(b['content'])

    new_lines.append(f"\n\n# ==============================================================================\n")
    new_lines.append(f"# 10. TELEGRAM BOT CORE LOGIC & BACKGROUND WORKERS\n")
    new_lines.append(f"# ==============================================================================\n\n")
    new_lines.extend(bottom_part)
            
    with open('app_reordered_safe.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("SUCCESS REORDERING TO app_reordered_safe.py!")

if __name__ == '__main__':
    reorder_app2()
