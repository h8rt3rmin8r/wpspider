import unittest
import os
import sys

# Allow importing from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wpspider.config import Config

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        # We need a dummy config file or just rely on defaults if file missing?
        # But Config fails if file is okay but target is missing.
        # Let's mock a config file or just rely on the existing one in root.
        pass

    def test_validation_error(self):
        # Test that empty validation raises error
        c = Config("non_existent_file.json")
        # Empty config raises ValueError because target is None
        with self.assertRaises(ValueError):
            c.validate()

if __name__ == '__main__':
    unittest.main()
