# Backend API - Sistem Deteksi Dini Stunting

# Fix Python path for imports when running from different directories
import sys
import os

# Ensure parent directory (/api) is in sys.path so 'app' module can be imported
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

