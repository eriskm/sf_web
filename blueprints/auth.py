import imghdr
import os
import time
from datetime import datetime

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from extensions import db_session, get_db, limiter
from utils import login_required


auth_bp = Blueprint('auth', __name__)

ROLE_PERMISSIONS = {
    'admin': 'keuangan,sparepart,servis,tutup_buku,users',
    'teknisi': 'sparepart,servis',
    'kasir': 'servis,pembayaran',
}


@auth_bp.route('/favicon.ico')
def favicon():
    return '', 204


@auth_bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('login.html', error=request.args.get('error'))


@auth_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def login():
    username = str(request.form.get('username') or '').strip()
    password = str(request.form.get('password') or '')
    if not username or not password:
        return redirect(url_for('auth.index', error='Username dan password wajib diisi.'))

    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE LOWER(username) = LOWER(%s) LIMIT 1',
        (username,),
    ).fetchone()

    if not user or not check_password_hash(user['password'], password):
        return redirect(url_for('auth.index', error='Username atau password salah.'))
    if user.get('status') == 'Nonaktif':
        return redirect(url_for('auth.index', error='Akun telah dinonaktifkan oleh admin.'))

    session.clear()
    session.permanent = True
    session['user'] = user['username']
    session['role'] = str(user.get('role') or 'custom').lower()
    session['foto_profil'] = user.get('foto_profil')
    session['nama_lengkap'] = user.get('nama_lengkap') or user['username']
    session['permissions'] = ROLE_PERMISSIONS.get(
        session['role'],
        user.get('permissions') or '',
    )

    try:
        conn.execute(
            'UPDATE users SET last_login = %s WHERE id = %s',
            (f"Hari ini {datetime.now().strftime('%H:%M')}", user['id']),
        )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f'[AUTH] Gagal mencatat last_login: {exc}')

    return redirect(url_for('dashboard.dashboard'))


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.index'))


@auth_bp.route('/upload_foto_profil', methods=['POST'])
@login_required
def upload_foto_profil():
    upload = request.files.get('foto')
    if not upload or not upload.filename:
        return jsonify({'success': False, 'message': 'Tidak ada file yang dipilih.'}), 400

    image_kind = imghdr.what(upload.stream)
    upload.stream.seek(0)
    extension = {'jpeg': 'jpg', 'png': 'png', 'gif': 'gif'}.get(image_kind)
    if not extension:
        return jsonify({
            'success': False,
            'message': 'Foto profil harus berupa JPG, PNG, atau GIF yang valid.',
        }), 400

    filename = secure_filename(
        f"profil_{session['user']}_{int(time.time())}.{extension}"
    )
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER_PROFIL'], filename)
    upload.save(filepath)
    db_path = f'/static/uploads/profiles/{filename}'

    try:
        with db_session() as conn:
            conn.execute(
                'UPDATE users SET foto_profil = %s WHERE username = %s',
                (db_path, session['user']),
            )
    except Exception:
        if os.path.isfile(filepath):
            os.remove(filepath)
        raise

    session['foto_profil'] = db_path
    return jsonify({
        'success': True,
        'path': db_path,
        'message': 'Foto profil berhasil diperbarui.',
    })
