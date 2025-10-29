"""Core components for Integrated Widgets.

This module contains the low-level controllers, controlled widgets, and base classes
that power the high-level IQT widgets. Most users should use the IQT widgets from the
main package instead of these core components directly.

## Architecture Overview

The core module implements the three-layer architecture:

1. **Controllers** - Manage bidirectional data binding between observables and Qt widgets
2. **Controlled Widgets** - Specialized Qt widgets with feedback loop prevention
3. **Base Classes** - Abstract base classes providing common functionality

## Controller Classes

Controllers sit between your application logic (observables) and the UI (Qt widgets):

- **BaseController**: Abstract base for all controllers
- **BaseSingleHookController**: For controllers managing a single observable
- **BaseComplexHookController**: For controllers managing multiple observables

### Specific Controllers

- **CheckBoxController**: Boolean checkbox with label support
- **FloatEntryController**: Floating-point number entry with validation
- **IntegerEntryController**: Integer number entry with validation
- **TextEntryController**: Single-line text input with validation
- **OptionalTextEntryController**: Optional text input with clear button
- **RadioButtonController**: Exclusive selection from multiple options
- **SelectionOptionController**: Dropdown selection from options
- **SelectionOptionalOptionController**: Optional dropdown selection
- **SingleListSelectionController**: Single selection from a list
- **DoubleListSelectionController**: Multiple selection from a list
- **DisplayValueController**: Read-only value display with formatting
- **PathSelectorController**: File/directory path selection
- **RangeSliderController**: Two-handle range slider with value displays
- **UnitComboBoxController**: Unit selection with dimension validation
- **RealUnitedScalarController**: Unit-aware numeric entry with conversion

## Controlled Widgets

Specialized Qt widgets that prevent accidental feedback loops:

- **ControlledCheckBox**: Checkbox with controlled state management
- **ControlledLineEdit**: Line edit with controlled text management
- **ControlledComboBox**: ComboBox with controlled selection management
- **ControlledSlider**: Slider with controlled value management
- **ControlledRangeSlider**: Range slider with controlled span management
- **ControlledListWidget**: List widget with controlled selection management
- **ControlledRadioButton**: Radio button with controlled state management
- **ControlledQLabel**: Label with controlled text management

## Usage Example

```python
from integrated_widgets.core import CheckBoxController
from nexpy import XValue

# Create observable
enabled = XValue( True)

# Create controller directly
controller = CheckBoxController(
    value_or_hook_or_observable=enabled,
    text="Enable Feature"
)

# Access the widget
checkbox_widget = controller.widget_check_box
layout.addWidget(checkbox_widget)

# Clean up
controller.dispose()
```

## Advanced Features

- **Debounced Input**: Configurable debouncing for smooth user experience
- **Validation Support**: Built-in validation with error handling
- **Thread Safety**: Qt signal/slot mechanism with queued connections
- **Lifecycle Management**: Proper initialization and cleanup
- **Feedback Prevention**: Internal update contexts prevent infinite loops

## When to Use Core Components

Use core components when you need:

- **Custom Widget Behavior**: Modify controller logic or add new features
- **Performance Optimization**: Direct control over update mechanisms
- **Integration**: Connect with existing Qt applications
- **Advanced Layouts**: Custom widget composition and styling

For most use cases, prefer the high-level IQT widgets from the main package.
"""

from ._version import __version__

# Base classes
from .controllers.core.base_composite_controller import BaseCompositeController as BaseComplexHookController
from .controllers.core.base_singleton_controller import BaseSingletonController as BaseSingleHookController
from .controllers.core.base_controller import BaseController
from .auxiliaries.default import get_default_debounce_ms
DEFAULT_DEBOUNCE_MS = get_default_debounce_ms()

from .controllers.composite.real_united_scalar_controller import RealUnitedScalarController
from .controllers.composite.unit_combo_box_controller import UnitComboBoxController
from .controllers.composite.single_set_select_controller import SingleSetSelectController
from .controllers.composite.single_set_optional_select_controller import SingleSetOptionalSelectController
from .controllers.composite.double_set_select_controller import DoubleSetSelectController
from .controllers.composite.range_slider_controller import RangeSliderController
from .controllers.singleton.display_value_controller import DisplayValueController
from .controllers.singleton.check_box_controller import CheckBoxController
from .controllers.singleton.integer_entry_controller import IntegerEntryController
from .controllers.singleton.float_entry_controller import FloatEntryController
from .controllers.singleton.text_entry_controller import TextEntryController
from .controllers.singleton.optional_text_entry_controller import OptionalTextEntryController
from .controllers.singleton.path_selector_controller import PathSelectorController

# IQT Widgets with payload-driven layouts
from .iqt_widgets.core.iqt_layouted_widget import IQtLayoutedWidget
from .iqt_widgets.core.layout_strategy_base import LayoutStrategyBase
from .iqt_widgets.core.layout_payload_base import LayoutPayloadBase

# Controlled Widgets
from .controlled_widgets.controlled_line_edit import ControlledLineEdit
from .controlled_widgets.controlled_check_box import ControlledCheckBox
from .controlled_widgets.controlled_combobox import ControlledComboBox
from .controlled_widgets.controlled_qlabel import ControlledQLabel
from .controlled_widgets.controlled_radio_button_group import ControlledRadioButtonGroup
from .controlled_widgets.controlled_editable_combobox import ControlledEditableComboBox
from .controlled_widgets.controlled_range_slider import ControlledRangeSlider
from .controlled_widgets.controlled_slider import ControlledSlider
from .controlled_widgets.controlled_list_widget import ControlledListWidget
from .controlled_widgets.blankable_widget import BlankableWidget

__all__ = [
    "__version__",
    
    # Constants
    "DEFAULT_DEBOUNCE_MS",
    
    # Base classes
    "BaseController",
    "BaseComplexHookController",
    "BaseSingleHookController",
    
    # Widget Singleton Controllers
    "DisplayValueController",
    "CheckBoxController",
    "IntegerEntryController",
    "FloatEntryController",
    "TextEntryController",
    "OptionalTextEntryController",
    "PathSelectorController",

    # Widget Composite Controllers
    "SingleSetSelectController",
    "RealUnitedScalarController",
    "UnitComboBoxController",
    "SingleSetOptionalSelectController",
    "DoubleSetSelectController",
    "RangeSliderController",
    
    # Controlled Widgets
    "ControlledLineEdit",
    "ControlledCheckBox",
    "ControlledComboBox",
    "ControlledQLabel",
    "ControlledRadioButtonGroup",
    "ControlledEditableComboBox",
    "ControlledRangeSlider",
    "ControlledSlider",
    "ControlledListWidget",
    "BlankableWidget",

    # Widgets with payload-driven layouts
    "IQtLayoutedWidget",
    "LayoutStrategyBase",
    "LayoutPayloadBase",
]

