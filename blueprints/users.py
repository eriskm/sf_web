import re

from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from extensions import db_session, get_db
from utils import admin_required


users_bp = Blueprint('users', __name__)
VALID_ROLES = {'admin', 'teknisi', 'kasir', 'custom'}
VALID_STATUS = {'Aktif', 'Nonaktif'}
USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9_.-]{3,50}$')


def _clean_role(value):
    role = str(value or 'teknisi').strip().lower()
    if role not in VALID_ROLES:
        raise ValueError('Role tidak valid.')
    return role


@users_bp.route('/users')
@admin_required
def manage_users():
    all_users = get_db().execute('SELECT * FROM users ORDER BY id ASC').fetchall()
    stats = {
        'total': len(all_users),
        'admin': sum(1 for user in all_users if user.get('role', '').lower() == 'admin'),
        'teknisi': sum(1 for user in all_users if user.get('role', '').lower() == 'teknisi'),
        'kasir': sum(1 for user in all_users if user.get('role', '').lower() == 'kasir'),
        'cs': sum(
            1
            for user in all_users
            if user.get('role', '').lower() not in {'admin', 'teknisi', 'kasir'}
        ),
    }
    return render_template('users.html', users=all_users, stats=stats)




@users_bp.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    username = str(request.form.get('username') or '').strip()
    nama_lengkap = str(request.form.get('nama_lengkap') or username).strip()
    password = str(request.form.get('password') or '')
    status = str(request.form.get('status') or 'Aktif').strip()

    try:
        role = _clean_role(request.form.get('role'))
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValueError('Username harus 3-50 karakter: huruf, angka, titik, garis bawah, atau strip.')
        if not nama_lengkap or len(nama_lengkap) > 100:
            raise ValueError('Nama lengkap wajib diisi dan maksimal 100 karakter.')
        if len(password) < 8:
            raise ValueError('Password minimal 8 karakter.')
        if status not in VALID_STATUS:
            raise ValueError('Status akun tidak valid.')

        with db_session() as conn:
            if conn.execute(
                'SELECT id FROM users WHERE LOWER(username) = LOWER(%s) LIMIT 1',
                (username,),
            ).fetchone():
                raise ValueError('Username sudah digunakan.')
            conn.execute(
                """INSERT INTO users
                       (username, nama_lengkap, password, role, status, last_login)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    username,
                    nama_lengkap,
                    generate_password_hash(password),
                    role,
                    status,
                    'Baru dibuat',
                ),
            )
    except ValueError as exc:
        return str(exc), 400

    return redirect(url_for('users.manage_users'))


@users_bp.route('/edit_user/<int:id>', methods=['POST'])
@admin_required
def edit_user(id):
    try:
        nama_lengkap = str(request.form.get('nama_lengkap') or '').strip()
        role = _clean_role(request.form.get('role'))
        if id == 1 and role != 'admin':
            raise ValueError('Role admin utama tidak boleh diubah.')
        if not nama_lengkap or len(nama_lengkap) > 100:
            raise ValueError('Nama lengkap wajib diisi dan maksimal 100 karakter.')
        with db_session() as conn:
            cursor = conn.execute(
                'UPDATE users SET nama_lengkap = %s, role = %s WHERE id = %s',
                (nama_lengkap, role, id),
            )
            if cursor.rowcount == 0:
                return 'User tidak ditemukan.', 404
    except ValueError as exc:
        return str(exc), 400
    return redirect(url_for('users.manage_users'))


@users_bp.route('/reset_password/<int:id>', methods=['POST'])
@admin_required
def reset_password(id):
    password = str(request.form.get('password') or '')
    if len(password) < 8:
        return 'Password minimal 8 karakter.', 400

    with db_session() as conn:
        cursor = conn.execute(
            'UPDATE users SET password = %s WHERE id = %s',
            (generate_password_hash(password), id),
        )
        if cursor.rowcount == 0:
            return 'User tidak ditemukan.', 404
    return redirect(url_for('users.manage_users'))


@users_bp.route('/toggle_status/<int:id>', methods=['POST'])
@admin_required
def toggle_status(id):
    if id == 1:
        return 'Admin utama tidak dapat dinonaktifkan.', 400

    with db_session() as conn:
        user = conn.execute('SELECT status FROM users WHERE id = %s', (id,)).fetchone()
        if not user:
            return 'User tidak ditemukan.', 404
        new_status = 'Nonaktif' if user.get('status') == 'Aktif' else 'Aktif'
        conn.execute('UPDATE users SET status = %s WHERE id = %s', (new_status, id))
    return redirect(url_for('users.manage_users'))


@users_bp.route('/delete_user/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    if id == 1:
        return 'Admin utama tidak boleh dihapus.', 400

    with db_session() as conn:
        user = conn.execute('SELECT username FROM users WHERE id = %s', (id,)).fetchone()
        if not user:
            return 'User tidak ditemukan.', 404
        if user['username'] == session.get('user'):
            return 'Akun yang sedang digunakan tidak dapat dihapus.', 400
        conn.execute('DELETE FROM users WHERE id = %s', (id,))
    return redirect(url_for('users.manage_users'))
