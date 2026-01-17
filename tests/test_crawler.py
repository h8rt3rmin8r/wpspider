import unittest
from unittest.mock import MagicMock, patch
from wpspider.crawler import UrlBuilder, WPCrawler
import requests

class TestUrlBuilder(unittest.TestCase):
    def test_normalize_base_url(self):
        # Case 1: Plain domain
        self.assertEqual(
            UrlBuilder.normalize_base_url("http://example.com"),
            "http://example.com/wp-json/wp/v2/"
        )
        # Case 1b: Scheme-less domain defaults to https
        self.assertEqual(
            UrlBuilder.normalize_base_url("example.com"),
            "https://example.com/wp-json/wp/v2/"
        )
        # Case 2: Clean slash
        self.assertEqual(
            UrlBuilder.normalize_base_url("http://example.com/"),
            "http://example.com/wp-json/wp/v2/"
        )
        # Case 3: Ends with /wp-json
        self.assertEqual(
            UrlBuilder.normalize_base_url("http://example.com/wp-json"),
            "http://example.com/wp-json/wp/v2/"
        )
        # Case 4: Full path provided
        self.assertEqual(
            UrlBuilder.normalize_base_url("http://example.com/wp-json/wp/v2"),
            "http://example.com/wp-json/wp/v2/"
        )

    def test_build_endpoint_url(self):
        base = "http://example.com/wp-json/wp/v2/"
        self.assertEqual(
            UrlBuilder.build_endpoint_url(base, "posts"),
            "http://example.com/wp-json/wp/v2/posts"
        )
        
        # Test if base lacks slash (though normalize fixes this)
        base_no_slash = "http://example.com/wp-json/wp/v2"
        self.assertEqual(
            UrlBuilder.build_endpoint_url(base_no_slash, "posts"),
            "http://example.com/wp-json/wp/v2/posts"
        )

class TestWPCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = WPCrawler("http://mock.com")

    @patch('wpspider.crawler.requests.Session.get')
    def test_crawl_endpoint_pagination_success(self, mock_get):
        # Setup mock responses
        # Page 1: returns 2 items
        mock_resp_1 = MagicMock()
        mock_resp_1.status_code = 200
        mock_resp_1.json.return_value = [{"id": 1}, {"id": 2}]
        mock_resp_1.headers = {}
        
        # Page 2: returns empty list (done)
        mock_resp_2 = MagicMock()
        mock_resp_2.status_code = 200
        mock_resp_2.json.return_value = []
        mock_resp_2.headers = {}

        mock_get.side_effect = [mock_resp_1, mock_resp_2]

        batches = list(self.crawler.crawl_endpoint("posts"))
        
        self.assertEqual(len(batches), 2) # One data batch + one terminal empty page
        self.assertEqual(len(batches[0][0]), 2)
        self.assertEqual(mock_get.call_count, 2)

    @patch('wpspider.crawler.requests.Session.get')
    def test_crawl_endpoint_400_termination(self, mock_get):
        # Page 1: 1 item
        mock_resp_1 = MagicMock()
        mock_resp_1.status_code = 200
        mock_resp_1.json.return_value = [{"id": 1}]
        mock_resp_1.headers = {}
        
        # Page 2: 400 Bad Request
        mock_resp_2 = MagicMock()
        mock_resp_2.status_code = 400
        mock_resp_2.headers = {}
        mock_resp_2.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_resp_2)
        
        mock_get.side_effect = [mock_resp_1, mock_resp_2]

        batches = list(self.crawler.crawl_endpoint("posts"))
        
        self.assertEqual(len(batches), 2)
        self.assertEqual(mock_get.call_count, 2)

    @patch('wpspider.crawler.requests.Session.get')
    def test_crawl_endpoint_400_with_json_error(self, mock_get):
        # Some WP installs return JSON error obj for out of bounds
        
        # Page 1: 1 item
        mock_resp_1 = MagicMock()
        mock_resp_1.status_code = 200
        mock_resp_1.json.return_value = [{"id": 1}]
        mock_resp_1.headers = {}

        # Page 2: Error object
        mock_resp_2 = MagicMock()
        mock_resp_2.status_code = 200 # Sometimes returns 200 even with error body? Or 400. Let's assume 200 but body is error.
        mock_resp_2.json.return_value = {'code': 'rest_post_invalid_page_number', 'message': '...'}
        mock_resp_2.headers = {}
        
        mock_get.side_effect = [mock_resp_1, mock_resp_2]
        
        batches = list(self.crawler.crawl_endpoint("posts"))
        
        self.assertEqual(len(batches), 2)
        self.assertEqual(mock_get.call_count, 2)

if __name__ == '__main__':
    unittest.main()
