# Git & Version Control

## Commits

- Commits nur auf explizite User-Anfrage erstellen
- Commit-Message via HEREDOC formatieren
- Co-Author-Zeile: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Immer NEUE Commits erstellen — niemals amenden (außer explizit angefragt)
- Bei Pre-Commit-Hook-Fehler: Fix, re-stage, NEUER Commit (kein Amend — Amend würde vorherigen Commit modifizieren)
- Spezifische Dateien stagen statt `git add -A` oder `git add .` (verhindert versehentliches Committen sensibler Dateien)
- Keine sensiblen Dateien committen (.env, credentials) — User warnen wenn explizit angefragt

## Verbotene Aktionen (ohne explizite Anfrage)

- `push --force` — niemals auf main/deve/master; User warnen wenn angefragt
- `reset --hard`
- `checkout .` / `restore .` / `clean -f`
- `branch -D`
- `--no-verify` / `--no-gpg-sign` (Hooks nicht überspringen)
- Interaktive Flags (`-i`) bei rebase, add etc.
- `--no-edit` bei rebase
- Git Config ändern

## Push

- Nicht automatisch pushen — nur auf explizite Anfrage
- Einmalige Zustimmung gilt nicht als generelle Autorisierung für künftige Pushes

## Pull Requests

- `gh pr create` mit HEREDOC-Body
- Titel unter 70 Zeichen
- Body-Format:
  ```
  ## Summary
  <1-3 bullet points>

  ## Test plan
  [Bulleted markdown checklist of TODOs for testing]

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```
- Vor PR-Erstellung: git status, git diff, git log analysieren

## Destruktive Aktionen

Immer User-Bestätigung einholen vor:
- Dateien oder Branches löschen
- Force-Push, reset --hard
- Aktionen die für andere sichtbar sind (Push, PR, Issues kommentieren, Releases)

## Unbekannter State

Bei unbekannten Dateien, Branches oder Konfiguration: erst untersuchen, dann handeln.
- Merge-Konflikte: lösen statt verwerfen
- Lock-Files: Prozess untersuchen statt löschen
- Unbekannte Branches: nicht löschen ohne Nachfrage
