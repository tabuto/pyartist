SPECS.md: Minimalist Watercolor Artist Portal
# 1. Project Overview
Il progetto consiste in una piattaforma duale per un artista acquerellista:

Website (Frontend): Sito statico, minimalista e performante che consuma dati da file Markdown e un file JSON.

Backoffice (Control Plane): Webapp in Python per la gestione dei contenuti, ottimizzazione immagini e deploy automatizzato via FTP.

# 2. Tech Stack
A. Website (Module: /website)
Framework: HTML5 / Tailwind CSS (CDN o PostCSS).

Interattività: Alpine.js (per il fetch del JSON e filtraggio gallery).

Content: File .md (pagine statiche) + gallery.json (opere).

Deployment: Hosting statico (es. Netlify, Vercel o semplice Web Server tramite FTP).

B. Backoffice (Module: /backoffice)
Language: Python 3.10+ con venv.

Framework: Flask + Flask-SQLAlchemy.

Database: Turso (libSQL/SQLite) per la persistenza dei metadati.

Auth: Google OAuth2 (tramite Authlib).

Image Engine: Pillow (ottimizzazione e generazione thumbnail).

Deployment: Render.com.

# 3. System Architecture & Workflow
Input: L'artista accede al Backoffice tramite Google Login.

Management: Carica un'immagine, inserisce titolo, categoria e descrizione.

Processing: Il sistema salva i dati su Turso, crea una versione "web-optimized" e una "thumbnail".

Generation: Il sistema rigenera il file gallery.json basandosi sul database.

Sync (FTP): Il sistema carica via FTP:

Nuove immagini e miniature.

File gallery.json aggiornato.

Eventuali file .md modificati.

# 4. Data Models & Schema
Database (Turso/SQLite)
Table Artwork:

id: Integer (PK)

title: String

category: String (es: Paesaggi, Ritratti, Astratti)

year: String

technique: String (default: "Acquerello su carta")

image_path: String (percorso pubblico)

thumb_path: String (percorso miniatura)

is_published: Boolean

position: Integer (per ordinamento manuale)

Output (gallery.json)
JSON
[
  {
    "title": "Tramonto",
    "category": "Paesaggi",
    "image": "/img/art/tramonto.jpg",
    "thumb": "/img/art/thumb_tramonto.jpg",
    "details": "2023, Acquerello su carta 300g"
  }
]
# 5. UI/UX Design Specs (Minimalist)
Palette: - Sfondo: #FCFCFC (off-white, richiama la carta da acquerello).

Testo: #1A1A1A (antracite scuro, non nero puro).

Accento: #7A9EB1 (un blu polvere trasparente).

Tipografia: - Titoli: Serif (es: Playfair Display).

Body: Sans-serif (es: Inter o Montserrat).

Layout: - Spaziature ampie (large padding/margins).

Galleria: Grid responsiva (1 col mobile, 2 col tablet, 3 col desktop).

Immagini con object-fit: contain per non tagliare le opere.

# 6. Repository Structure
Plaintext
/
├── website/                # File statici da caricare sul server pubblico
│   ├── index.html          # Homepage + Logica Alpine.js
│   ├── css/                # Tailwind config / styles.css
│   ├── js/                 # Script leggeri (marked.js per MD)
│   ├── content/            # File .md (chi-sono.md, contatti.md)
│   └── data/               # gallery.json (generato dal backoffice)
├── backoffice/             # Webapp Flask
│   ├── app.py              # Entry point
│   ├── models.py           # SQLAlchemy models
│   ├── oauth.py            # Configurazione Google Login
│   ├── sync_engine.py      # Logica FTP e Image processing
│   ├── templates/          # Dashboard Jinja2
│   └── static/             # Assets del backoffice
├── .env.example            # Variabili d'ambiente (FTP_HOST, TURSO_URL, etc.)
├── requirements.txt
└── README.md
# 7. Implementation Roadmap (Tasks)
Phase 1: Backoffice Core
[ ] Setup repo e venv.

[ ] Implementazione Google OAuth2.

[ ] Configurazione SQLAlchemy con Turso.

[ ] Creazione form di upload (Titolo, Cat, File).

Phase 2: Processing & Sync
[ ] Funzione optimize_image: ridimensiona a max 1920px, crea thumb 400px.

[ ] Funzione generate_json: esporta la tabella Artwork in gallery.json.

[ ] Modulo ftp_sync: connessione e upload file al server target.

# Phase 3: Website Development
[ ] Struttura HTML5 con Tailwind.

[ ] Fetch dinamico di gallery.json tramite Alpine.js.

[ ] Sistema di filtraggio per categoria (Tabs o Dropdown).

[ ] Parser Markdown lato client per le sezioni testuali.

# Phase 4: Deployment
[ ] Configurazione Gunicorn per Render.com.

[ ] Setup variabili d'ambiente (Secret Key, Turso Token, FTP Credentials).

# 8. Specifiche Tecniche Immagini
Max Items: 100 opere.

Formato Output: JPEG (qualità 85) o WebP.

Naming Convention: titolo-opera-id.jpg.

Next Step consigliato: > Vuoi che ti generi il codice per backoffice/sync_engine.py (la parte che gestisce Pillow + FTP) o preferisci partire dallo scheletro della dashboard Flask?