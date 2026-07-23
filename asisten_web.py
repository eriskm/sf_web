from flask import Flask, render_template, request, jsonify
import requests
import subprocess
import os

app = Flask(__name__)

# Konfigurasi
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

@app.route('/')
def index():
    return render_template('asisten.html', model=MODEL_NAME)

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('prompt')
    
    system_prompt = """
    Anda adalah asisten Windows yang ahli bernama AIS Technologies AI.
    Tugas Anda adalah menerjemahkan perintah pengguna menjadi satu baris perintah POWERSHELL.
    
    ATURAN KHUSUS:
    - Jika perintah adalah aksi sistem, awali WAJIB dengan 'EXEC:'
    - Contoh Buka Web: EXEC:start-process "https://www.google.com"
    - Contoh Buka Aplikasi: EXEC:start-process notepad
    - Contoh Tutup Aplikasi: EXEC:stop-process -name notepad -ErrorAction SilentlyContinue
    
    Jika hanya sapaan atau obrolan biasa, jawablah dengan ramah tanpa awalan EXEC:.
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nUser: {user_input}\nAI:",
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        ai_response = response.json()['response'].strip()
        
        is_command = ai_response.startswith("EXEC:")
        command = ai_response.replace("EXEC:", "").strip() if is_command else None
        text = ai_response if not is_command else f"Saya akan membantu Anda menjalankan perintah: {command}"
        
        return jsonify({
            "status": "success",
            "text": text,
            "is_command": is_command,
            "command": command
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/execute', methods=['POST'])
def execute():
    command = request.json.get('command')
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        return jsonify({
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print(f"Asisten Web berjalan di http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
