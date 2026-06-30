import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from .db import get_db
from .auth import login_required

bp = Blueprint('tags', __name__, url_prefix='/tags')

ALLOWED_COLORS = ('indigo', 'green', 'yellow', 'red', 'purple', 'blue', 'orange')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def list_tags():
    db = get_db()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        color = request.form.get('color', 'indigo')
        error = None
        if not name:
            error = 'Tag name is required.'
        elif color not in ALLOWED_COLORS:
            error = 'Invalid color.'
        if error is None:
            try:
                db.execute('INSERT INTO tags (name, color) VALUES (?, ?)', (name, color))
                db.commit()
                flash(f'Tag "{name}" created.', 'success')
            except sqlite3.IntegrityError:
                flash(f'A tag named "{name}" already exists.', 'error')
        else:
            flash(error, 'error')
        return redirect(url_for('tags.list_tags'))

    edit_id = request.args.get('edit', type=int)
    tags = db.execute(
        'SELECT t.id, t.name, t.color, COUNT(ct.card_id) AS card_count'
        ' FROM tags t LEFT JOIN card_tags ct ON t.id = ct.tag_id'
        ' GROUP BY t.id ORDER BY t.name'
    ).fetchall()
    edit_tag = db.execute('SELECT * FROM tags WHERE id = ?', (edit_id,)).fetchone() if edit_id else None
    return render_template('tags.html', tags=tags, edit_tag=edit_tag, allowed_colors=ALLOWED_COLORS)


@bp.route('/<int:tag_id>/edit', methods=['POST'])
@login_required
def edit_tag(tag_id):
    db = get_db()
    name = request.form.get('name', '').strip()
    color = request.form.get('color', 'indigo')
    error = None
    if not name:
        error = 'Tag name is required.'
    elif color not in ALLOWED_COLORS:
        error = 'Invalid color.'
    if error is None:
        try:
            db.execute('UPDATE tags SET name = ?, color = ? WHERE id = ?', (name, color, tag_id))
            db.commit()
            flash('Tag updated.', 'success')
        except sqlite3.IntegrityError:
            flash(f'A tag named "{name}" already exists.', 'error')
    else:
        flash(error, 'error')
    return redirect(url_for('tags.list_tags'))


@bp.route('/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    db = get_db()
    tag = db.execute('SELECT name FROM tags WHERE id = ?', (tag_id,)).fetchone()
    if tag:
        db.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
        db.commit()
        flash(f'Tag "{tag["name"]}" deleted.', 'success')
    return redirect(url_for('tags.list_tags'))
