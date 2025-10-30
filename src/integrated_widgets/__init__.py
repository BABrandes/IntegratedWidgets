"""
Integrated Widgets - Reactive PySide6/Qt Widget Framework

A comprehensive PySide6/Qt widget framework for reactive, unit-aware UI components with bidirectional data binding.

Import organization:
--------------------
- Top-level (`from integrated_widgets import ...`):
    - End-user widgets (e.g., IQtCheckBox, IQtTextEntry, IQtFloatEntry, etc.)
    - Signal hooks and debouncing utilities (IQtSignalHook, default)
- Payloads for custom layouting:
    - `from integrated_widgets.payloads import CheckBoxPayload, ...`
- Advanced/core API (for composition, custom containers, etc.):
    - `from integrated_widgets.core import IQtControllerWidgetBase, LayoutStrategyBase, ...`

Import structure cheatsheet:
    from integrated_widgets import IQtCheckBox, IQtTextEntry, ...
    from integrated_widgets.payloads import CheckBoxPayload, ...
    from integrated_widgets.core import IQtControllerWidgetBase, LayoutStrategyBase, ...
    from integrated_widgets import IQtSignalHook, default

"""

from ._version import __version__

# IQT Widgets - Primary API
from .iqt_widgets.iqt_check_box import IQtCheckBox
from .iqt_widgets.iqt_display_value import IQtDisplayValue
from .iqt_widgets.iqt_double_list_selection import IQtDoubleListSelection
from .iqt_widgets.iqt_float_entry import IQtFloatEntry
from .iqt_widgets.iqt_integer_entry import IQtIntegerEntry
from .iqt_widgets.iqt_optional_text_entry import IQtOptionalTextEntry
from .iqt_widgets.iqt_path_selector import IQtPathSelector
from .iqt_widgets.iqt_radio_buttons_select import IQtRadioButtonsSelect
from .iqt_widgets.iqt_range_slider import IQtRangeSlider
from .iqt_widgets.iqt_real_united_scalar_entry import IQtRealUnitedScalarEntry
from .iqt_widgets.iqt_listview_single_optional_select import IQtListviewSingleOptionalSelect
from .iqt_widgets.iqt_combobox_optional_select import IQtComboboxOptionalSelect
from .iqt_widgets.iqt_combobox_select import IQtComboboxSelect
from .iqt_widgets.iqt_text_entry import IQtTextEntry
from .iqt_widgets.iqt_unit_entry import IQtUnitEntry
from .auxiliaries.iqt_signal_hook import IQtSignalHook
from .auxiliaries.default import default

__all__ = [
    "__version__",
    # Simple entry widgets
    "IQtCheckBox",
    "IQtFloatEntry",
    "IQtIntegerEntry",
    "IQtTextEntry",
    "IQtOptionalTextEntry",
    # Display widgets
    "IQtDisplayValue",
    # Selection widgets
    "IQtRadioButtonsSelect",
    "IQtComboboxOptionalSelect",
    "IQtComboboxSelect",
    "IQtListviewSingleOptionalSelect",
    "IQtDoubleListSelection",
    # File/path widgets
    "IQtPathSelector",
    # Complex widgets
    "IQtRangeSlider",
    "IQtRealUnitedScalarEntry",
    "IQtUnitEntry",
    "IQtSignalHook",
    # Debouncing / default
    "default",
]
