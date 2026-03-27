---
id: TSK-1
title: Inizializzare struttura repository e moduli
status: In Progress
assignee: []
created_date: '2026-03-27 13:23'
updated_date: '2026-03-27 13:26'
labels:
  - fase-1
  - setup
milestone: Fase 1 - Setup Progetto
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Creare la struttura di cartelle e file base del progetto come definita nelle SPECS.md sezione 6.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Esiste la cartella /website con sottocartelle css/, js/, content/, data/
- [ ] #2 Esiste la cartella /backoffice con file placeholder: app.py, models.py, oauth.py, sync_engine.py
- [ ] #3 Esiste la cartella /backoffice/templates/ e /backoffice/static/
- [ ] #4 Esiste il file .env.example con le variabili FTP_HOST, TURSO_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY
- [ ] #5 Esiste requirements.txt con le dipendenze: flask, flask-sqlalchemy, authlib, pillow, libsql-client o equivalente
- [ ] #6 Esiste README.md con descrizione del progetto
<!-- AC:END -->
