"""Integrated Widgets package.

Qt widgets and utilities that integrate with `united_system` and `observable`.

This package is independent from any host application and does not create a
QApplication by itself. It is safe to import in any context.
"""

from ._version import __version__

# Re-export the stable widgets API
from .widget_controllers.real_united_scalar_controller import RealUnitedScalarController
from .widget_controllers.unit_combo_box_controller import UnitComboBoxController
from .widget_controllers.display_value_controller import DisplayValueController

__all__ = [
    "__version__",
    "RealUnitedScalarController",
    "DisplayValueController",
    "UnitComboBoxController",
]


