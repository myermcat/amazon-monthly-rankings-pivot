"""
Monthly Rankings Pivot System
A multi-dimensional pivot table system for Amazon Brand Analytics data.
"""

from .table_state import TableState
from .data_detector import DataDetector
from .pivot_table_manager import PivotTableManager

__version__ = "1.0.0"
__author__ = "Amazon R&D Team"

__all__ = [
    "TableState",
    "DataDetector", 
    "PivotTableManager"
]
