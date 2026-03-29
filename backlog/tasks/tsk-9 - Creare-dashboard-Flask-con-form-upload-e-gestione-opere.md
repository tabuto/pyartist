---
id: TSK-9
title: Creare dashboard Flask con form upload e gestione opere
status: To Do
assignee: []
created_date: '2026-03-27 13:24'
labels:
  - fase-3
  - backoffice
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Creare la dashboard Flask con form di upload opere, lista opere, modifica e gestione dello stato di pubblicazione. La dashboard include anche la sezione Galleria per la gestione delle categorie e la selezione delle opere da includere nel gallery.json.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dashboard mostra la lista delle opere con titolo, categoria, stato pubblicazione e posizione
- [ ] #2 Form di upload accetta: titolo, categoria, anno, tecnica, file immagine (JPEG/PNG)
- [ ] #3 Form di modifica opera permette di aggiornare tutti i campi e toggle is_published
- [ ] #4 Funzione di eliminazione opera (con conferma) rimuove il record dal DB
- [ ] #5 Riordinamento manuale della posizione delle opere
- [ ] #6 Sezione Categorie: CRUD completo (nome, slug, posizione) con template dedicato in templates/gallery/
- [ ] #7 Sezione Galleria: creazione/modifica configurazione Gallery con selezione/deselezione delle opere associate (GalleryItem) e riordinamento drag-and-drop
- [ ] #8 Sezione Sync: pannello con pulsante "Scarica ZIP" (Opzione A) e pulsante "Pubblica via FTP" (Opzione B)
- [ ] #9 Template Jinja2 coerente con stile minimalista, organizzati in templates/artworks/, templates/gallery/, templates/sync/
<!-- AC:END -->
