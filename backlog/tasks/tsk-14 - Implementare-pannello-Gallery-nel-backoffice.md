---
id: TSK-14
title: Implementare pannello Gallery nel backoffice
status: To Do
assignee: []
created_date: '2026-03-29 09:46'
labels:
  - fase-3
  - backoffice
  - gallery
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare il pannello Gallery nel backoffice Flask per la gestione completa delle configurazioni di galleria: CRUD delle categorie (tabella Category), creazione e modifica di Gallery con selezione/deselezione delle opere associate (GalleryItem) e riordinamento drag-and-drop. Il pannello include anche i controlli per generare il gallery.json e scegliere la modalità di export (ZIP o FTP).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Sezione Categorie: lista, creazione, modifica ed eliminazione di Category (nome, slug autogenerato, posizione); template in templates/gallery/categories.html
- [ ] #2 Sezione Gallerie: lista delle Gallery con nome, descrizione e data aggiornamento; template in templates/gallery/index.html
- [ ] #3 Pagina di dettaglio Gallery: mostra tutte le opere disponibili con checkbox di selezione e le opere già selezionate (GalleryItem) con posizione modificabile via drag-and-drop
- [ ] #4 Il salvataggio della selezione aggiorna la tabella GalleryItem mantenendo l'ordinamento definito dall'utente
- [ ] #5 Pulsante "Anteprima JSON" mostra il gallery.json generato dalla selezione corrente senza salvarlo
- [ ] #6 Pulsante "Scarica ZIP" (Opzione A) invoca gallery_builder.build_zip() e restituisce il file .zip al browser
- [ ] #7 Pulsante "Pubblica via FTP" (Opzione B) invoca gallery_builder.generate_json() + ftp_sync() e mostra il log di esito nella pagina
- [ ] #8 Tutti i template sono in templates/gallery/ e coerenti con lo stile minimalista della dashboard
<!-- AC:END -->
