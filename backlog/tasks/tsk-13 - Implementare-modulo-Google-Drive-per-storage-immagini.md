---
id: TSK-13
title: Implementare modulo Google Drive per storage immagini
status: To Do
assignee: []
created_date: '2026-03-29 09:46'
labels:
  - fase-3
  - backoffice
  - drive
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare il modulo drive.py che gestisce l'integrazione con Google Drive API v3 tramite Service Account. Il modulo gestisce autenticazione, creazione cartelle per categoria, upload e download dei file immagine (originali, ottimizzati, thumbnail) nella struttura definita in SPECS §8. Le credenziali sono configurabili tramite variabili d'ambiente.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 drive.py si autentica con Google Drive API v3 tramite Service Account (file JSON referenziato da GOOGLE_SERVICE_ACCOUNT_FILE)
- [ ] #2 get_or_create_folder() crea la struttura di cartelle pyartist/originals/{cat}/, pyartist/web/{cat}/, pyartist/thumbs/{cat}/ sotto la cartella root GOOGLE_DRIVE_ROOT_FOLDER_ID
- [ ] #3 upload_file() carica un file (da path locale o stream) in una cartella Drive specificata e restituisce il drive_file_id
- [ ] #4 download_file() scarica un file da Drive tramite drive_file_id e restituisce uno stream (BytesIO), senza necessità di salvataggio su disco
- [ ] #5 delete_file() elimina un file da Drive tramite drive_file_id
- [ ] #6 Le operazioni gestiscono errori di autenticazione e quota con messaggi chiari
- [ ] #7 Il modulo è coperto da test unitari con mock delle chiamate API Drive
<!-- AC:END -->
