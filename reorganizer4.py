def reorder_app_fix():
    with open('backups/fullbackup_before_app_reorder_20260718_135930/app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    part_init = lines[0:559]
    part_auth = lines[559:617] + lines[1662:1667] + lines[1957:1985]
    part_users = lines[1985:2090]
    part_dash = lines[655:1192] + lines[1682:1836]
    part_servis = lines[1192:1207] + lines[1437:1662] + lines[1667:1682] + lines[1836:1957] + lines[2370:2435]
    part_keuangan = lines[2090:2195] + lines[2965:2995]
    
    # Perbaikan: Pisahkan part_nota dengan part_main
    part_nota = lines[617:655] + lines[1207:1437] + lines[2995:3010] + lines[3113:3123]
    part_main = lines[3123:]
    
    part_bot = lines[2195:2370] + lines[2435:2965] + lines[3010:3113]
    
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
    
    add_header("10. APP RUNNER (if __name__ == '__main__')")
    new_lines.extend(part_main)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("SUCCESS REORDERING AND FIXING APP RUNNER LOCATION!")

if __name__ == '__main__':
    reorder_app_fix()
