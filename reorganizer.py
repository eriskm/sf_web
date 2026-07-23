import re

def reorder_app():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    blocks = []
    current_block = []
    block_name = "INIT"
    
    for i, line in enumerate(lines):
        # Deteksi awal blok fungsi atau decorator baru (unindented)
        if (line.startswith('@app.') or line.startswith('@bot.') or line.startswith('def ')) and not line.startswith(' '):
            # Simpan blok sebelumnya
            if current_block:
                blocks.append({'name': block_name, 'content': current_block})
            current_block = [line]
            
            # Coba ekstrak nama fungsinya
            m = re.search(r'def (\w+)\(', line)
            if m:
                block_name = m.group(1)
            else:
                # Jika ini decorator, cek baris-baris berikutnya untuk mencari def
                next_def = ""
                for j in range(i+1, min(i+5, len(lines))):
                    m_next = re.search(r'^def (\w+)\(', lines[j])
                    if m_next:
                        next_def = m_next.group(1)
                        break
                block_name = next_def if next_def else line.strip()
        elif line.startswith('if __name__ =='):
            if current_block:
                blocks.append({'name': block_name, 'content': current_block})
            current_block = [line]
            block_name = "MAIN"
        else:
            current_block.append(line)
            
    if current_block:
        blocks.append({'name': block_name, 'content': current_block})

    # Kategori Region
    categories = {
        '1_INIT': [],
        '2_MIDDLEWARE': [],
        '3_AUTH': [],
        '4_USERS': [],
        '5_DASHBOARD': [],
        '6_SERVIS': [],
        '7_KEUANGAN': [],
        '8_NOTA': [],
        '9_BOT_WORKER': [],
        '10_MAIN': []
    }
    
    # Mapping fungsi ke kategori
    cat_map = {
        'get_db': '2_MIDDLEWARE',
        'set_timezone': '2_MIDDLEWARE',
        'close_db': '2_MIDDLEWARE',
        'index': '3_AUTH',
        'logout': '3_AUTH',
        'upload_foto_profil': '3_AUTH',
        
        'manage_users': '4_USERS',
        'users_mockup': '4_USERS',
        'users_mockup_v1': '4_USERS',
        'users_mockup_v2': '4_USERS',
        'add_user': '4_USERS',
        'edit_user': '4_USERS',
        'reset_password': '4_USERS',
        'toggle_status': '4_USERS',
        'delete_user': '4_USERS',
        
        'dashboard': '5_DASHBOARD',
        'search_pelanggan': '5_DASHBOARD',
        'check_wa': '5_DASHBOARD',
        'check_update': '5_DASHBOARD',
        
        'input_baru': '6_SERVIS',
        'preview_input': '6_SERVIS',
        'tambah': '6_SERVIS',
        'detail': '6_SERVIS',
        'update': '6_SERVIS',
        'preview_update': '6_SERVIS',
        'delete': '6_SERVIS',
        'edit_data': '6_SERVIS',
        'simpan_sparepart': '6_SERVIS',
        'delete_sparepart': '6_SERVIS',
        
        'beban': '7_KEUANGAN',
        'tambah_beban': '7_KEUANGAN',
        'edit_beban': '7_KEUANGAN',
        'hapus_beban': '7_KEUANGAN',
        'tambah_tambahan': '7_KEUANGAN',
        'hapus_tambahan': '7_KEUANGAN',
        'portal_pembayaran': '7_KEUANGAN',
        'proses_bayar': '7_KEUANGAN',
        
        'cetak_nota': '8_NOTA',
        'cetak_penerimaan': '8_NOTA',
        'generate_nota_image': '8_NOTA',
        'generate_penerimaan_image': '8_NOTA',
        'nota_bridge': '8_NOTA',
        'wa_selesai': '8_NOTA',
        'engine_dashboard': '8_NOTA',
        'preview_teknisi': '8_NOTA',
        'preview_header': '8_NOTA',
        'milestone_preview': '8_NOTA',
        'favicon': '8_NOTA',
        
        'robot_ais_chat': '9_BOT_WORKER',
        'check_milestone_bg': '9_BOT_WORKER',
        'proses_milestone_bg': '9_BOT_WORKER',
        'telegram_tutup_buku': '9_BOT_WORKER',
        'telegram_buka_buku': '9_BOT_WORKER',
        'eksekusi_db': '9_BOT_WORKER'
    }

    # Distribusi blok
    for b in blocks:
        name = b['name']
        if name == 'INIT':
            categories['1_INIT'].append(b)
        elif name == 'MAIN':
            categories['10_MAIN'].append(b)
        elif name.startswith('@bot.') or 'bot.message_handler' in name or 'send_cek_modal' in name or name in ['send_garansi', 'send_tutup_buku', 'send_rekap_bulanan', 'send_welcome']:
            categories['9_BOT_WORKER'].append(b)
        elif name in cat_map:
            categories[cat_map[name]].append(b)
        else:
            # Fallback if unknown
            if '@bot' in ''.join(b['content']) or 'telebot' in ''.join(b['content']):
                categories['9_BOT_WORKER'].append(b)
            else:
                print(f"WARNING: Unknown block {name}, putting in SERVIS")
                categories['6_SERVIS'].append(b)

    # Susun ulang file
    new_lines = []
    
    headers = {
        '1_INIT': "1. INIT & CONFIG (Import, Setup Flask, Secret Key)",
        '2_MIDDLEWARE': "2. DATABASE & MIDDLEWARE (Timezone, session, g.db)",
        '3_AUTH': "3. AUTENTIKASI & PROFIL (Login, Logout, Profil)",
        '4_USERS': "4. MANAJEMEN USER (Admin Area, CRUD User)",
        '5_DASHBOARD': "5. DASHBOARD & PENCARIAN (Halaman Utama, API Search)",
        '6_SERVIS': "6. TRANSAKSI SERVIS (Input, Update, Detail, Delete)",
        '7_KEUANGAN': "7. KEUANGAN & BEBAN (Beban Harian, Kas Tambahan, Pembayaran)",
        '8_NOTA': "8. NOTA, CETAK & ENGINE RENDER (Cetak Termal, WA Bridge)",
        '9_BOT_WORKER': "9. TELEGRAM BOT & BACKGROUND WORKER (Telebot, Milestone)",
        '10_MAIN': "10. APP RUNNER"
    }
    
    for cat_id in ['1_INIT', '2_MIDDLEWARE', '3_AUTH', '4_USERS', '5_DASHBOARD', '6_SERVIS', '7_KEUANGAN', '8_NOTA', '9_BOT_WORKER', '10_MAIN']:
        new_lines.append(f"\n\n# ==============================================================================\n")
        new_lines.append(f"# {headers[cat_id]}\n")
        new_lines.append(f"# ==============================================================================\n\n")
        for b in categories[cat_id]:
            new_lines.extend(b['content'])
            
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("SUCCESS REORDERING APP.PY!")

if __name__ == '__main__':
    reorder_app()
