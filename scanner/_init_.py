# scanner/__init__.py

from .spider import Spider
from .sqli import SQLiScanner

__all__ = ["Spider", "SQLiScanner"]
