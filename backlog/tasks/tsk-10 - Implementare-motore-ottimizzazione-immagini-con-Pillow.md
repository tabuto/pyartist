---
id: TSK-10
title: Implementare motore ottimizzazione immagini con Pillow
status: To Do
assignee: []
created_date: '2026-03-27 13:24'
labels:
  - fase-3
  - backoffice
  - image-processing
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare in sync_engine.py le funzioni di ottimizzazione immagini con Pillow: ridimensionamento a 1920px, generazione thumbnail 400px, output JPEG/WebP qualità 85.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 optimize_image() ridimensiona l'immagine a max 1920px (lato lungo) mantenendo le proporzioni
- [ ] #2 optimize_image() salva in JPEG qualità 85 o WebP
- [ ] #3 generate_thumbnail() crea una versione thumbnail a max 400px
- [ ] #4 Naming convention rispettata: titolo-opera-{id}.jpg e thumb_titolo-opera-{id}.jpg
- [ ] #5 Le funzioni sono in sync_engine.py e testate con immagini di prova
<!-- AC:END -->
