---
id: TSK-5
title: Implementare gallery dinamica con Alpine.js e gallery.json
status: To Do
assignee: []
created_date: '2026-03-27 13:24'
labels:
  - fase-2
  - website
milestone: Fase 2 - Sito Web Statico
dependencies: []
priority: high
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare con Alpine.js il fetch dinamico del file gallery.json e la renderizzazione delle opere nella griglia della gallery.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Alpine.js esegue fetch di /data/gallery.json al caricamento della pagina
- [ ] #2 Le opere vengono renderizzate nella griglia responsiva
- [ ] #3 Ogni card mostra: thumbnail, titolo, categoria e dettagli (anno + tecnica)
- [ ] #4 Le immagini usano object-fit: contain per non tagliare le opere
- [ ] #5 Stato di loading e gestione errore fetch implementati
<!-- AC:END -->
