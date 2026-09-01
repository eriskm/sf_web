import imghdr
import os
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from extensions import db_session, get_db
from utils import permission_required


keuangan_bp = Blueprint('keuangan', __name__)


def _positive_int(value, field_name):
    try:
        parsed = int(str(value).replace('.', '').replace(',', '').strip())
    except (TypeError, ValueError):
        raise ValueError(f'{field_name} harus berupa angka.')
    if parsed < 0:
        raise ValueError(f'{field_name} tidak boleh negatif.')
    return parsed


def _database_money(value):
    """Normalize DECIMAL, integer, and legacy numeric strings from MySQL."""
    try:
        return int(Decimal(str(value or 0).strip()))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('Data nominal unit tidak valid.')


@keuangan_bp.route('/beban')
@permission_required('keuangan')
def beban():
    semua_beban = get_db().execute(
        'SELECT * FROM beban ORDER BY kategori, nama_beban'
    ).fetchall()
    return render_template(
        'beban.html',
        tgl=datetime.now().strftime('%Y-%m-%d'),
        beban_list=semua_beban,
    )


@keuangan_bp.route('/edit_beban/<int:id>', methods=['POST'])
@permission_required('keuangan')
def edit_beban(id):
    try:
        nama = str(request.form.get('nama_beban') or '').strip()
        nilai = _positive_int(request.form.get('nilai'), 'Nilai beban')
        if not nama:
            raise ValueError('Nama beban wajib diisi.')
        with db_session() as conn:
            cursor = conn.execute(
                'UPDATE beban SET nama_beban = %s, nilai = %s WHERE id = %s',
                (nama, nilai, id),
            )
            if cursor.rowcount == 0:
                return 'Beban tidak ditemukan.', 404
    except ValueError as exc:
        return str(exc), 400
    return redirect(url_for('keuangan.beban'))


@keuangan_bp.route('/tambah_beban', methods=['POST'])
@permission_required('keuangan')
def tambah_beban():
    try:
        kategori = str(request.form.get('kategori') or '').strip()
        nama = str(request.form.get('nama_beban') or '').strip()
        nilai = _positive_int(request.form.get('nilai'), 'Nilai beban')
        if not kategori or not nama:
            raise ValueError('Kategori dan nama beban wajib diisi.')

        with db_session() as conn:
            existing = conn.execute(
                'SELECT id FROM beban WHERE LOWER(nama_beban) = LOWER(%s) LIMIT 1',
                (nama,),
            ).fetchone()
            if existing:
                conn.execute(
                    'UPDATE beban SET kategori = %s, nilai = %s WHERE id = %s',
                    (kategori, nilai, existing['id']),
                )
            else:
                conn.execute(
                    'INSERT INTO beban (kategori, nama_beban, nilai) VALUES (%s, %s, %s)',
                    (kategori, nama, nilai),
                )
    except ValueError as exc:
        return str(exc), 400
    return redirect(url_for('keuangan.beban'))


@keuangan_bp.route('/hapus_beban/<int:id>', methods=['POST'])
@permission_required('keuangan')
def hapus_beban(id):
    with db_session() as conn:
        conn.execute('DELETE FROM beban WHERE id = %s', (id,))
    return redirect(url_for('keuangan.beban'))


@keuangan_bp.route('/tambah_tambahan', methods=['POST'])
@permission_required('keuangan')
def tambah_tambahan():
    try:
        jenis = str(request.form.get('jenis') or '').strip()
        if jenis not in {'Masuk', 'Keluar'}:
            raise ValueError('Jenis transaksi tidak valid.')

        uraian_select = str(request.form.get('uraian_select') or '').strip()
        uraian_custom = str(request.form.get('uraian_custom') or '').strip()
        uraian = uraian_custom if uraian_select in {'', 'Lainnya'} else uraian_select
        if not uraian:
            raise ValueError('Uraian transaksi wajib diisi.')

        nominal = _positive_int(request.form.get('nominal'), 'Nominal')
        with db_session() as conn:
            conn.execute(
                """INSERT INTO transaksi_tambahan (tanggal, uraian, jenis, nominal)
                   VALUES (%s, %s, %s, %s)""",
                (datetime.now().strftime('%Y-%m-%d'), uraian, jenis, nominal),
            )
    except ValueError as exc:
        return str(exc), 400
    return redirect(url_for('dashboard.dashboard'))


@keuangan_bp.route('/hapus_tambahan/<int:id>', methods=['POST'])
@permission_required('keuangan')
def hapus_tambahan(id):
    with db_session() as conn:
        conn.execute('DELETE FROM transaksi_tambahan WHERE id = %s', (id,))
    return redirect(url_for('dashboard.dashboard') + '#tabel-kas')


