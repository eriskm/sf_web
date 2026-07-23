import requests
import json
import subprocess
import os
import platform

# Konfigurasi
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"  # Pake Qwen karena pinter dan kenceng

def nanya_ollama(prompt):
    system_prompt = """
    Anda adalah asisten Windows yang ahli. Tugas Anda adalah menerjemahkan perintah pengguna menjadi satu baris perintah POWERSHELL.
    Berikan HANYA kode perintahnya saja, tanpa penjelasan, tanpa tanda backtick, tanpa kata-kata lain.
    Contoh:
    User: Buka notepad
    AI: start-process notepad
    
    User: Cek sisa disk
    AI: Get-PSDrive C | Select-Object Used, Free
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nUser: {prompt}\nAI:",
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json()['response'].strip()
    except Exception as e:
        return f"Error: {e}"

def jalankan_perintah(cmd):
    print(f"\n[AI Menyarankan]: {cmd}")
    konfirmasi = input("Jalankan perintah ini? (y/n): ").lower()
    
    if konfirmasi == 'y':
        try:
            # Jalankan di PowerShell
            result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            if result.stdout:
                print("\n[Hasil]:")
                print(result.stdout)
            if result.stderr:
                print("\n[Error]:")
                print(result.stderr)
        except Exception as e:
            print(f"Gagal mengeksekusi: {e}")
    else:
        print("Perintah dibatalkan.")

def main():
    print("="*50)
    print(" ASISTEN LOKAL SUKABUMI (OLLAMA BRIDGE) ")
    print("="*50)
    print(f"Menggunakan Model: {MODEL_NAME}")
    print("Ketik 'keluar' untuk berhenti.\n")
    
    while True:
        user_input = input("Mau nyuruh apa bro? > ")
        
        if user_input.lower() in ['keluar', 'exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        print("Berpikir...")
        cmd_ai = nanya_ollama(user_input)
        
        if cmd_ai.startswith("Error:"):
            print(cmd_ai)
            print("Pastiin Ollama ente sudah nyala ya bro!")
            continue
            
        jalankan_perintah(cmd_ai)

if __name__ == "__main__":
    main()
