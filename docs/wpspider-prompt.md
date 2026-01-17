# WPSpider

Write a Python module that crawls and paginates through the Wordpress API endpoints related to a target website and saves the resulting data into an sqlite database.

## Inputs

- **Target**: A target website to extract Wordpress API data from
  - This input can be in the form of a domain ("example.com", or "https://example.com/")
    - If the input points to a domain root, we auto-construct the path to what would typically be the appropriate API endpoint ("https://example.com/wp-json/", "https://example.com/wp-json/wp/v2/", etc).
  - This input can be a direct URL to an API endpoint or the root Wordpress "wp-json" endpoint (either way, we can still auto-construct the remaining chunks as needed).
    - If "/wp-json", we auto-construct the remaining chunks -> "/wp-json/wp/v2/posts" etc
    - If "/wp-json/wp/v2", we auto-construct the remaining chunks -> "/wp-json/wp/v2/posts" etc
- **Endpoints**: An array of Wordpress API endpoints to extract data from
  - If not provided, we default to the following common endpoints:
    - categories
    - comments
    - media
    - pages
    - posts
    - tags
    - users

## Outputs

An sqlite database file will contain a "targets" table with metadata related to the crawl (e.g. target URL, date crawled, etc). This table should have the following columns:
- id (Primary Key)
- url (Text)
- domain (Text)
- date_crawled (Datetime)

The output data should be written to the sqlite metadata database. The database should contain a table for each endpoint, with the table name matching the endpoint name (e.g. "posts" table for the "posts" endpoint). Each table should have columns that correspond to the fields returned by the Wordpress API for that endpoint. If necessary, to avoid data loss, columns can be created with a generic "data" column that stores the entire JSON object as text (or other appropriate format).

## Operation Types

After deriving (or accepting as an input) the absolute path to the remote URL **Target**, we utilize the maximum "posts-per-page" query string (`?per_page=100`) to iterate through all available pages of "posts" when possible. We continue to paginate through the results until we reach a page that returns an empty array, indicating that there are no more results to fetch. Expect that some endpoints may not support pagination or may have different pagination mechanisms; handle these cases appropriately by checking the response structure and adjusting the logic as needed. Bear in mind that some endpoints may be protected or entirely disabled. We need to handle such errors gracefully, logging any issues encountered without terminating the entire process.

## Final Production

- The finalized module should be bundled into a single binary executable using PyInstaller or a similar tool. This executable should be easy to deploy and run on various systems without requiring users to install Python or any dependencies manually.
- The module should require a "cfg" file in the same directory as the executable. This "cfg" file should allow users to specify default parameters such as the target website, endpoints to crawl, output database name, and any other relevant settings.
- Ensure that the module includes comprehensive error handling and logging to facilitate troubleshooting and ensure robustness during execution.
  - Logs should be written to a file in the same directory as the executable, with timestamps and relevant context for each log entry.
  - Users should be able to point the logging output to a custom location via the "cfg" file if desired.
- Provide clear documentation on how to use the executable, including instructions on configuring the "cfg" file, running the module, and interpreting the output database.
