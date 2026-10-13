"""Flask entry point; compatible with app:app and PythonAnywhere."""
import os
from pathlib import Path
from flask import Flask


def create_app(test_config=None):
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.getenv('SECRET_KEY'), MAX_CONTENT_LENGTH=2 * 1024 * 1024)
    if test_config:
        app.config.update(test_config)
    from fcs.catalog import CatalogRepository
    from fcs.api import api
    from views import my_blueprint
    app.extensions['catalog'] = CatalogRepository()
    app.register_blueprint(api)
    app.register_blueprint(my_blueprint)
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', '5000')), debug=os.getenv('FLASK_DEBUG') == '1')
