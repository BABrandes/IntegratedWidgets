"""
Centralized payload definitions for IQt widgets.

This module re-exports all payload dataclasses from their respective widget modules
with convenient, discoverable names. This makes it easy to find the right payload
for a specific widget when composing widgets.

Usage:
    >>> from integrated_widgets.payloads import CheckBoxPayload, TextEntryPayload
    >>> # Use payloads when composing widgets or creating custom layouts
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
