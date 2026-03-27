---
id: TSK-8
title: Implementare autenticazione Google OAuth2
status: To Do
assignee: []
created_date: '2026-03-27 13:24'
labels:
  - fase-3
  - backoffice
  - auth
milestone: Fase 3 - Modulo Backoffice
dependencies: []
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementare il flusso di autenticazione Google OAuth2 tramite Authlib per proteggere tutte le route del backoffice.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 oauth.py configura Authlib con Google OAuth2
- [ ] #2 Route /login reindirizza a Google per l'autenticazione
- [ ] #3 Route /auth/callback gestisce il token e crea la sessione utente
- [ ] #4 Route /logout termina la sessione
- [ ] #5 Le route del backoffice sono protette da un decorator @login_required
- [ ] #6 Solo l'email autorizzata (configurabile via env) può accedere
<!-- AC:END -->
