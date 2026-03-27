import os
from flask import Flask, render_template_string
from models import db
from oauth import configure_oauth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_prefixed_env()  # reads FLASK_* from .env

# --- Turso / libSQL engine setup ---
_turso_url = os.environ.get("TURSO_URL", "")
_turso_token = os.environ.get("TURSO_AUTH_TOKEN", "")

if _turso_url and _turso_token:
    import libsql_experimental as libsql
    from sqlalchemy.pool import StaticPool

    class _LibSQLWrapper:
        """Thin wrapper that adds sqlite3-compatible stubs missing from libsql."""

        def __init__(self, conn):
            self._conn = conn

        def __getattr__(self, item):
            return getattr(self._conn, item)

        # SQLAlchemy pysqlite dialect calls this on connect — libsql doesn't support it
        def create_function(self, *_args, **_kwargs):
            pass

        def cursor(self):
            return self._conn.cursor()

        def commit(self):
            return self._conn.commit()

        def rollback(self):
            return self._conn.rollback()

        def execute(self, *args, **kwargs):
            return self._conn.execute(*args, **kwargs)

        def close(self):
            pass  # keep singleton alive

    _raw_conn = libsql.connect(
        "pyartist.db", sync_url=_turso_url, auth_token=_turso_token
    )
    _raw_conn.sync()
    _wrapped = _LibSQLWrapper(_raw_conn)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite+pysqlite://"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "creator": lambda: _wrapped,
        "poolclass": StaticPool,
    }

    @app.teardown_appcontext
    def sync_turso(_exc=None):
        """Push local writes to Turso after each request."""
        try:
            _raw_conn.sync()
        except Exception:
            pass
# ------------------------------------

db.init_app(app)
configure_oauth(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template_string("""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>PyArtist Backoffice</title></head>
    <body style="font-family:sans-serif;padding:2rem;background:#FCFCFC;color:#1A1A1A">
      <h1 style="color:#7A9EB1">PyArtist Backoffice</h1>
      <p>Placeholder — authentication and dashboard coming in TSK-8 and TSK-9.</p>
      <a href="/login">Login with Google</a>
    </body>
    </html>
    """)


if __name__ == "__main__":
    app.run(debug=True)
