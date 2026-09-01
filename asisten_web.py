import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from utils import csrf_token, validate_csrf_request


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', '').strip()
if not app.secret_key:
    raise RuntimeError('FLASK_SECRET_KEY wajib diisi di environment/.env.')

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434/api/generate')
MODEL_NAME = os.getenv('OLLAMA_ASSISTANT_MODEL', 'qwen2.5:1.5b')


@app.before_request
def enforce_csrf():
    validate_csrf_request()


@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'no-referrer')
    return response


app.jinja_env.globals['csrf_token'] = csrf_token


@app.route('/')
def index():
    return render_template('asisten.html', model=MODEL_NAME)


@app.route('/ask', methods=['POST'])
def ask():
    payload = request.get_json(silent=True) or {}
    user_input = str(payload.get('prompt') or '').strip()
    if not user_input:
        return jsonify({'status': 'error', 'message': 'Pesan tidak boleh kosong.'}), 400
    if len(user_input) > 2000:
        return jsonify({'status': 'error', 'message': 'Pesan terlalu panjang.'}), 400

    system_prompt = (
        'Anda adalah AIS Technologies AI, asisten percakapan operasional. '
        'Berikan jawaban singkat dan aman. Jangan membuat, menyarankan, atau '
        'menjalankan perintah shell, PowerShell, perubahan file, maupun aksi sistem.'
    )
    ollama_payload = {
        'model': MODEL_NAME,
        'prompt': f'{system_prompt}\n\nUser: {user_input}\nAI:',
        'stream': False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=ollama_payload,
            timeout=(3, 60),
        )
        response.raise_for_status()
        ai_response = str(response.json().get('response') or '').strip()
        if not ai_response:
            raise ValueError('Respons model kosong.')
        return jsonify({
            'status': 'success',
            'text': ai_response,
            'is_command': False,
            'command': None,
        })
    except (requests.RequestException, ValueError, KeyError) as exc:
        return jsonify({
            'status': 'error',
            'message': 'Asisten lokal tidak tersedia. Pastikan Ollama sedang berjalan.',
        }), 503


@app.route('/execute', methods=['POST'])
def execute_disabled():
    return jsonify({
        'status': 'error',
        'message': 'Eksekusi perintah sistem dinonaktifkan untuk keamanan.',
    }), 410


if __name__ == '__main__':
    print('Asisten Web berjalan di http://127.0.0.1:5050')
    app.run(host='127.0.0.1', port=5050, debug=False)
