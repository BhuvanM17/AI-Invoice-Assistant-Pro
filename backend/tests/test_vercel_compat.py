import os
import sys
import unittest
from unittest.mock import patch

# Add the project root to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.core.agent import InvoiceStorage

class TestVercelCompatibility(unittest.TestCase):
    def test_vercel_storage_fallback(self):
        # Simulate Vercel environment
        with patch.dict(os.environ, {"VERCEL": "1"}):
            storage = InvoiceStorage("any/path/invoices.json")
            
            # On Windows, /tmp isn't a standard path, but our code should still use it as redirected
            # This test mainly checks the redirection logic
            self.assertEqual(storage.storage_path, os.path.join("/tmp", "invoices.json"))
            print(f"Verified: Storage path redirected to {storage.storage_path}")

    def test_normal_storage(self):
        # Simulate normal environment
        with patch.dict(os.environ, {}, clear=True):
            if "VERCEL" in os.environ:
                 del os.environ["VERCEL"]
                 
            original_path = "data/test_invoices.json"
            storage = InvoiceStorage(original_path)
            
            self.assertEqual(storage.storage_path, original_path)
            print(f"Verified: Normal storage path remains {storage.storage_path}")

if __name__ == "__main__":
    unittest.main()
