---
id: TSK-15
title: Estendere modello Artwork con nuovi attributi e sezione Configurazione
status: To Do
assignee: []
created_date: '2026-04-01 13:17'
labels:
  - fase-3
  - backoffice
  - artwork
  - configurazione
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Aggiungere al modello Artwork i campi Formato (select), Tecnica (select), Descrizione (text)
e Collezione (select). Le opzioni disponibili per i campi select (Formato, Tecnica, Collezione)
sono gestite nella nuova sezione "Configurazione" del backoffice, che sostituisce ed estende
l'attuale sezione "Categorie".

Il campo Collezione è un attributo interno dell'opera e non deve essere incluso nel gallery.json
generato da gallery_builder.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Migrare il DB: aggiungere le colonne `formato` (TEXT), `tecnica` (TEXT), `descrizione` (TEXT), `collezione` (TEXT) alla tabella `artwork` su Turso
- [ ] #2 Aggiungere le tabelle di configurazione `formato_option`, `tecnica_option`, `collezione_option` (colonne: id, label, position) su Turso
- [ ] #3 Aggiornare `turso_db.py` con le funzioni CRUD per le tre tabelle di opzioni e per i nuovi campi di Artwork
- [ ] #4 La sezione "Categorie" nel backoffice diventa "Configurazione": unica pagina con tab o sotto-sezioni per gestire Categorie, Formati, Tecniche e Collezioni (lista, creazione, modifica, eliminazione, riordinamento)
- [ ] #5 I form di creazione e modifica opera mostrano i quattro nuovi campi: Formato e Tecnica e Collezione come `<select>` popolate dalle rispettive tabelle di opzioni, Descrizione come `<textarea>`
- [ ] #6 `gallery_builder.generate_gallery_json()` e `ArtworkNS.to_dict()` includono `formato` e `tecnica` e `descrizione` nel JSON esportato, ma **non** `collezione`
- [ ] #7 Tutti i template aggiornati sono coerenti con lo stile minimalista della dashboard
<!-- AC:END -->
