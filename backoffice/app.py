import os
from flask import Flask, render_template_string
from models import db
from oauth import configure_oauth
from dotenv import load_dotenv, find_dotenv

# override=True: sovrascrive sempre le env vars con i valori del .env
load_dotenv(find_dotenv(), override=True)


def _turso_engine_config():
    """Restituisce (uri, engine_options) per Turso.
    auth_token viene passato come connect_arg — SQLAlchemy lo inietta come
    keyword arg direttamente a libsql_experimental.connect(), bypssando il bug
    del dialetto sqlalchemy-libsql con l'URL encoding dei valori tuple."""
    from sqlalchemy.engine import URL

    url = os.environ.get("TURSO_URL", "")
    token = os.environ.get("TURSO_AUTH_TOKEN", "")
    if not url or not token:
        raise RuntimeError(
            "Variabili mancanti: TURSO_URL e TURSO_AUTH_TOKEN sono obbligatorie."
        )
    host = url.replace("libsql://", "")

    db_uri = URL.create(
        drivername="sqlite+libsql",
        host=host,
        query={"secure": "true"},   # authToken NON nel URL: evita bug urlencode tuple
    )
    engine_opts = {
        "connect_args": {"auth_token": token},
    }
    return db_uri, engine_opts


def create_app():
    app = Flask(__name__)

    # Legge FLASK_* da .env (es. FLASK_SECRET_KEY)
    app.config.from_prefixed_env()

    # ── Database: Turso via sqlalchemy-libsql ────────────────────────────────
    db_uri, engine_opts = _turso_engine_config()
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_opts
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
