# PyArtist — Minimalist Watercolor Artist Portal

Piattaforma duale per un artista acquerellista:

- **Website** (`/website`): sito statico minimalista che consuma `gallery.json` e file Markdown.
- **Backoffice** (`/backoffice`): webapp Flask per la gestione opere, ottimizzazione immagini e deploy via FTP.

## Stack

| Modulo | Tecnologia |
|---|---|
| Website | HTML5, Tailwind CSS, Alpine.js |
| Backoffice | Python 3.10+, Flask, Flask-SQLAlchemy |
| Database | Turso (libSQL/SQLite) |
| Auth | Google OAuth2 (Authlib) |
| Image Engine | Pillow |
| Deploy | Render.com (backoffice) + FTP (website) |

## Struttura

```
/
├── website/
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── content/        # .md (chi-sono.md, contatti.md)
│   └── data/           # gallery.json (generato dal backoffice)
├── backoffice/
│   ├── app.py
│   ├── models.py
│   ├── oauth.py
│   ├── sync_engine.py
│   ├── templates/
│   └── static/
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Compila .env con le tue credenziali

cd backoffice
flask run
```

## Workflow

1. L'artista accede al backoffice tramite Google Login.
2. Carica un'immagine con titolo, categoria e descrizione.
3. Il sistema ottimizza l'immagine (max 1920px) e genera la thumbnail (400px).
4. Viene rigenerato `website/data/gallery.json`.
5. Il sito viene aggiornato via FTP con immagini e JSON.
