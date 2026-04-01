---
id: TSK-16
title: Gestire il nome del file JSON per ogni Gallery
status: To Do
assignee: []
created_date: '2026-04-01 13:20'
labels:
  - fase-3
  - backoffice
  - gallery
  - ftp
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: medium
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ogni Gallery deve poter generare un file JSON con nome personalizzabile
(es. `gallery-principale.json`, `gallery-sculture.json`).
Il nome del file è definito dall'utente nella UI del backoffice (campo `json_filename`
nella Gallery) e viene usato sia per il salvataggio locale che per il percorso FTP
al momento della pubblicazione.

Attualmente il percorso è fisso (`website/data/gallery.json` in locale,
`FTP_GALLERY_JSON_PATH` via FTP). Con questa modifica ogni Gallery ha il proprio
file, rendendo possibile la gestione di gallerie multiple sul sito.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Aggiungere la colonna `json_filename` (TEXT, NOT NULL, default `gallery.json`) alla tabella `gallery` su Turso
- [ ] #2 Il form di creazione e modifica Gallery include il campo "Nome file JSON" (es. `gallery.json`); validare che termini con `.json` e che sia unico tra le Gallery
- [ ] #3 `gallery_builder.generate_gallery_json(gallery)` usa `gallery.json_filename` per determinare il percorso di output locale (`website/data/{json_filename}`)
- [ ] #4 `sync_bp.ftp_publish()` usa `gallery.json_filename` per costruire il percorso FTP remoto (`{FTP_REMOTE_BASE_PATH}/data/{json_filename}`) invece del valore fisso `FTP_GALLERY_JSON_PATH`
- [ ] #5 La variabile d'ambiente `FTP_GALLERY_JSON_PATH` rimane come fallback per compatibilità, ma viene ignorata se `gallery.json_filename` è valorizzato
- [ ] #6 Aggiornare `turso_db.py` (colonne `_GAL_COLS`, `gallery_create`, `gallery_update`) per includere `json_filename`
<!-- AC:END -->
