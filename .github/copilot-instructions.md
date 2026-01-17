# wpspider Copilot Instructions

## Project Context
`wpspider` is a Python CLI tool that crawls WordPress API endpoints and saves data to a SQLite database.
- **Core Specification**: Always refer to `docs/wpspider-prompt.md` for functional requirements.
- **Data Structure**: JSON schemas for WordPress endpoints are located in `docs/schemas/`.
- **Goal**: Produce a standalone PyInstaller executable defined by `config.json`.

## Architecture & Data Flow
1.  **Input**: Domain/URL (Runtime Argument) + Endpoints list (via `config.json` or defaults).
    -   **Clarification**: The Target URL is highly variable and should be provided via CLI argument, not statically defined in `config.json`.
2.  **Process**:
    - Construct API path (`/wp-json/...`).
    - Pagination loop (max `per_page=100`).
    - Handles schema variations and errors gracefully.
3.  **Output**: SQLite database (`.db`).
    - `targets` table: Metadata (crawled date, url).
    - `[endpoint]` tables: One per endpoint (e.g., `posts`, `media`).

## Workflows & Environment
- **OS**: Windows. Use PowerShell for all terminal commands.
- **Python**: Use the local virtual environment `.venv/`.
    - Activate: `.venv\Scripts\Activate.ps1` (or rely on usage within VS Code which handles this).
    - Interpreter path is generally `.venv/Scripts/python.exe`.
- **Scripts**: Automation lives in `scripts/`.
    - Existing: `scripts/json2schema.ps1` (Generates schemas using `genson`).
    - **Convention**: If creating new build/test capabilities, wrap them in PowerShell scripts in `scripts/` and document in `README.md`.

## Development Guidelines
- **Spec-First**: Implement features strictly according to `docs/wpspider-prompt.md`.
- **Dependencies**: Manage via standard requirements files (create `requirements.txt` if missing) and `.venv`.
- **Packaging**: Code must be compatible with PyInstaller bundling.
- **Testing**: Create tests that mock API responses (do not hit live sites for unit tests).

## Safety & Exclusion
- **CRITICAL**: NEVER read, parse, search, or modify anything under `.archive/`.
