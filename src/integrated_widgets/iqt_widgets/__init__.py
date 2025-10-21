"""IQT Widgets - High-level PySide6/Qt Widgets with Reactive Data Binding

This module contains the IQT (Integrated Qt) widgets - high-level, ready-to-use widgets
that provide automatic bidirectional data binding with observables and hooks.

## What are IQT Widgets?

IQT Widgets are high-level PySide6/Qt widgets that combine Qt UI components with reactive
data binding. They provide:

- **Automatic bidirectional synchronization** with observables and hooks
- **Hook-based architecture** for flexible data connections
- **Layout strategies** for customizable widget composition
- **Unit awareness** for physical quantities via `united_system`
- **Built-in validation** and error handling
- **Clean disposal** and resource management

## Key Features

1. **Hook System**: Connect to observables, hooks, or use plain values
2. **Layout Flexibility**: Customize how widgets are arranged using layout strategies
3. **Type Safety**: Full type hints for better IDE support and fewer runtime errors
4. **Observable Integration**: Works seamlessly with the `observables` library
5. **Unit System Integration**: Handles physical units via `united_system`
6. **Automatic Cleanup**: Proper resource disposal and lifecycle management

## Available Widgets

### Input Widgets
- **IQtCheckBox**: Boolean checkbox with label
- **IQtFloatEntry**: Floating-point number entry with validation
- **IQtIntegerEntry**: Integer number entry with validation
- **IQtTextEntry**: Single-line text input
- **IQtOptionalTextEntry**: Optional text input with clear button

### Selection Widgets
- **IQtRadioButtons**: Exclusive selection from multiple options
- **IQtSelectionOption**: Dropdown selection from options
- **IQtSelectionOptionalOption**: Dropdown with optional "None" selection
- **IQtSingleListSelection**: Single selection from a list
- **IQtDoubleListSelection**: Multiple selection from a list
- **IQtDictOptionalSelection**: Dictionary-based optional selection

### Display Widgets
- **IQtDisplayValue**: Read-only value display with formatting

### File/Path Widgets
- **IQtPathSelector**: File/directory path selection with browse dialog

### Advanced Widgets
- **IQtRangeSlider**: Two-handle range slider with value displays
- **IQtUnitComboBox**: Unit selection with dimension validation
- **IQtRealUnitedScalar**: Full unit-aware numeric entry with unit conversion

## Quick Start

```python
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from nexpy import XValue
from integrated_widgets.iqt_widgets import IQtCheckBox, IQtFloatEntry, IQtSelectionOption

app = QApplication([])
window = QWidget()
layout = QVBoxLayout(window)

# Create observables
enabled = XValue( True)
distance = XValue( 42.5)
fruit = XValue( "apple")
fruits = XValue( {"apple", "banana", "cherry"})

# Create IQT widgets - they stay in sync automatically
layout.addWidget(IQtCheckBox(enabled, text="Enable Feature"))
layout.addWidget(IQtFloatEntry(distance))
layout.addWidget(IQtSelectionOption(fruit, fruits))

window.show()
app.exec()
```

## Hook System

IQT widgets expose **hooks** for data binding. Hooks are named connection points that can be accessed via the widget:

```python
checkbox = IQtCheckBox(initial_value=True, text="Enable")

# Get hook for the value
value_hook = checkbox.get_hook("value")

# Connect to another observable
other_observable = XValue( False)
value_hook.connect_to_target(other_observable.get_hook("value"))

# Now they stay in sync!
```

## Layout Strategies

Define custom layouts for widgets:

```python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

def labeled_layout(parent: QWidget, payload) -> QWidget:
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(QLabel("Current Status:"))
    layout.addWidget(payload.label)
    return widget

status = XValue( "Ready")
display = IQtDisplayValue(
    status,
    formatter=lambda x: f"✓ {x}" if x == "Ready" else f"⚠ {x}",
    layout_strategy=labeled_layout
)
```

## Demo Applications

Explore the comprehensive demo suite:

```bash
# Featured demos - try these first!
python demos/demo_range_slider.py        # 🎚️ Dynamic range slider
python demos/demo_real_united_scalar.py  # 🔬 Unit-aware numeric entry

# Complete demo list
python demos/demo_check_box.py
python demos/demo_float_entry.py
python demos/demo_selection_option.py
# ... and many more!
```

## Architecture

IQT widgets are built on top of the three-layer architecture:

1. **IQT Widgets** (This module) - High-level API with layout strategies
2. **Controllers** - Manage bidirectional data binding
3. **Controlled Widgets** - Specialized Qt widgets with feedback prevention

## Thread Safety

All widgets use Qt's signal/slot mechanism with queued connections to ensure thread-safe updates from nexpy to widgets.

## Lifecycle Management

IQT widgets automatically manage their lifecycle:

1. **Initialization**: Creates controller, sets up data bindings
2. **Active**: Bidirectional updates between observables and widgets
3. **Disposal**: Clean disconnection, observers removed, resources freed

## Contributing

This library is in active development. See the main package documentation for contribution guidelines.
"""

# Import all IQT widgets for easy access
from .iqt_check_box import IQtCheckBox
from .iqt_display_value import IQtDisplayValue
from .iqt_double_list_selection import IQtDoubleListSelection
from .iqt_float_entry import IQtFloatEntry
from .iqt_integer_entry import IQtIntegerEntry
from .iqt_optional_text_entry import IQtOptionalTextEntry
from .iqt_path_selector import IQtPathSelector
from .iqt_radio_buttons import IQtRadioButtons
from .iqt_range_slider import IQtRangeSlider
from .iqt_real_united_scalar import IQtRealUnitedScalar
from .iqt_selection_optional_option import IQtSelectionOptionalOption
from .iqt_selection_option import IQtSelectionOption
from .iqt_single_list_selection import IQtSingleListSelection
from .iqt_dict_optional_selection import IQtDictOptionalSelection
from .iqt_text_entry import IQtTextEntry
from .iqt_unit_combo_box import IQtUnitComboBox

__all__ = [
    # Input widgets
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
    "IQtDictOptionalSelection",
    
    # File/path widgets
    "IQtPathSelector",
    
    # Advanced widgets
    "IQtRangeSlider",
    "IQtUnitComboBox",
    "IQtRealUnitedScalar",
]
