import logging
import os

from flask import Flask, render_template, render_template_string, session, redirect, url_for, abort
from models import db, Artwork, Gallery, Category
from oauth import configure_oauth, oauth
from utils import login_required
from dotenv import load_dotenv, find_dotenv

# override=True: sovrascrive sempre le env vars con i valori del .env
load_dotenv(find_dotenv(), override=True)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


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
        "pool_recycle": 280,   # ricicla connessioni ogni ~5min (evita connessioni stantie)
        "pool_pre_ping": True, # verifica connessione prima di usarla dal pool
    }
    return db_uri, engine_opts


def _check_connectivity(app):
    """Verifica la connettività verso Turso e Cloudinary al boot e logga l'esito."""
    # ── Turso ──────────────────────────────────────────────────────────────────
    def _turso_ping():
        with app.app_context():
            return db.session.execute(db.text("SELECT 1")).scalar()

    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FT
        with ThreadPoolExecutor(max_workers=1) as ex:
            count = ex.submit(_turso_ping).result(timeout=10)
        logger.info("✅ Turso: connessione OK (SELECT 1 = %s)", count)
    except FT:
        logger.error("❌ Turso: timeout dopo 10s — il database non risponde")
    except Exception as exc:
        logger.error("❌ Turso: errore di connessione — %s", exc)

    # ── Cloudinary ─────────────────────────────────────────────────────────────
    cloudinary_url = os.environ.get("CLOUDINARY_URL", "")
    if not cloudinary_url:
        logger.warning("⚠️  Cloudinary: CLOUDINARY_URL non configurato")
    else:
        try:
            import cloudinary
            import cloudinary.api
            cloudinary.config(cloudinary_url=cloudinary_url)
            result = cloudinary.api.ping()
            logger.info("✅ Cloudinary: connessione OK (status=%s)", result.get("status"))
        except Exception as exc:
            logger.error("❌ Cloudinary: errore di connessione — %s", exc)



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

    # ── Configurazione sessione per OAuth2 ────────────────────────────────────
    # SameSite=Lax è essenziale: senza di esso il browser non invia il cookie
    # di sessione al ritorno dal redirect Google, causando MismatchingStateError.
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_PATH", "/")
    app.config.setdefault("SESSION_PERMANENT", True)
    app.config.setdefault("PERMANENT_SESSION_LIFETIME", 604800)  # 7 giorni
    # In produzione (HTTPS) il cookie deve essere Secure; disabilitabile in locale
    # impostando SESSION_COOKIE_SECURE=false nel .env
    secure = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() != "false"
    app.config.setdefault("SESSION_COOKIE_SECURE", secure)
    # ─────────────────────────────────────────────────────────────────────────

    with app.app_context():
        db.create_all()

    _check_connectivity(app)

    # ── Register blueprints ────────────────────────────────────────────────────
    from artworks_bp import artworks_bp
    from gallery_bp import gallery_bp
    from sync_bp import sync_bp

    app.register_blueprint(artworks_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(sync_bp)

    # ── Auth routes ───────────────────────────────────────────────────────────
    @app.route("/login")
    def login():
        redirect_uri = url_for("auth_callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    @app.route("/auth/callback")
    def auth_callback():
        from authlib.integrations.base_client.errors import MismatchingStateError

        try:
            token = oauth.google.authorize_access_token()
        except MismatchingStateError:
            # La sessione è scaduta o il cookie non è stato inviato durante il redirect OAuth.
            # Reindirizza al login invece di mostrare un 500.
            return redirect(url_for("login"))
        except Exception:
            return redirect(url_for("login"))

        user_info = token.get("userinfo")
        allowed_email = os.environ.get("ALLOWED_EMAIL", "")
        if not user_info or user_info.get("email") != allowed_email:
            abort(403)
        session.permanent = True
        session["user"] = {
            "email": user_info["email"],
            "name": user_info.get("name", ""),
        }
        return redirect(url_for("home"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    # ── Route placeholder ─────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template_string("""
        <!doctype html>
        <html lang="it">
        <head><meta charset="utf-8"><title>PyArtist Backoffice</title></head>
        <body style="font-family:sans-serif;padding:2rem;background:#FCFCFC;color:#1A1A1A">
          <h1 style="color:#7A9EB1">PyArtist Backoffice</h1>
          <a href="/login">Login con Google</a>
        </body>
        </html>
        """)

    @app.route("/home")
    @login_required
    def home():
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

        def _query_stats():
            return (
                Artwork.query.count(),
                Artwork.query.filter_by(is_published=True).count(),
                Gallery.query.count(),
                Category.query.count(),
            )

        artwork_count = published_count = gallery_count = category_count = 0
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                artwork_count, published_count, gallery_count, category_count = (
                    ex.submit(_query_stats).result(timeout=8)
                )
        except (FuturesTimeout, Exception):
            pass  # mostra la home con contatori a 0 se Turso non risponde

        return render_template(
            "home.html",
            artwork_count=artwork_count,
            published_count=published_count,
            gallery_count=gallery_count,
            category_count=category_count,
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
