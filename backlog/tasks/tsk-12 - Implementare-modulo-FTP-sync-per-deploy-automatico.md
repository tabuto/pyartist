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
Implementare il modulo FTP sync in sync_engine.py per il caricamento automatico di immagini, gallery.json e file .md sul server di hosting tramite FTP.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ftp_sync() si connette al server FTP tramite credenziali da variabili d'ambiente (FTP_HOST, FTP_USER, FTP_PASS, FTP_PATH)
- [ ] #2 Carica le immagini ottimizzate e le thumbnail nella cartella /img/art/ del server
- [ ] #3 Carica il file gallery.json aggiornato nella cartella /data/ del server
- [ ] #4 Carica eventuali file .md modificati nella cartella /content/ del server
- [ ] #5 Log dell'operazione di sync con esito (successo/errore per file)
- [ ] #6 Pulsante 'Pubblica e Sincronizza' nella dashboard attiva il processo completo
<!-- AC:END -->
