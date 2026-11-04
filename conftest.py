"""
Pytest автоматически загружает conftest.py из корня и добавляет
его директорию в sys.path
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))