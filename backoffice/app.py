from flask import Flask
from models import db
from oauth import configure_oauth

app = Flask(__name__)
app.config.from_prefixed_env()  # legge FLASK_* da .env

db.init_app(app)
configure_oauth(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
