---
id: TSK-11
title: Implementare generazione gallery.json e pacchetto di export
status: To Do
assignee: []
created_date: '2026-03-27 13:24'
labels:
  - fase-3
  - backoffice
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare in gallery_builder.py la funzione generate_json() che costruisce il file gallery.json a partire dalla configurazione Gallery e dalla selezione GalleryItem nel database. Il JSON è strutturato per categorie (come da SPECS §4). Il modulo gestisce due modalità di export:

- **Opzione A – Download ZIP**: genera un archivio .zip contenente gallery.json + cartelle {categoria}/ con le relative immagini (scaricate da Google Drive).
- **Opzione B – Sync FTP**: carica gallery.json e i file immagine direttamente sul server FTP rispettando la struttura /img/art/{categoria}/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 generate_json() legge la Gallery selezionata e i GalleryItem associati, ordinati per categoria e posizione
- [ ] #2 Output JSON conforme allo schema definito in SPECS §4: oggetto con "gallery_name" e array "categories" ciascuno con i propri "items"
- [ ] #3 Opzione A: build_zip() scarica da Google Drive i file immagine (web e thumb) per le opere selezionate e li impacchetta con gallery.json in un archivio .zip scaricabile dalla dashboard
- [ ] #4 La struttura interna dello ZIP rispetta /img/art/{categoria}/{titolo-id}.jpg e /img/art/{categoria}/thumb_{titolo-id}.jpg
- [ ] #5 Opzione B: il modulo ftp_sync (TSK-12) viene invocato con la lista dei file da caricare e il gallery.json generato
- [ ] #6 La funzione viene invocata dalla dashboard tramite i pulsanti "Scarica ZIP" e "Pubblica via FTP"
- [ ] #7 In caso di errore (file Drive non trovato, FTP irraggiungibile) viene restituito un messaggio di errore chiaro
<!-- AC:END -->
