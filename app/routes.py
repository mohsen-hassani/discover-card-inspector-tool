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
    tag_id = request.args.get('tag_id', type=int)
    all_tags = db.execute('SELECT * FROM tags ORDER BY name').fetchall()

    if tag_id:
        cards = db.execute(
            'SELECT c.id, c.filename, c.original_filename, c.json_data, c.created_at, u.username'
            ' FROM cards c'
            ' JOIN users u ON c.user_id = u.id'
            ' JOIN card_tags ct ON c.id = ct.card_id'
            ' WHERE ct.tag_id = ?'
            ' ORDER BY c.created_at DESC',
            (tag_id,)
        ).fetchall()
    else:
        cards = db.execute(
            'SELECT c.id, c.filename, c.original_filename, c.json_data, c.created_at, u.username'
            ' FROM cards c JOIN users u ON c.user_id = u.id'
            ' ORDER BY c.created_at DESC'
        ).fetchall()

    card_ids = [c['id'] for c in cards]
    card_tags_map = {}
    if card_ids:
        placeholders = ','.join('?' * len(card_ids))
        for row in db.execute(
            f'SELECT ct.card_id, t.id, t.name, t.color'
            f' FROM card_tags ct JOIN tags t ON ct.tag_id = t.id'
            f' WHERE ct.card_id IN ({placeholders}) ORDER BY t.name',
            card_ids
        ).fetchall():
            card_tags_map.setdefault(row['card_id'], []).append(
                {'id': row['id'], 'name': row['name'], 'color': row['color']}
            )

    return render_template('gallery.html', cards=cards, all_tags=all_tags,
                           active_tag_id=tag_id, card_tags_map=card_tags_map)


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

    card_tags = db.execute(
        'SELECT t.id, t.name, t.color FROM tags t'
        ' JOIN card_tags ct ON t.id = ct.tag_id'
        ' WHERE ct.card_id = ? ORDER BY t.name',
        (card_id,)
    ).fetchall()

    pretty_json = json.dumps(json.loads(card['json_data']), indent=2)
    return render_template('detail.html', card=card, all_cards=all_cards,
                           pretty_json=pretty_json, card_tags=card_tags)


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


@bp.route('/card/<int:card_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_card(card_id):
    db = get_db()
    card = db.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
    if card is None:
        abort(404)

    if request.method == 'POST':
        selected_ids = request.form.getlist('tag_ids', type=int)
        db.execute('DELETE FROM card_tags WHERE card_id = ?', (card_id,))
        for tid in selected_ids:
            db.execute('INSERT OR IGNORE INTO card_tags (card_id, tag_id) VALUES (?, ?)',
                       (card_id, tid))
        db.commit()
        flash('Tags updated.', 'success')
        return redirect(url_for('main.card_detail', card_id=card_id))

    all_tags = db.execute('SELECT * FROM tags ORDER BY name').fetchall()
    card_tag_ids = {
        row['tag_id'] for row in
        db.execute('SELECT tag_id FROM card_tags WHERE card_id = ?', (card_id,)).fetchall()
    }
    return render_template('card_edit.html', card=card, all_tags=all_tags,
                           card_tag_ids=card_tag_ids)


@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