@keuangan_bp.route('/bayar/<int:id>')
@permission_required('pembayaran')
def portal_pembayaran(id):
    database = get_db()
    unit = database.execute('SELECT * FROM servis WHERE id = %s', (id,)).fetchone()
    if not unit:
        return 'Unit tidak ditemukan', 404

    paid_row = database.execute(
        '''SELECT COALESCE(SUM(
               CASE WHEN status IN ('Ditolak', 'Dibatalkan', 'Gagal')
                    THEN 0 ELSE nominal END
           ), 0) AS total
           FROM pembayaran WHERE servis_id = %s''',
        (id,),
    ).fetchone()
    try:
        target = _database_money(unit['harga_jual'] or unit['estimasi_biaya'])
        outstanding = max(
            target - _database_money(unit['dp']) - _database_money(paid_row['total']),
            0,
        )
    except ValueError as exc:
        current_app.logger.warning('Nominal pembayaran unit %s tidak valid: %s', id, exc)
        return 'Data nominal unit tidak valid.', 422
    return render_template('pembayaran.html', unit=unit, sisa_tagihan=outstanding)


@keuangan_bp.route('/proses_bayar', methods=['POST'])
@permission_required('pembayaran')
def proses_bayar():
    saved_path = None
    try:
        servis_id = int(request.form.get('servis_id'))
        metode = str(request.form.get('metode') or '').strip()
        if metode not in {'Cash', 'Transfer', 'QRIS'}:
            raise ValueError('Metode pembayaran tidak valid.')
        nominal = _positive_int(request.form.get('nominal'), 'Nominal')
        if nominal <= 0:
            raise ValueError('Nominal pembayaran harus lebih dari nol.')

        upload = request.files.get('bukti_bayar')
        filename = None
        if upload and upload.filename:
            kind = imghdr.what(upload.stream)
            upload.stream.seek(0)
            extension = {'jpeg': 'jpg', 'png': 'png', 'gif': 'gif'}.get(kind)
            if not extension:
                raise ValueError('Bukti pembayaran harus berupa JPG, PNG, atau GIF yang valid.')
            filename = secure_filename(
                f'BUKTI_{servis_id}_{time.time_ns()}.{extension}'
            )

        with db_session() as transaction:
            unit = transaction.execute(
                '''SELECT id, harga_jual, estimasi_biaya, dp
                   FROM servis WHERE id = %s FOR UPDATE''',
                (servis_id,),
            ).fetchone()
            if not unit:
                raise LookupError('Unit tidak ditemukan.')

            paid_row = transaction.execute(
                '''SELECT COALESCE(SUM(
                       CASE WHEN status IN ('Ditolak', 'Dibatalkan', 'Gagal')
                            THEN 0 ELSE nominal END
                   ), 0) AS total
                   FROM pembayaran WHERE servis_id = %s''',
                (servis_id,),
            ).fetchone()
            target = _database_money(unit['harga_jual'] or unit['estimasi_biaya'])
            outstanding = (
                target
                - _database_money(unit['dp'])
                - _database_money(paid_row['total'])
            )
            if target <= 0:
                raise ValueError('Harga atau estimasi unit belum ditetapkan.')
            if outstanding <= 0:
                raise ValueError('Tagihan unit ini sudah lunas atau sedang diproses.')
            if nominal > outstanding:
                raise ValueError(
                    f'Nominal melebihi sisa tagihan Rp {outstanding:,}.'.replace(',', '.')
                )

            if upload and upload.filename:
                saved_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                upload.save(saved_path)

            transaction.execute(
                '''INSERT INTO pembayaran
                       (servis_id, metode, nominal, bukti_bayar, tanggal, status)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (servis_id, metode, nominal, filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Pending'),
            )
    except LookupError as exc:
        if saved_path and os.path.isfile(saved_path):
            os.remove(saved_path)
        return str(exc), 404
    except (TypeError, ValueError) as exc:
        if saved_path and os.path.isfile(saved_path):
            os.remove(saved_path)
        return str(exc), 400
    except Exception as exc:
        if saved_path and os.path.isfile(saved_path):
            os.remove(saved_path)
        print(f'[PAYMENT] Gagal menyimpan pembayaran: {exc}')
        return 'Gagal menyimpan pembayaran.', 500

    return jsonify({
        'status': 'success',
        'message': 'Pembayaran sedang menunggu verifikasi.',
    })
