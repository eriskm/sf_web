import os
import subprocess
import sys

def run_command(command):
    try:
        print(f"[RUNNING] {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {e.stderr}")
        return False

def update_system():
    print("="*50)
    print("   🚀 AIS GENESIS - AUTO UPDATER CLIENT 🚀")
    print("="*50)
    
    # 1. Pull latest code from GitHub
    print("\n[1/3] Menarik pembaruan dari GitHub...")
    if not run_command("git pull origin main"):
        print("❌ Gagal menarik data dari GitHub. Pastikan Git terpasang dan koneksi internet stabil.")
        return

    # 2. Update Database Schema
    print("\n[2/3] Menyesuaikan struktur database...")
    # Kita panggil script FIX_DATABASE yang tadi sudah dibuat
    if os.path.exists("FIX_DATABASE.py"):
        run_command("python FIX_DATABASE.py")
    elif os.path.exists("update SF/FIX_DATABASE.py"):
        run_command("python \"update SF/FIX_DATABASE.py\"")
    else:
        print("⚠️ Script database fix tidak ditemukan, melewati langkah ini.")

    # 3. Selesai
    print("\n[3/3] Pembaruan Selesai!")
    print("="*50)
    print("✅ Sistem Sukabumi Flasher sudah versi terbaru.")
    print("👉 Silakan jalankan kembali app.py")
    print("="*50)
    input("\nTekan ENTER untuk keluar...")

if __name__ == "__main__":
    update_system()
