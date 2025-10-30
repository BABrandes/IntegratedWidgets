"""
Centralized payload definitions for IQT widget composition.

This module provides convenient access to all payload dataclasses used by IQT widgets.
Payloads describe the structure of widgets that can be arranged in custom layouts,
enabling flexible widget composition and responsive UI design.

Key Concepts:
-------------
- **Payloads**: Immutable dataclasses containing QWidget references
- **Composition**: Combine multiple widgets into reusable composite widgets
- **Layout Strategies**: Functions that arrange payload widgets visually
- **Type Safety**: Full type checking for widget composition

Usage Patterns:
---------------
1. **Simple Layouts**: Arrange a single widget with custom styling
2. **Composite Widgets**: Combine multiple related widgets (e.g., label + input)
3. **Complex Forms**: Build multi-section forms with custom arrangements
4. **Responsive UI**: Switch between different layouts dynamically

Basic Usage:
    >>> from integrated_widgets.payloads import TextEntryPayload, CheckBoxPayload
    >>> from integrated_widgets.core import IQtWidgetBase, LayoutPayloadBase
    >>> from dataclasses import dataclass
    >>>
    >>> @dataclass(frozen=True)
    ... class MyFormPayload(LayoutPayloadBase):
    ...     name_field: TextEntryPayload
    ...     enabled_checkbox: CheckBoxPayload
    >>>
    >>> # Create composite widget with custom layout...

Available Payloads:
------------------
All payload classes follow the naming convention: {WidgetName}Payload
"""

# Entry Widget Payloads
from .iqt_widgets.iqt_text_entry import Controller_Payload as TextEntryPayload
from .iqt_widgets.iqt_optional_text_entry import Controller_Payload as OptionalTextEntryPayload
from .iqt_widgets.iqt_float_entry import Controller_Payload as FloatEntryPayload
from .iqt_widgets.iqt_integer_entry import Controller_Payload as IntegerEntryPayload

# Selection Widget Payloads
from .iqt_widgets.iqt_check_box import Controller_Payload as CheckBoxPayload
from .iqt_widgets.iqt_combobox_select import Controller_Payload as ComboboxSelectPayload
from .iqt_widgets.iqt_combobox_optional_select import Controller_Payload as ComboboxOptionalSelectPayload
from .iqt_widgets.iqt_radio_buttons_select import Controller_Payload as RadioButtonsSelectPayload
from .iqt_widgets.iqt_listview_single_optional_select import Controller_Payload as ListviewSingleOptionalSelectPayload
from .iqt_widgets.iqt_double_list_selection import Controller_Payload as DoubleListSelectionPayload

# Display Widget Payloads
from .iqt_widgets.iqt_display_value import Controller_Payload as DisplayValuePayload

# Specialized Widget Payloads
from .iqt_widgets.iqt_path_selector import Controller_Payload as PathSelectorPayload
from .iqt_widgets.iqt_unit_entry import Controller_Payload as UnitEntryPayload
from .iqt_widgets.iqt_real_united_scalar_entry import Controller_Payload as RealUnitedScalarEntryPayload

# Range Widget Payloads
from .iqt_widgets.iqt_range_slider import Controller_Payload as RangeSliderPayload


# Export all with easy-to-find names
__all__ = [
    # Entry widgets
    "TextEntryPayload",
    "OptionalTextEntryPayload",
    "FloatEntryPayload",
    "IntegerEntryPayload",
    # Selection widgets
    "CheckBoxPayload",
    "ComboboxSelectPayload",
    "ComboboxOptionalSelectPayload",
    "RadioButtonsSelectPayload",
    "ListviewSingleOptionalSelectPayload",
    "DoubleListSelectionPayload",
    # Display widgets
    "DisplayValuePayload",
    # Specialized widgets
    "PathSelectorPayload",
    "UnitEntryPayload",
    "RealUnitedScalarEntryPayload",
    # Range widgets
    "RangeSliderPayload",
]
