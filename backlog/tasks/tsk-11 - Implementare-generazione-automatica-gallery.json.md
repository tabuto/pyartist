---
id: TSK-11
title: Implementare generazione automatica gallery.json
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
Implementare la funzione generate_json() in sync_engine.py che esporta le opere pubblicate dal database in website/data/gallery.json.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 generate_json() legge le opere con is_published=True ordinate per position
- [ ] #2 Output è un array JSON conforme allo schema definito nelle SPECS sezione 4
- [ ] #3 Il file viene salvato in website/data/gallery.json
- [ ] #4 La funzione viene invocata automaticamente dopo ogni modifica/upload opera
<!-- AC:END -->
