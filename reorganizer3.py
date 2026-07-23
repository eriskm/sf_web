def reorder_app3():
    with open('backups/fullbackup_before_app_reorder_20260718_135930/app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Exact line slices (0-indexed, so line 1 is index 0. slice(a, b) means lines a to b-1)
    
    # 1 & 2. INIT & MIDDLEWARE (Lines 1 to 559)
    # Includes imports, app=Flask, get_db, auto_backup_worker, before_request, etc
    part_init = lines[0:559]
    
    # 3. AUTH (favicon, index, login, logout, upload_foto)
    part_auth = (
        lines[559:617] +  # favicon, index, login
        lines[1662:1667] + # logout
        lines[1957:1985]   # upload_foto
    )
    
    # 4. USERS (users, mockups, add_user, edit_user, reset_pwd, toggle, delete_user)
    part_users = lines[1985:2090]
    
    # 5. DASHBOARD & PENCARIAN
    part_dash = (
        lines[655:1192] +  # check_update, dashboard
        lines[1682:1836]   # search_pelanggan, check_wa
    )
    
    # 6. TRANSAKSI SERVIS
    part_servis = (
        lines[1192:1207] + # detail
        lines[1437:1662] + # update
        lines[1667:1682] + # input_baru, preview, preview_update
        lines[1836:1957] + # tambah, delete, edit_data
        lines[2370:2435]   # simpan_sparepart, delete_sparepart
    )
    
    # 7. KEUANGAN
    part_keuangan = (
        lines[2090:2195] + # beban, tambah_beban, dll
        lines[2965:2995]   # portal_pembayaran, proses_bayar
    )
    
    # 8. NOTA & ENGINE RENDER
    part_nota = (
        lines[617:655] +   # milestone_preview
        lines[1207:1437] + # cetak_nota, cetak_penerimaan, img_nota, wa_selesai
        lines[2995:3010] + # engine
        lines[3113:3175]   # preview_teknisi, preview_header
    )
    
    # 9. TELEGRAM BOT
    part_bot = (
        lines[2195:2370] + # kirim_laporan_ke_grup, telegram_tutup_buku, eksekusi_db, telegram_buka_buku
        lines[2435:2965] + # ai_tambah_servis, telebot handlers, run_bot
        lines[3010:3113]   # robot_ais_chat
    )
    
    new_lines = []
    
    def add_header(title):
        new_lines.append(f"\n\n# ==============================================================================\n")
        new_lines.append(f"# {title}\n")
        new_lines.append(f"# ==============================================================================\n\n")

    add_header("1 & 2. INIT, CONFIG & MIDDLEWARE")
    new_lines.extend(part_init)
    
    add_header("3. AUTENTIKASI & PROFIL (Login, Logout, Profil)")
    new_lines.extend(part_auth)
    
    add_header("4. MANAJEMEN USER (Admin Area, CRUD User)")
    new_lines.extend(part_users)
    
    add_header("5. DASHBOARD & PENCARIAN (Halaman Utama, API Search)")
    new_lines.extend(part_dash)
    
    add_header("6. TRANSAKSI SERVIS (Input, Update, Detail, Delete)")
    new_lines.extend(part_servis)
    
    add_header("7. KEUANGAN & BEBAN (Beban Harian, Kas Tambahan, Pembayaran)")
    new_lines.extend(part_keuangan)
    
    add_header("8. NOTA, CETAK & ENGINE RENDER (Cetak Termal, WA Bridge)")
    new_lines.extend(part_nota)
    
    add_header("9. TELEGRAM BOT & BACKGROUND WORKER (Telebot, Milestone)")
    new_lines.extend(part_bot)
    
    # Verify we didn't lose any lines (Total should be exactly 3175 + headers)
    total_original = 559 + (617-559) + 5 + 28 + 105 + (1192-655) + (1836-1682) + 15 + 225 + 15 + 121 + 65 + 105 + 30 + 38 + 230 + 15 + 62 + 175 + 530 + 103
    print(f"Total lines sliced: {total_original} vs Original lines: {len(lines)}")
    
    with open('app_reordered_final.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("SUCCESS SLICING!")

if __name__ == '__main__':
    reorder_app3()
