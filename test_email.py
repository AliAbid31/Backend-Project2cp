import sys
import os

# Set up path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.services.email_service import _send_email_base, ENABLE_EMAIL_DEBUG
import time

def test_email():
    start = time.time()
    print("Testing email sending...")
    success, message = _send_email_base("oa_abid@esi.dz", "Test", "<h1>Test</h1>")
    end = time.time()
    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Time taken: {end - start:.2f} seconds")
    print(f"ENABLE_EMAIL_DEBUG is: {ENABLE_EMAIL_DEBUG}")

if __name__ == "__main__":
    test_email()
