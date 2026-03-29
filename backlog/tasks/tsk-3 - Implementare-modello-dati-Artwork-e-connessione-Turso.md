---
id: TSK-3
title: Implementare modello dati Artwork e connessione Turso
status: To Do
assignee: []
created_date: '2026-03-27 13:23'
labels:
  - fase-1
  - database
milestone: Fase 1 - Setup Progetto
dependencies: []
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare i modelli SQLAlchemy (Artwork, Category, Gallery, GalleryItem) e configurare la connessione al database Turso (libSQL/SQLite compatibile) tramite variabili d'ambiente. Il modello Artwork include i riferimenti ai file su Google Drive.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 models.py contiene la classe Artwork con tutti i campi: id, title, category, year, technique, image_path, thumb_path, drive_file_id, drive_thumb_id, is_published, position
- [ ] #2 models.py contiene la classe Category con i campi: id, name, slug, position
- [ ] #3 models.py contiene la classe Gallery con i campi: id, name, description, created_at, updated_at
- [ ] #4 models.py contiene la classe GalleryItem con i campi: id, gallery_id (FK), artwork_id (FK), position
- [ ] #5 La connessione a Turso (libSQL/SQLite) è configurabile tramite variabili d'ambiente TURSO_DATABASE_URL e TURSO_AUTH_TOKEN
- [ ] #6 Le tabelle vengono create correttamente con db.create_all()
- [ ] #7 Funzione di test che inserisce e recupera un record di prova per ciascun modello
<!-- AC:END -->
