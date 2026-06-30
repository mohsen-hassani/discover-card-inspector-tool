import sqlite3
import os
import click
from flask import g, current_app


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema) as f:
        db.executescript(f.read())
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
