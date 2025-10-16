"""Integrated Widgets - High-level Qt widgets with observable binding.

This package provides IQT (Integrated Qt) widgets - easy-to-use, high-level widgets
that integrate with `united_system` and `observables` for reactive programming.

## Quick Start

Import the IQT widgets you need:

    from integrated_widgets import (
        IQtCheckBox,
        IQtFloatEntry,
        IQtTextEntry,
        IQtSelectionOption,
    )

## Low-Level API

For advanced use cases, low-level controllers and widgets are available in `core`:

    from integrated_widgets.core import (
        BaseController,
        CheckBoxController,
        ControlledLineEdit,
    )
"""

from ._version import __version__

# IQT Widgets - Primary API
from .iqt_widgets.iqt_layouted_widget import IQtLayoutedWidget, LayoutStrategy
from .iqt_widgets.iqt_check_box import IQtCheckBox
from .iqt_widgets.iqt_display_value import IQtDisplayValue
from .iqt_widgets.iqt_double_list_selection import IQtDoubleListSelection
from .iqt_widgets.iqt_float_entry import IQtFloatEntry
from .iqt_widgets.iqt_integer_entry import IQtIntegerEntry
from .iqt_widgets.iqt_optional_text_entry import IQtOptionalTextEntry
from .iqt_widgets.iqt_path_selector import IQtPathSelector
from .iqt_widgets.iqt_radio_buttons import IQtRadioButtons
from .iqt_widgets.iqt_range_slider import IQtRangeSlider
from .iqt_widgets.iqt_real_united_scalar import IQtRealUnitedScalar
from .iqt_widgets.iqt_selection_optional_option import IQtSelectionOptionalOption
from .iqt_widgets.iqt_selection_option import IQtSelectionOption
from .iqt_widgets.iqt_single_list_selection import IQtSingleListSelection
from .iqt_widgets.iqt_text_entry import IQtTextEntry
from .iqt_widgets.iqt_unit_combo_box import IQtUnitComboBox

# Commonly used constant
from .util.base_controller import DEFAULT_DEBOUNCE_MS

# Other
from .util.qt_signal_hook import QtSignalHook

__all__ = [
    "__version__",

    # Widgets with payload-driven layouts
    "IQtLayoutedWidget",
    "LayoutStrategy",

    # Simple entry widgets
    "IQtCheckBox",
    "IQtFloatEntry",
    "IQtIntegerEntry",
    "IQtTextEntry",
    "IQtOptionalTextEntry",
    
    # Display widgets
    "IQtDisplayValue",
    
    # Selection widgets
    "IQtRadioButtons",
    "IQtSelectionOption",
    "IQtSelectionOptionalOption",
    "IQtSingleListSelection",
    "IQtDoubleListSelection",
    
    # File/path widgets
    "IQtPathSelector",
    
    # Complex widgets
    "IQtRangeSlider",
    "IQtUnitComboBox",
    "IQtRealUnitedScalar",
    
    # Constants
    "DEFAULT_DEBOUNCE_MS",

    # Other
    "QtSignalHook",
]
