---
id: TSK-12
title: Implementare modulo FTP sync per deploy automatico
status: To Do
assignee: []
created_date: '2026-03-27 13:25'
labels:
  - fase-3
  - backoffice
  - ftp
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare il modulo FTP sync in sync_engine.py per il caricamento di immagini (scaricate da Google Drive), gallery.json e file .md sul server di hosting tramite FTP/FTPS. Le immagini vengono organizzate in sotto-cartelle per categoria (/img/art/{categoria}/). Tutte le credenziali e i percorsi sono configurabili tramite variabili d'ambiente.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ftp_sync() si connette al server FTP tramite le variabili d'ambiente: FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD, FTP_USE_TLS
- [ ] #2 Crea automaticamente le sotto-cartelle per categoria in FTP_IMAGES_PATH/{categoria}/ se non esistono
- [ ] #3 Carica le immagini ottimizzate e le thumbnail nella struttura FTP_IMAGES_PATH/{categoria}/
- [ ] #4 Carica il file gallery.json nel percorso FTP_GALLERY_JSON_PATH
- [ ] #5 Carica eventuali file .md modificati nella cartella /content/ del server
- [ ] #6 Supporto FTPS (TLS) attivabile tramite FTP_USE_TLS=true
- [ ] #7 Log dell'operazione di sync con esito (successo/errore per file)
- [ ] #8 I file immagine da caricare vengono forniti come stream scaricati da Google Drive tramite drive.py (nessun file temporaneo locale obbligatorio)
<!-- AC:END -->
