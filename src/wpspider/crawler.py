import logging
import time
import requests
from typing import List, Dict, Any, Generator, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class UrlBuilder:
    """Helper to construct WordPress API URLs."""
    
    @staticmethod
    def normalize_base_url(target: str) -> str:
        """
        Ensures the target URL points to the WP API root.
        """
        target = target.strip().rstrip('/')
        
        if '/wp-json' not in target:
            # Assume it's a domain root, append default API path
            return f"{target}/wp-json/wp/v2/"
        
        # If it ends in /wp-json, usually we want /wp-json/wp/v2/
        if target.endswith('/wp-json'):
             return f"{target}/wp/v2/"

        # If it already has some path like /wp-json/wp/v2, just ensure trailing slash
        return f"{target}/"

    @staticmethod
    def build_endpoint_url(base_url: str, endpoint: str) -> str:
        """Joins the base API URL with the endpoint."""
        if not base_url.endswith('/'):
            base_url += '/'
        return urljoin(base_url, endpoint)

class WPCrawler:
    """
    Handles the crawling logic for WordPress endpoints using pagination.
    """
    def __init__(self, target_url: str):
        self.base_url = UrlBuilder.normalize_base_url(target_url)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'wpspider/0.1 (Targeting public WP API)'
        })
    
    def fetch_page(self, url: str, params: Dict[str, Any]) -> requests.Response:
        """Wrapper for requests to handle basic errors/timeouts."""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            # We log simple warnings here, but let the caller handle logic flow (like break loop)
            # unless it's a critical failure
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise

    def crawl_endpoint(self, endpoint: str) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Yields batches of items from a specific endpoint, handling pagination.
        """
        url = UrlBuilder.build_endpoint_url(self.base_url, endpoint)
        page = 1
        per_page = 100
        
        logger.info(f"Starting crawl for endpoint: {endpoint} at {url}")
        
        while True:
            params = {
                'per_page': per_page,
                'page': page
            }
            
            try:
                response = self.fetch_page(url, params)
                
                # Check if response provides JSON content type roughly
                content_type = response.headers.get('Content-Type', '')
                if 'json' not in content_type:
                    logger.warning(f"Endpoint {endpoint} returned non-JSON content type: {content_type}")
                    # Try parsing anyway, some servers are misconfigured
                
                try:
                    data = response.json()
                except ValueError:
                    logger.error(f"Endpoint {endpoint} returned invalid JSON.")
                    break
                
                # Check termination conditions
                if not data:
                    logger.info(f"Endpoint {endpoint}: Empty response at page {page}. Finished.")
                    break
                
                if isinstance(data, dict) and ('code' in data or 'message' in data):
                    # Some inputs might return an error object instead of list
                    # e.g. {'code': 'rest_post_invalid_page_number', 'message': '...'}
                    logger.info(f"Endpoint {endpoint}: Received API message at page {page}: {data.get('code', 'unknown')}. Finished.")
                    break
                
                if not isinstance(data, list):
                    logger.error(f"Endpoint {endpoint} returned unexpected format (not list): {type(data)}")
                    break

                yield data
                
                # Check headers for total pages to anticipate end
                total_pages = response.headers.get('X-WP-TotalPages')
                if total_pages and page >= int(total_pages):
                    logger.info(f"Endpoint {endpoint}: Reached X-WP-TotalPages ({total_pages}). Finished.")
                    break
                
                page += 1
                
                # Simple rate limiting
                time.sleep(0.2)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    logger.info(f"Endpoint {endpoint}: Received 400 Bad Request at page {page}. Assuming end of pagination.")
                    break
                elif e.response.status_code in [401, 403]:
                    logger.warning(f"Endpoint {endpoint}: Access denied ({e.response.status_code}). Skipping.")
                    break
                elif e.response.status_code == 404:
                    logger.warning(f"Endpoint {endpoint}: Not found. Skipping.")
                    break
                else:
                    logger.error(f"Stopping {endpoint} due to HTTP error: {e}")
                    break
            except Exception as e:
                logger.error(f"Stopping {endpoint} due to unexpected error: {e}")
                break
