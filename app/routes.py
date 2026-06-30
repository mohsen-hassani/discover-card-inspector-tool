import json
import os
import uuid
from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, current_app, send_from_directory, abort
)
from werkzeug.utils import secure_filename
from .db import get_db
from .auth import login_required

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@login_required
def gallery():
    db = get_db()
    cards = db.execute(
        'SELECT c.id, c.filename, c.original_filename, c.json_data, c.created_at, u.username'
        ' FROM cards c JOIN users u ON c.user_id = u.id'
        ' ORDER BY c.created_at DESC'
    ).fetchall()
    return render_template('gallery.html', cards=cards)


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        error = None

        if 'image' not in request.files or request.files['image'].filename == '':
            error = 'No image file selected.'

        json_data_raw = request.form.get('json_data', '').strip()
        if not json_data_raw:
            error = 'JSON data is required.'

        if error is None:
            try:
                parsed = json.loads(json_data_raw)
                json_data_clean = json.dumps(parsed)
            except json.JSONDecodeError as e:
                error = f'Invalid JSON: {e}'

        if error is None:
            file = request.files['image']
            if not allowed_file(file.filename):
                error = 'File type not allowed. Use PNG, JPG, GIF, WebP, or BMP.'

        if error is None:
            ext = file.filename.rsplit('.', 1)[1].lower()
            stored_name = f'{uuid.uuid4().hex}.{ext}'
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file.save(os.path.join(upload_folder, stored_name))

            db = get_db()
            from flask import g
            db.execute(
                'INSERT INTO cards (user_id, filename, original_filename, json_data)'
                ' VALUES (?, ?, ?, ?)',
                (g.user['id'], stored_name, secure_filename(file.filename), json_data_clean)
            )
            db.commit()
            flash('Card uploaded successfully.', 'success')
            return redirect(url_for('main.gallery'))

        flash(error, 'error')

    return render_template('upload.html')


@bp.route('/card/<int:card_id>')
@login_required
def card_detail(card_id):
    db = get_db()
    card = db.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
    if card is None:
        abort(404)

    all_cards = db.execute(
        'SELECT id, filename, original_filename FROM cards ORDER BY created_at DESC'
    ).fetchall()

    pretty_json = json.dumps(json.loads(card['json_data']), indent=2)
    return render_template('detail.html', card=card, all_cards=all_cards, pretty_json=pretty_json)


@bp.route('/card/<int:card_id>/delete', methods=['POST'])
@login_required
def delete_card(card_id):
    db = get_db()
    card = db.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
    if card is None:
        abort(404)

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], card['filename'])
    if os.path.exists(filepath):
        os.remove(filepath)

    db.execute('DELETE FROM cards WHERE id = ?', (card_id,))
    db.commit()
    flash('Card deleted.', 'success')
    return redirect(url_for('main.gallery'))


@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
