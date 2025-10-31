"""Controlled Widgets for Integrated Widgets.

This module contains specialized Qt widgets with "controlled" semantics that prevent
feedback loops between UI and observables. These widgets are designed to be used with
controllers, which manage programmatic mutations through internal update contexts.

## Controlled Widgets

All widgets inherit from base controlled widget classes and wrap standard Qt widgets:

- **ControlledQLabel**: Label with controlled text management
- **ControlledLineEdit**: Line edit with controlled text management
- **ControlledCheckBox**: Checkbox with controlled state management
- **ControlledComboBox**: ComboBox with controlled selection management
- **ControlledEditableComboBox**: Editable ComboBox with controlled text/selection
- **ControlledRadioButtonGroup**: Radio button group with controlled selection
- **ControlledListWidget**: List widget with controlled selection management
- **ControlledRangeSlider**: Range slider with controlled span management
- **BlankableWidget**: Wrapper that can show/hide widgets based on optional values

## Why Controlled Widgets?

In reactive UI architectures with bidirectional binding, feedback loops can occur:
1. User changes widget → controller updates observable
2. Observable change → controller updates widget
3. Widget change triggers signal → infinite loop!

Controlled widgets prevent this by:
- Blocking programmatic mutations outside controller contexts
- Allowing user interactions to proceed normally
- Raising clear errors when misused

## Usage

These widgets are typically created and managed by controllers:

```python
from integrated_widgets.controllers import TextEntryController

# Controller internally uses ControlledLineEdit
controller = TextEntryController("Hello")
widget = controller.widget_line_edit  # Returns ControlledLineEdit instance
```

For advanced use cases, you can create controlled widgets directly, but you must
ensure programmatic mutations happen within proper update contexts.
"""

from .controlled_qlabel import ControlledQLabel
from .controlled_combobox import ControlledComboBox
from .controlled_editable_combobox import ControlledEditableComboBox
from .controlled_list_widget import ControlledListWidget
from .controlled_line_edit import ControlledLineEdit
from .controlled_radio_button_group import ControlledRadioButtonGroup
from .controlled_check_box import ControlledCheckBox
from .controlled_range_slider import ControlledRangeSlider
from .blankable_widget import BlankableWidget

__all__ = [
    "ControlledQLabel",
    "ControlledComboBox",
    "ControlledEditableComboBox",
    "ControlledListWidget",
    "ControlledLineEdit",
    "ControlledRadioButtonGroup",
    "ControlledCheckBox",
    "ControlledRangeSlider",
    "BlankableWidget",
]


