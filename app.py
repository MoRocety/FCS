"""Flask entry point; compatible with app:app and PythonAnywhere."""

import os
from pathlib import Path
import secrets
import tempfile
import click
from werkzeug.security import generate_password_hash
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


def create_app(test_config=None):
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        DATABASE=os.getenv(
            "FCS_DATABASE", str(Path(app.instance_path) / "fcs.sqlite3")
        ),
        SESSION_COOKIE_NAME=os.getenv("FCS_COOKIE_NAME", "fcs_session"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("FCS_SECURE_COOKIES") == "1",
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"]:
        if app.config.get("TESTING"):
            app.config["SECRET_KEY"] = secrets.token_hex(32)
        else:
            secret_file = Path(app.instance_path) / ".session-secret"
            secret_file.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", dir=secret_file.parent, delete=False
            ) as stream:
                stream.write(secrets.token_hex(32))
                temporary = Path(stream.name)
            temporary.chmod(0o600)
            try:
                os.link(temporary, secret_file)
            except FileExistsError:
                pass
            finally:
                temporary.unlink(missing_ok=True)
            app.config["SECRET_KEY"] = secret_file.read_text().strip()
    from fcs.database import Database
    from fcs.identity import identity

    app.extensions["database"] = Database(
        ":memory:"
        if app.config.get("TESTING") and not (test_config or {}).get("DATABASE")
        else app.config["DATABASE"]
    )
    app.config["DUMMY_PASSWORD_HASH"] = generate_password_hash(secrets.token_hex(16))
    app.register_blueprint(identity)

    @app.cli.command("promote-user")
    @click.argument("username")
    def promote_user(username):
        """Grant local moderation permissions to an existing account."""
        with app.extensions["database"].connect() as connection:
            cursor = connection.execute(
                "UPDATE users SET role='moderator' WHERE username=?",
                (username.lower(),),
            )
            if not cursor.rowcount:
                raise click.ClickException("Account not found")
        click.echo("Moderator role granted")

    from fcs.catalog import CatalogRepository
    from fcs.api import api
    from views import my_blueprint
    from fcs.platform import platform
    from fcs.community import community_api
    from fcs.library import library_api
    from fcs.availability import availability_api

    app.extensions["catalog"] = CatalogRepository()
    app.register_blueprint(api)
    app.register_blueprint(platform)
    app.register_blueprint(community_api)
    app.register_blueprint(library_api)
    app.register_blueprint(availability_api)

    @app.errorhandler(HTTPException)
    def http_error(error):
        if request.path.startswith("/api/"):
            return jsonify(error=error.description), error.code
        return error

    app.register_blueprint(my_blueprint)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )
