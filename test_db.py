"""
test_db.py — Verifica la connessione a Turso e il modello Artwork.
Esegui con: python test_db.py  (dalla root del progetto, con venv attivo)
"""

import sys
import os

# Aggiungi backoffice/ al path così i moduli si importano senza prefisso pacchetto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backoffice"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "backoffice", ".env"))

from app import app
from models import db, Artwork


def run():
    with app.app_context():
        # 1. Crea tabelle
        db.create_all()
        print("✓ db.create_all() completato")

        # 2. Inserisce un record di prova
        test_art = Artwork(
            title="Test Opera",
            category="Test",
            year="2024",
            technique="Acquerello su carta",
            image_path="/img/art/test.jpg",
            thumb_path="/img/art/thumb_test.jpg",
            is_published=False,
            position=999,
        )
        db.session.add(test_art)
        db.session.commit()
        print(f"✓ Artwork inserito  → id={test_art.id}")

        # 3. Recupera il record
        fetched = db.session.get(Artwork, test_art.id)
        assert fetched is not None
        assert fetched.title == "Test Opera"
        print(f"✓ Artwork recuperato → title='{fetched.title}', category='{fetched.category}'")

        # 4. Cleanup
        db.session.delete(fetched)
        db.session.commit()
        print("✓ Record di test rimosso")

        print("\n✅ Tutti i test superati — connessione Turso + modello Artwork OK")


if __name__ == "__main__":
    run()
