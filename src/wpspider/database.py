import sqlite3
import json
import logging
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages SQLite database connections and operations for WPSpider.
    Handles schema creation and data insertion for WordPress endpoints.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Establishes connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.debug(f"Connected to database: {self.db_path}")
            self._init_metadata_tables()
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.debug("Database connection closed")

    def _init_metadata_tables(self):
        """Initializes the metadata tables (targets)."""
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        
        # Targets table to track crawl history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                domain TEXT NOT NULL,
                date_crawled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()

    def log_target(self, url: str) -> Optional[int]:
        """
        Logs the target URL and returns the row ID.
        Extracts domain from the URL.
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
            
        parsed = urlparse(url)
        # Handle cases where url might not have scheme (though validation should catch this)
        if not parsed.netloc and parsed.path:
             domain = parsed.path.split('/')[0]
        else:
            domain = parsed.netloc
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO targets (url, domain, date_crawled) VALUES (?, ?, ?)",
            (url, domain, datetime.now().isoformat())
        )
        self.conn.commit()
        logger.info(f"Logged target: {url} (ID: {cursor.lastrowid})")
        return cursor.lastrowid

    def ensure_endpoint_table(self, endpoint: str):
        """
        Ensures a table exists for the given endpoint using the generic schema.
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        # Basic sanitization: keep only alphanumeric and underscores
        sanitized_table = "".join(c for c in endpoint if c.isalnum() or c == '_')
        if not sanitized_table:
            logger.warning(f"Skipping table creation for invalid endpoint name: {endpoint}")
            return
        
        cursor = self.conn.cursor()
        
        # Generic Schema with extracted columns for easier querying:
        # id: Auto-increment primary key for local ID
        # wp_id: The ID from WordPress (if present in data, otherwise NULL)
        # slug: URL friendly name (posts, pages, terms, users)
        # link: Permalink to the object
        # title: The title or name of the object
        # date: The publication date
        # data: Complete JSON response for the item
        # crawled_at: Timestamp
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {sanitized_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wp_id INTEGER, 
                slug TEXT,
                link TEXT,
                title TEXT,
                date TEXT,
                data TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def _extract_title(self, item: Dict[str, Any]) -> Optional[str]:
        """Extracts a display title/name from various WP object structures."""
        # 1. Try 'title.rendered' (Posts, Pages, Media)
        title_obj = item.get('title')
        if isinstance(title_obj, dict) and 'rendered' in title_obj:
            return title_obj['rendered']
        
        # 2. Try 'name' (Users, Categories, Tags)
        if 'name' in item and isinstance(item['name'], str):
            return item['name']
            
        return None

    def save_batch(self, endpoint: str, data_items: List[Dict[str, Any]]):
        """
        Saves a batch of data items to the endpoint table.
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
            
        if not data_items:
            return

        sanitized_table = "".join(c for c in endpoint if c.isalnum() or c == '_')
        if not sanitized_table:
            logger.warning(f"Invalid endpoint name '{endpoint}', skipping save.")
            return

        self.ensure_endpoint_table(sanitized_table)
        
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        try:
            # Prepare data
            rows = []
            for item in data_items:
                # Try to extract common fields
                wp_id = item.get('id')
                if not isinstance(wp_id, int):
                    wp_id = None
                
                slug = item.get('slug')
                link = item.get('link')
                
                # Title extraction logic
                title = self._extract_title(item)
                
                # Date extraction logic (try date_gmt, then date, else None)
                date_val = item.get('date_gmt') or item.get('date')

                json_data = json.dumps(item)
                rows.append((wp_id, slug, link, title, date_val, json_data, now))
                
            cursor.executemany(f"""
                INSERT INTO {sanitized_table} (wp_id, slug, link, title, date, data, crawled_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows)
            
            self.conn.commit()
            logger.info(f"Saved {len(rows)} items to table '{sanitized_table}'")
            
        except sqlite3.Error as e:
            logger.error(f"Failed to save batch to {sanitized_table}: {e}")
            self.conn.rollback()
            raise
