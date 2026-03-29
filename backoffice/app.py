import os
from flask import Flask, render_template_string
from models import db
from oauth import configure_oauth
from dotenv import load_dotenv

load_dotenv()


def _turso_uri() -> str:
    """Costruisce l'URI SQLAlchemy per Turso da TURSO_URL + TURSO_AUTH_TOKEN."""
    url = os.environ.get("TURSO_URL", "")
    token = os.environ.get("TURSO_AUTH_TOKEN", "")
    if not url or not token:
        raise RuntimeError(
            "Variabili d'ambiente mancanti: TURSO_URL e TURSO_AUTH_TOKEN sono obbligatorie."
        )
    # Converte libsql://host → libsql+https://host?authToken=TOKEN
    host = url.replace("libsql://", "")
    return f"libsql+https://{host}?authToken={token}"


def create_app():
    app = Flask(__name__)

    # Legge FLASK_* da .env (es. FLASK_SECRET_KEY)
    app.config.from_prefixed_env()

    # ── Database: Turso via sqlalchemy-libsql (HTTP, no Rust) ─────────────────
    app.config["SQLALCHEMY_DATABASE_URI"] = _turso_uri()
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
