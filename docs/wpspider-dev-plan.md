# WPSpider Development Plan

This document outlines the phased development plan to build the `wpspider` MVP (Minimum Viable Product). The goal is to create a Python CLI tool that crawls WordPress API endpoints, saves data to SQLite, and compiles into a standalone executable.

## Phase 1: Foundation & Configuration
**Goal:** Establish the project structure, configuration management, and logging infrastructure.

1.  **Project Initialization**
    -   [x] Create standard Python project structure (`src/wpspider/`, `tests/`).
    -   [x] Initialize `requirements.txt` (core dependencies: `requests`, `jsonschema` (optional), `appdirs` (maybe?), building blocks).
    -   [x] Create `scripts/dev.ps1` for easy local execution.

2.  **Configuration Manager**
    -   [x] Implement a `Config` class/module to read `config.json`.
    -   [x] Define default values (default endpoints: categories, comments, media, pages, posts, tags, users).
    -   [x] Implement validation: Ensure `target` is provided (via args or config).

3.  **Logging System**
    -   [x] Set up Python `logging` module.
    -   [x] Implement file logging (timestamped).
    -   [x] Add support for custom log file paths defined in `config.json`.
    -   [x] Ensure console output mirrors logs (optional but good for CLI).

## Phase 2: Database Architecture
**Goal:** Implement the SQLite storage layer to handle dynamic schemas and metadata.

1.  **Database Connection**
    -   [x] Create `DatabaseManager` class.
    -   [x] Implement connection logic to `.db` file (name from config).

2.  **Targets Metadata Table**
    -   [x] Define schema for `targets` table (`id`, `url`, `domain`, `date_crawled`).
    -   [x] Implement insertion/update logic for the current crawl session.

3.  **Dynamic Endpoint Tables**
    -   [x] Implement logic to check if a table exists for an endpoint.
    -   [x] **Strategy Decision**: Implement the "Generic Data Column" approach first for safety (Columns: `id`, `data` (JSON text), `crawled_at`). This ensures no data loss if WP schemas vary.
    -   [x] (Optional) Add specific columns extraction if critical fields are known constants.
        -   Start with `slug`, `link`, `title` (or `name`), and `date` as these are widespread across Posts, Pages, Users, and Terms.

## Phase 3: The Crawler Engine
**Goal:** Build the core logic for URL construction, API requests, and pagination.

1.  **URL Construction**
    -   [x] Implement `UrlBuilder` utility.
    -   [x] Logic to handle direct URL inputs vs. domain inputs.
    -   [x] Logic to append `/wp-json/wp/v2/` (or discovery) if plain domain is given.

2.  **Request Handler**
    -   [x] Implement robust HTTP request wrapper (using `requests`).
    -   [x] Add timeout and connection error handling.
    -   [x] Add user-agent headers.

3.  **Pagination Logic**
    -   [x] Implement the pagination loop (`?per_page=100&page=X`).
    -   [x] Detect termination condition: Empty array `[]` response or HTTP 400 (some WP versions return error on out-of-bounds page).
    -   [x] Handle rate limits (basic sleep if needed, though not strictly specified).

## Phase 4: Integration & Data Flow
**Goal:** Connect the Crawler to the Database and create the main execution loop.

1.  **Pipeline Orchestration**
    -   [x] Create `main.py` entry point.
    -   [x] Workflow:
        1.  Load Config.
        2.  Init DB & Log target.
        3.  Iterate Endpoints.
        4.  Crawl & Paginate.
        5.  Save batches to DB.

2.  **Error Handling Polish**
    -   [x] Ensure one failed endpoint doesn't crash the whole run.
    -   [x] Log specific errors (403 Forbidden, 404 Not Found) without stopping.

3.  **CLI Arguments**
    -   [x] Parse command line args to override `config.json` (e.g., `--target`, `--output`).

## Phase 5: Build & Distribution
**Goal:** package the application for end-users.

1.  **PyInstaller Setup**
    -   [x] Create `spec` file for PyInstaller.
    -   [x] Create `scripts/build.ps1` to run the build process.
    -   [x] Ensure `config.json` template is copied alongside the executable (or instructions provided).

2.  **Documentation & Validation**
    -   [x] Update `README.md` with usage instructions.
    -   [x] Document `config.json` structure.
    -   [x] Verify the executable runs on a clean Windows environment (if possible to test).
