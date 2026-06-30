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

    @app.template_filter('tag_classes')
    def tag_classes_filter(color):
        classes = {
            'indigo': 'bg-indigo-900 text-indigo-300 border-indigo-700',
            'green':  'bg-green-900 text-green-300 border-green-700',
            'yellow': 'bg-yellow-900 text-yellow-300 border-yellow-700',
            'red':    'bg-red-900 text-red-300 border-red-700',
            'purple': 'bg-purple-900 text-purple-300 border-purple-700',
            'blue':   'bg-blue-900 text-blue-300 border-blue-700',
            'orange': 'bg-orange-900 text-orange-300 border-orange-700',
        }
        return classes.get(color, classes['indigo'])

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

    from . import auth, routes, tags
    app.register_blueprint(auth.bp)
    app.register_blueprint(routes.bp)
    app.register_blueprint(tags.bp)

    return app
