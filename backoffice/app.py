import os
from flask import Flask, render_template_string
from models import db
from oauth import configure_oauth
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Legge FLASK_* da .env (es. FLASK_SECRET_KEY, FLASK_SQLALCHEMY_DATABASE_URI)
    app.config.from_prefixed_env()

    # ── Turso / libSQL ────────────────────────────────────────────────────────
    turso_url = os.environ.get("TURSO_URL", "")
    turso_token = os.environ.get("TURSO_AUTH_TOKEN", "")

    if turso_url and turso_token:
        try:
            import libsql_experimental as libsql
            from sqlalchemy.pool import StaticPool

            class _LibSQLWrapper:
                """Adatta la connessione libsql all'interfaccia sqlite3 attesa da SQLAlchemy."""

                def __init__(self, conn):
                    self._conn = conn

                def __getattr__(self, item):
                    return getattr(self._conn, item)

                def create_function(self, *_args, **_kwargs):
                    pass  # non supportato da libsql

                def cursor(self):
                    return self._conn.cursor()

                def commit(self):
                    return self._conn.commit()

                def rollback(self):
                    return self._conn.rollback()

                def execute(self, *args, **kwargs):
                    return self._conn.execute(*args, **kwargs)

                def close(self):
                    pass  # connessione singleton — non chiudere

            _raw_conn = libsql.connect(
                "pyartist.db", sync_url=turso_url, auth_token=turso_token
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
                """Propaga le scritture locali su Turso al termine di ogni request."""
                try:
                    _raw_conn.sync()
                except Exception:
                    pass

        except ImportError:
            app.logger.warning(
                "libsql_experimental non disponibile: utilizzo SQLite locale."
            )
    # ─────────────────────────────────────────────────────────────────────────

    db.init_app(app)
    configure_oauth(app)

    with app.app_context():
        db.create_all()

    # ── Route placeholder ─────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template_string("""
        <!doctype html>
        <html lang="en">
        <head><meta charset="utf-8"><title>PyArtist Backoffice</title></head>
        <body style="font-family:sans-serif;padding:2rem;background:#FCFCFC;color:#1A1A1A">
          <h1 style="color:#7A9EB1">PyArtist Backoffice</h1>
          <p>Placeholder — autenticazione e dashboard in arrivo (TSK-8, TSK-9).</p>
          <a href="/login">Login with Google</a>
        </body>
        </html>
        """)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
