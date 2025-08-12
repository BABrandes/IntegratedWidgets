"""Integrated Widgets package.

Qt widgets and utilities that integrate with `united_system` and `observable`.

This package is independent from any host application and does not create a
QApplication by itself. It is safe to import in any context.
"""

from ._version import __version__

# Re-export the stable widgets API
from .widgets import UnitValueDisplay

__all__ = [
    "__version__",
    "UnitValueDisplay",
]


