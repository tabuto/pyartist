---
id: TSK-3
title: Implementare modello dati Artwork e connessione Turso
status: To Do
assignee: []
created_date: '2026-03-27 13:23'
labels:
  - fase-1
  - database
milestone: Fase 1 - Setup Progetto
dependencies: []
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare il modello SQLAlchemy Artwork e configurare la connessione al database Turso (libSQL/SQLite compatibile) tramite variabili d'ambiente.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 models.py contiene la classe Artwork con tutti i campi: id, title, category, year, technique, image_path, thumb_path, is_published, position
- [ ] #2 La connessione a Turso (libSQL/SQLite) è configurabile tramite variabile d'ambiente TURSO_URL
- [ ] #3 Le tabelle vengono create correttamente con db.create_all()
- [ ] #4 Funzione di test che inserisce e recupera un record di prova
<!-- AC:END -->
