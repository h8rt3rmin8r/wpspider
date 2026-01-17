# wpspider — Copilot agent notes

- Prefer small, spec-aligned increments (Sprint 0 → Sprint N); if you introduce dev commands/scripts, document them in `README.md`.
- **Do not rely on global Python for running commands**: use the repo-local `.venv` and the PowerShell scripts in `scripts/` (e.g. `scripts/dev-core.ps1`, `scripts/check-core.ps1`).

## Safety
- NEVER read, parse, search, or modify anything under `.archive/`.
