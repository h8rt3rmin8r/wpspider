# WPSpider

**WPSpider** is a robust, standalone command-line tool designed to crawl WordPress websites via their publicly available REST API. It efficiently paginates through endpoints (posts, pages, media, etc.) and archives the data into a structured SQLite database for analysis, backup, or migration.

## Features

-   **Intelligent Discovery**: Automatically handles API path construction from simple domains (e.g., `example.com` → `https://example.com/wp-json/wp/v2/`).
-   **Smart Pagination**: Iterates through all available pages using maximum page size to ensure complete data retrieval.
-   **Resilient Crawling**: Handles rate limiting, missing endpoints, and API errors gracefully without crashing.
-   **Flexible Output**: Saves all data to a portable SQLite database (`.db`) with metadata tracking.
-   **Standalone Executable**: Distributed as a single `.exe` file requiring no Python installation for end-users.
-   **Configurable**: Fully controlled via a simple `config.json` file.

## Installation

### For End Users
1.  Download the latest release binary (`wpspider.exe`).
2.  Ensure `config.json` is present in the same directory.

### For Developers
1.  Clone the repository.
2.  Initialize the environment (Windows/PowerShell):
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

## Usage

### 1. Configuration
Create or edit the `config.json` file in the application directory.

**Minimal Example:**
```json
{
    "target": "https://techcrunch.com",
    "db_name": "techcrunch_data.db"
}
```

**Full Configuration Example:**
```json
{
    "target": "https://example.com",
    "endpoints": [
        "posts",
        "pages",
        "media",
        "categories",
        "users"
    ],
    "db_name": "crawled_data.db",
    "log_file": "wpspider.log"
}
```

| Setting | Description | Default |
| :--- | :--- | :--- |
| `target` | The URL or domain of the WordPress site. | **Required** |
| `endpoints` | List of API endpoints to crawl. | `['posts', 'pages', 'media', ...]` |
| `db_name` | Name of the SQLite database file. | `wpspider.db` |
| `log_file` | Path to save the execution log. | `wpspider.log` |

### 2. Running the Crawler
Run the executable (or Python script) from your terminal:

```powershell
.\wpspider.exe
```

Or from source:
```powershell
python -m wpspider.main
```

The tool will display progress as it connects to the target, discovers endpoints, and fetches records.

## Output Structure

Data is saved to a SQLite database specified in your config.

### Metadata Table (`targets`)
Tracks the history of crawls.
-   `id`: Primary Key
-   `url`: The full API URL used.
-   `domain`: The target domain.
-   `date_crawled`: Timestamp of the operation.

### Data Tables
Each endpoint gets its own table (e.g., `posts`, `users`).
To ensure 100% data fidelity across different WordPress versions and plugin schemas:
-   `id`: The WordPress object ID.
-   `data`: The full raw JSON object stored as text.
-   `crawled_at`: Timestamp for the specific record.

## Development

### Structure
-   `src/`: Source code.
-   `tests/`: Unit and integration tests.
-   `scripts/`: PowerShell automation scripts.
-   `docs/`: Project documentation and schemas.

### Building the Executable
To bundle the application into a standalone `.exe`:

```powershell
# Install build dependencies
pip install pyinstaller

# Run the build script
.\scripts\build.ps1
```

The output will be located in the `dist/` folder.

## License

[MIT License](LICENSE)
