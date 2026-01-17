# WPSpider

Write a Python script that paginates through a Wordpress API endpoint for website posts (`/wp-json/wp/v2/posts?per_page=100`) and saves the resulting data.

## Inputs

- **Target**: A target website to extract Wordpress API data from
  - This input can be in the form of a domain ("example.com", "https://example.com/")
    - If the input points to a domain root, we auto-construct the path to what would typically be the appropriate API endpoint ("https://example.com/wp-json/wp/v2/posts").
  - This input can be a direct URL to the appropriate API endpoint or the root Wordpress "wp-json" endpoint.
    - If "/wp-json", we auto-construct the remaining chunks -> "/wp-json/wp/v2/posts"
    - If "/wp-json/wp/v2", we auto-construct the remaining chunks -> "/wp-json/wp/v2/posts"

## Outputs

The output data should be written to an sqlite database with the endpoint pages written to files named with the following name scheme: <ZeroPaddedPageNumber> + ".json"

## Operation Types

After deriving (or accepting as an input) the absolute path to the remote URL **Target**, we utilize the maximum "posts-per-page" query string (`?per_page=100`) to iterate through all available pages of "posts"
