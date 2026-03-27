from flask import Flask, render_template_string
from models import db
from oauth import configure_oauth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_prefixed_env()  # reads FLASK_* from .env

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
