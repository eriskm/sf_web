import hmac
import secrets
from functools import wraps

from flask import abort, current_app, flash, redirect, request, session, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Anda harus login terlebih dahulu.', 'danger')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


def _permission_set():
    raw_permissions = session.get('permissions', '')
    if isinstance(raw_permissions, str):
        return {item.strip().lower() for item in raw_permissions.split(',') if item.strip()}
    return {str(item).strip().lower() for item in raw_permissions if str(item).strip()}


def permission_required(permission):
    """Require login and a named backend permission (admin always allowed)."""
    permission = permission.strip().lower()

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash('Anda harus login terlebih dahulu.', 'danger')
                return redirect(url_for('auth.index'))
            if session.get('role', '').lower() != 'admin' and permission not in _permission_set():
                return 'Akses ditolak: permission tidak tersedia.', 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Require an authenticated administrator session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Anda harus login terlebih dahulu.', 'danger')
            return redirect(url_for('auth.index'))
        if session.get('role', '').lower() != 'admin':
            return 'Akses ditolak: hanya admin yang diizinkan.', 403
        return f(*args, **kwargs)
    return decorated_function


def csrf_token():
    """Return a per-session CSRF token for HTML forms and AJAX requests."""
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token


def validate_csrf_request():
    """Fail closed for state-changing browser requests."""
    if request.method in {'GET', 'HEAD', 'OPTIONS', 'TRACE'}:
        return

    expected = session.get('_csrf_token')
    supplied = request.headers.get('X-CSRF-Token') or request.form.get('_csrf_token')
    if not expected or not supplied or not hmac.compare_digest(str(expected), str(supplied)):
        abort(400, description='Token CSRF tidak valid atau sudah kedaluwarsa.')


def _internal_serializer():
    return URLSafeTimedSerializer(current_app.secret_key, salt='sf-web-internal-access-v1')


def generate_internal_access_token(purpose):
    """Create a short-lived signed token for local screenshot rendering."""
    return _internal_serializer().dumps({'purpose': purpose})


def verify_internal_access_token(token, purpose, max_age=90):
    if not token:
        return False
    try:
        payload = _internal_serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return False
    return payload.get('purpose') == purpose


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

