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

Storage: Google Drive API v3 (repository cloud delle immagini originali, ottimizzate e thumbnail).

Deployment: Render.com.

# 3. System Architecture & Workflow
Input: L'artista accede al Backoffice tramite Google Login.

Management: Carica un'immagine, inserisce titolo, categoria e descrizione.

Processing: Il sistema salva i dati su Turso, crea una versione "web-optimized" e una "thumbnail"; entrambi i file vengono archiviati su Google Drive in cartelle strutturate per categoria.

Storage (Google Drive): Le immagini originali, ottimizzate e thumbnail sono conservate su un Google Drive dedicato, organizzato in sotto-cartelle per categoria. Il campo `drive_file_id` nel database permette di recuperare o aggiornare ogni asset.

Generation: Il sistema rigenera il file gallery.json basandosi sul database e sulla selezione effettuata nella tabella Gallery.

Sync (FTP): Il sistema carica via FTP:

Nuove immagini e miniature (scaricate da Drive o streamate direttamente).

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

image_path: String (percorso pubblico sul sito)

thumb_path: String (percorso miniatura sul sito)

drive_file_id: String (ID file immagine ottimizzata su Google Drive)

drive_thumb_id: String (ID file thumbnail su Google Drive)

is_published: Boolean

position: Integer (per ordinamento manuale)

Table Category:

id: Integer (PK)

name: String (nome univoco della categoria, es: "Paesaggi")

slug: String (slug URL-friendly, es: "paesaggi")

position: Integer (per ordinamento manuale)

Table Gallery:

id: Integer (PK)

name: String (nome della configurazione galleria, es: "Galleria Principale")

description: String (opzionale)

created_at: DateTime

updated_at: DateTime

Table GalleryItem:

id: Integer (PK)

gallery_id: Integer (FK → Gallery.id)

artwork_id: Integer (FK → Artwork.id)

position: Integer (ordinamento nella galleria)

Output (gallery.json)
La struttura del file riflette le categorie e le opere selezionate nella Gallery:
JSON
{
  "gallery_name": "Galleria Principale",
  "categories": [
    {
      "name": "Paesaggi",
      "slug": "paesaggi",
      "items": [
        {
          "title": "Tramonto",
          "category": "paesaggi",
          "image": "/img/art/paesaggi/tramonto.jpg",
          "thumb": "/img/art/paesaggi/thumb_tramonto.jpg",
          "details": "2023, Acquerello su carta 300g"
        }
      ]
    }
  ]
}
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
│   ├── models.py           # SQLAlchemy models (Artwork, Category, Gallery, GalleryItem)
│   ├── oauth.py            # Configurazione Google Login
│   ├── drive.py            # Modulo Google Drive API (upload/download immagini)
│   ├── sync_engine.py      # Logica FTP e Image processing
│   ├── gallery_builder.py  # Logica selezione opere, generazione gallery.json e pacchetto ZIP
│   ├── templates/          # Dashboard Jinja2
│   │   ├── artworks/       # CRUD opere
│   │   ├── gallery/        # Gestione gallerie e selezione immagini
│   │   └── sync/           # Pannello sync FTP / download ZIP
│   └── static/             # Assets del backoffice
├── .env.example            # Variabili d'ambiente (vedere sezione 9)
├── requirements.txt
└── README.md
# 7. Implementation Roadmap (Tasks)
Phase 1: Backoffice Core
[ ] Setup repo e venv.

[ ] Implementazione Google OAuth2.

[ ] Configurazione SQLAlchemy con Turso.

[ ] Creazione form di upload (Titolo, Cat, File).

[ ] Integrazione Google Drive API: upload immagine originale, ottimizzata e thumbnail nelle cartelle di categoria; salvataggio drive_file_id e drive_thumb_id nel DB.

Phase 2: Processing & Sync
[ ] Funzione optimize_image: ridimensiona a max 1920px, crea thumb 400px.

[ ] Modulo drive.py: autenticazione Service Account, upload/download file, gestione cartelle per categoria.

[ ] Funzione generate_json: esporta la selezione Gallery in gallery.json strutturato per categorie.

[ ] Pannello Gallery (backoffice): CRUD categorie, selezione/deselezione opere per gallery, riordinamento drag-and-drop.

[ ] Opzione A – Download ZIP: genera archivio contenente gallery.json + cartelle categoria con i relativi file immagine.

[ ] Opzione B – Sync FTP: scarica immagini da Drive e carica su FTP insieme a gallery.json.

[ ] Modulo ftp_sync: connessione, upload file e struttura directory al server target.

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

Naming Convention: `{slug-categoria}/{titolo-opera-id}.jpg` (sia su Drive che sul server FTP).

Struttura cartelle Drive:
```
My Drive/
└── pyartist/
    ├── originals/
    │   └── {categoria}/   ← file originali ad alta risoluzione
    ├── web/
    │   └── {categoria}/   ← immagini ottimizzate (max 1920px)
    └── thumbs/
        └── {categoria}/   ← miniature (400px)
```

Struttura cartelle sul server FTP / ZIP di export:
```
/img/art/
└── {categoria}/
    ├── {titolo-id}.jpg
    └── thumb_{titolo-id}.jpg
```

# 9. Variabili d'Ambiente (.env.example)
```dotenv
# ── Flask ──────────────────────────────────────────
SECRET_KEY=change-me

# ── Google OAuth2 (login backoffice) ───────────────
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# ── Google Drive API (storage immagini) ────────────
# Percorso al file JSON del Service Account con le credenziali Drive
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service_account.json
# ID della cartella radice "pyartist" su Google Drive
GOOGLE_DRIVE_ROOT_FOLDER_ID=

# ── Turso / libSQL ─────────────────────────────────
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=

# ── FTP (sync website) ─────────────────────────────
FTP_HOST=
FTP_PORT=21
FTP_USER=
FTP_PASSWORD=
# Percorso remoto base dove vengono caricati i file del sito
FTP_REMOTE_BASE_PATH=/public_html
# Sottocartella remota per le immagini delle opere
FTP_IMAGES_PATH=/public_html/img/art
# Percorso remoto del file gallery.json
FTP_GALLERY_JSON_PATH=/public_html/data/gallery.json
# Usare connessione sicura FTPS (true/false)
FTP_USE_TLS=true
```