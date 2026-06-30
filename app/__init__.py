import json
import os
from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['DATABASE_PATH'] = os.environ.get('DATABASE_PATH', os.path.join(app.instance_path, 'db.sqlite3'))
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(app.instance_path, 'uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)

    from . import db
    db.init_app(app)

    with app.app_context():
        db.init_db()

    from . import auth, routes
    app.register_blueprint(auth.bp)
    app.register_blueprint(routes.bp)

    return app
