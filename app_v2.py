import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

from extensions import limiter
from utils import csrf_token, validate_csrf_request
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.servis import servis_bp
from blueprints.keuangan import keuangan_bp
from blueprints.cetak import cetak_bp
from blueprints.users import users_bp


def create_app():
    app = Flask(__name__)

    secret_key = os.getenv('FLASK_SECRET_KEY', '').strip()
    if not secret_key:
        raise RuntimeError('FLASK_SECRET_KEY wajib diisi di environment/.env.')
    app.secret_key = secret_key
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['UPLOAD_FOLDER_PROFIL'] = 'static/uploads/profiles'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_PROFIL'], exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    os.makedirs('static/nota_digital', exist_ok=True)
    os.makedirs('static/laporan', exist_ok=True)

    @app.teardown_appcontext
    def close_db(error):
        from flask import g
        if 'db' in g:
            try:
                g.db.close()
            except Exception:
                pass

    @app.before_request
    def enforce_csrf():
        validate_csrf_request()

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'same-origin')
        response.headers.setdefault(
            'Permissions-Policy',
            'camera=(), microphone=(), geolocation=()',
        )
        response.headers.setdefault(
            'Content-Security-Policy',
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: blob: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'self'; form-action 'self'",
        )
        if request.endpoint != 'static':
            response.headers.setdefault('Cache-Control', 'no-store')
        if app.config['SESSION_COOKIE_SECURE']:
            response.headers.setdefault(
                'Strict-Transport-Security',
                'max-age=31536000',
            )
        return response

    app.jinja_env.globals['csrf_token'] = csrf_token

    limiter.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(servis_bp)
    app.register_blueprint(keuangan_bp)
    app.register_blueprint(cetak_bp)
    app.register_blueprint(users_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    print("=========================================")
    print("      MEMULAI SERVER SF WEB (V2)         ")
    print("      Database: Native MySQL             ")
    print("=========================================")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
