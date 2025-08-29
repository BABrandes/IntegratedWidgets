"""Integrated Widgets package.

Qt widgets and utilities that integrate with `united_system` and `observable`.

This package is independent from any host application and does not create a
QApplication by itself. It is safe to import in any context.
"""

from ._version import __version__

# Re-export the stable widgets API
from .widget_controllers.base_controller import BaseWidgetController
from .widget_controllers.real_united_scalar_controller import RealUnitedScalarController
from .widget_controllers.unit_combo_box_controller import UnitComboBoxController
from .widget_controllers.display_value_controller import DisplayValueController
from .widget_controllers.selection_optional_option_controller import SelectionOptionalOptionController
from .widget_controllers.selection_option_controller import SelectionOptionController
from .widget_controllers.check_box_controller import CheckBoxController
from .widget_controllers.integer_entry_controller import IntegerEntryController
from .widget_controllers.radio_buttons_controller import RadioButtonsController
from .widget_controllers.range_slider_controller import RangeSliderController

__all__ = [
    "__version__",
    "BaseWidgetController",
    "RealUnitedScalarController",
    "DisplayValueController",
    "UnitComboBoxController",
    "SelectionOptionalOptionController",
    "SelectionOptionController",
    "CheckBoxController",
    "IntegerEntryController",
    "RadioButtonsController",
    "RangeSliderController",
]


