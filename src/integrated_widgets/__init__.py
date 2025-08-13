"""Integrated Widgets package.

Qt widgets and utilities that integrate with `united_system` and `observable`.

This package is independent from any host application and does not create a
QApplication by itself. It is safe to import in any context.
"""

from ._version import __version__

# Re-export the stable widgets API
from .widget_controllers.display_real_united_scalar_controller import DisplayRealUnitedScalarController
from .widget_controllers.edit_real_united_scalar_controller import EditRealUnitedScalarController
from .widget_controllers.check_box_controller import CheckBoxController
from .widget_controllers.integer_entry_controller import IntegerEntryController
from .widget_controllers.combo_box_controller import ComboBoxController
from .widget_controllers.radio_buttons_controller import RadioButtonsController
from .widget_controllers.path_selector_controller import PathSelectorController
from .widget_controllers.range_slider_controller import RangeSliderController

__all__ = [
    "__version__",
    "DisplayRealUnitedScalarController",
    "EditRealUnitedScalarController",
    "CheckBoxController",
    "IntegerEntryController",
    "ComboBoxController",
    "RadioButtonsController",
    "PathSelectorController",
    "RangeSliderController",
]


