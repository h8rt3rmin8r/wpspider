import unittest
import os
import sqlite3
import json
import tempfile
import sys

# Allow importing from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wpspider.database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for the database
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.temp_db_fd)
        
        self.db = DatabaseManager(self.temp_db_path)
        self.db.connect()

    def tearDown(self):
        self.db.close()
        # Remove the temp file
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_init_metadata(self):
        assert self.db.conn is not None
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='targets';")
        self.assertIsNotNone(cursor.fetchone(), "targets table should exist")

    def test_log_target(self):
        assert self.db.conn is not None
        url = "https://example.com"
        row_id = self.db.log_target(url)
        self.assertIsInstance(row_id, int)
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT url, domain FROM targets WHERE id=?", (row_id,))
        row = cursor.fetchone()
        self.assertEqual(row[0], url)
        self.assertEqual(row[1], "example.com")

    def test_save_batch(self):
        assert self.db.conn is not None
        endpoint = "posts"
        data = [
            {
                "id": 101, 
                "title": {"rendered": "Hello World"}, 
                "slug": "hello-world",
                "link": "http://example.com/hello-world",
                "date": "2023-01-01T12:00:00"
            },
            {
                "id": 102, 
                "title": {"rendered": "Post 2"},
                "slug": "post-2"
            }
        ]
        
        self.db.save_batch(endpoint, data)
        
        cursor = self.db.conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts';")
        self.assertIsNotNone(cursor.fetchone(), "posts table should be created")
        
        # Check content and extracted fields
        cursor.execute("SELECT wp_id, title, slug, link, date, data FROM posts ORDER BY wp_id")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2)
        
        # Row 1 checks
        self.assertEqual(rows[0][0], 101) # wp_id
        self.assertEqual(rows[0][1], "Hello World") # extracted title
        self.assertEqual(rows[0][2], "hello-world") # slug
        self.assertEqual(rows[0][3], "http://example.com/hello-world") # link
        self.assertEqual(rows[0][4], "2023-01-01T12:00:00") # date
        self.assertEqual(json.loads(rows[0][5])['slug'], "hello-world") # json blob
        
        # Row 2 checks (missing fields)
        self.assertEqual(rows[1][0], 102)
        self.assertEqual(rows[1][1], "Post 2")
        self.assertIsNone(rows[1][3]) # link is missing

    def test_save_batch_users_extraction(self):
        # Test extraction for User/Term like objects (using 'name' instead of title.rendered)
        assert self.db.conn is not None
        endpoint = "users"
        data = [
            {
                "id": 1,
                "name": "Admin User",
                "slug": "admin",
                "link": "http://example.com/author/admin"
            }
        ]
        
        self.db.save_batch(endpoint, data)
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT title, slug FROM users")
        row = cursor.fetchone()
        
        self.assertEqual(row[0], "Admin User") # Should extract 'name' into 'title' column
        self.assertEqual(row[1], "admin")

    def test_save_batch_no_id(self):
        assert self.db.conn is not None
        endpoint = "options" # some endpoints might not have IDs
        data = [
            {"key": "value", "foo": "bar"}
        ]
        
        self.db.save_batch(endpoint, data)
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT wp_id, data FROM options")
        row = cursor.fetchone()
        
        self.assertIsNone(row[0])
        self.assertEqual(json.loads(row[1])['key'], "value")

    def test_context_manager(self):
        # Test context manager usage
        with DatabaseManager(self.temp_db_path) as db:
            assert db.conn is not None
            self.assertIsNotNone(db.conn)
            # Should be able to query
            cursor = db.conn.cursor()
            cursor.execute("SELECT 1")
            self.assertEqual(cursor.fetchone()[0], 1)
            
        # Should be closed now
        self.assertIsNone(db.conn)

if __name__ == '__main__':
    unittest.main()
