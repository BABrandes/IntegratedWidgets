# Integrated Widgets Documentation

A comprehensive PySide6/Qt widget framework that integrates with `nexpys` and `united_system` to create reactive, unit-aware UI components with bidirectional data binding.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [IQT Widgets](#iqt-widgets)
- [Controllers](#controllers)
- [Demos](#demos)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)
- [Contributing](#contributing)

## Overview

Integrated Widgets provides a three-layer architecture for building reactive Qt applications:

1. **IQT Widgets** - High-level, ready-to-use widgets with automatic data binding
2. **Controllers** - Mid-level components managing bidirectional synchronization
3. **Controlled Widgets** - Low-level Qt widgets with feedback loop prevention

### Key Features

- **🔄 Reactive Data Binding**: Automatic bidirectional synchronization with nexpys
- **📏 Unit Awareness**: Built-in support for physical units and dimensions
- **🎨 Flexible Layouts**: Customizable layout strategies for widget composition
- **⚡ Debounced Input**: Smooth user experience with configurable debouncing
- **🛡️ Type Safety**: Full type hints and validation support
- **🧹 Clean Lifecycle**: Automatic resource management and cleanup
- **🔗 Hook System**: Flexible connection points for data binding

## Quick Start

### Installation

```bash
# For development
pip install -e .[test]

# For production (not recommended - library is in development)
pip install integrated-widgets
```

### Basic Usage

```python
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from nexpy import XValue
from integrated_widgets import IQtCheckBox, IQtFloatEntry, IQtSelectionOption

app = QApplication([])
window = QWidget()
layout = QVBoxLayout(window)

# Create nexpys
enabled = XValue(True)
distance = XValue(42.5)
fruit = XValue("apple")
fruits = XValue({"apple", "banana", "cherry"})

# Create IQT widgets - they stay in sync automatically
layout.addWidget(IQtCheckBox(enabled, text="Enable Feature"))
layout.addWidget(IQtFloatEntry(distance))
layout.addWidget(IQtSelectionOption(fruit, fruits))

window.show()
app.exec()
```

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────┐
│           IQT Widgets                    │  ← High-level API
│  (Ready-to-use, layout strategies)      │
├─────────────────────────────────────────┤
│           Controllers                    │  ← Mid-level API
│  (Bidirectional binding, lifecycle)      │
├─────────────────────────────────────────┤
│        Controlled Widgets               │  ← Low-level API
│  (Qt widgets, feedback prevention)      │
└─────────────────────────────────────────┘
```

### Data Flow

```
Observable ←→ Controller ←→ Qt Widget
     ↑              ↑           ↑
   Interface      Interface    Display
     ↓              ↓           Layer
    ┌─────────────┐
    │    Nexus    │
    │(Shared Data)│
    └─────────────┘
```

## IQT Widgets

### Input Widgets

#### IQtCheckBox
Boolean checkbox with label support.

```python
from integrated_widgets import IQtCheckBox
from nexpy import XValue

enabled = XValue( True)
checkbox = IQtCheckBox(enabled, text="Enable Feature")
```

**Hooks:**
- `value`: bool - The checked state
- `enabled`: bool - Whether the widget is enabled

#### IQtFloatEntry
Floating-point number entry with validation.

```python
from integrated_widgets import IQtFloatEntry

temperature = XValue( 20.0)

def valid_temp(value: float) -> bool:
    return -273.15 <= value <= 1000.0

entry = IQtFloatEntry(temperature, validator=valid_temp)
```

**Hooks:**
- `value`: float - The numeric value
- `enabled`: bool - Whether the widget is enabled

#### IQtIntegerEntry
Integer number entry with validation.

```python
from integrated_widgets import IQtIntegerEntry

count = XValue( 42)
entry = IQtIntegerEntry(count, validator=lambda x: x >= 0)
```

#### IQtTextEntry
Single-line text input with optional validation.

```python
from integrated_widgets import IQtTextEntry

name = XValue( "John Doe")
entry = IQtTextEntry(name, strip_whitespace=True)
```

#### IQtOptionalTextEntry
Optional text input with clear button.

```python
from integrated_widgets import IQtOptionalTextEntry

description = XValue( None)
entry = IQtOptionalTextEntry(description, placeholder="Enter description...")
```

### Selection Widgets

#### IQtRadioButtons
Exclusive selection from multiple options.

```python
from integrated_widgets import IQtRadioButtons

selected_color = XValue( "red")
colors = XValue( {"red", "green", "blue"})

radio = IQtRadioButtons(selected_color, colors, formatter=lambda x: x.title())
```

#### IQtSelectionOption
Dropdown selection from options.

```python
from integrated_widgets import IQtSelectionOption

selected_fruit = XValue( "apple")
available_fruits = XValue( {"apple", "banana", "cherry"})

selector = IQtSelectionOption(selected_fruit, available_fruits)
```

#### IQtSelectionOptionalOption
Dropdown with optional "None" selection.

```python
from integrated_widgets import IQtSelectionOptionalOption

selected_size = XValue( None)
sizes = XValue( {"S", "M", "L", "XL"})

selector = IQtSelectionOptionalOption(
    selected_size, 
    sizes, 
    none_option_text="No size selected"
)
```

#### IQtSingleListSelection
Single selection from a list with custom formatting.

```python
from integrated_widgets import IQtSingleListSelection

selected_item = XValue( "item1")
available_items = XValue( {"item1", "item2", "item3"})

list_selector = IQtSingleListSelection(
    selected_item, 
    available_items,
    formatter=lambda x: f"Item: {x.upper()}"
)
```

#### IQtDoubleListSelection
Multiple selection from a list.

```python
from integrated_widgets import IQtDoubleListSelection

selected_items = XValue( {"item1"})
available_items = XValue( {"item1", "item2", "item3"})

multi_selector = IQtDoubleListSelection(selected_items, available_items)
```

### Display Widgets

#### IQtDisplayValue
Read-only value display with custom formatting.

```python
from integrated_widgets import IQtDisplayValue
from united_system import RealUnitedScalar, Unit

temperature = XValue( RealUnitedScalar(20.0, Unit("°C")))

display = IQtDisplayValue(
    temperature,
    formatter=lambda x: f"{x.value():.1f} {x.unit}"
)
```

**Hooks:**
- `value`: T - The displayed value

### File/Path Widgets

#### IQtPathSelector
File/directory path selection with browse dialog.

```python
from integrated_widgets import IQtPathSelector
from pathlib import Path

file_path = XValue( None)

selector = IQtPathSelector(
    file_path,
    mode="file",
    dialog_title="Select File",
    allowed_extensions=["*.txt", "*.py"]
)
```

**Hooks:**
- `path`: Path | None - The selected file/directory path

### Advanced Widgets

#### IQtRangeSlider
Two-handle range slider with value displays.

```python
from integrated_widgets import IQtRangeSlider

# Define range bounds
range_lower = XValue( 0.0)
range_upper = XValue( 100.0)

# Define selected span
span_lower = XValue( 20.0)
span_upper = XValue( 80.0)

slider = IQtRangeSlider(
    number_of_ticks=100,
    span_lower_relative_value=span_lower,
    span_upper_relative_value=span_upper,
    range_lower_value=range_lower,
    range_upper_value=range_upper
)
```

**Hooks:**
- `span_lower_relative_value`: float - Lower bound of selected range
- `span_upper_relative_value`: float - Upper bound of selected range
- `range_lower_value`: float - Lower bound of total range
- `range_upper_value`: float - Upper bound of total range

#### IQtUnitComboBox
Unit selection with dimension validation.

```python
from integrated_widgets import IQtUnitComboBox
from united_system import Unit, Dimension

selected_unit = XValue( Unit("m"))
available_units = XValue( {
    Dimension("L"): {Unit("m"), Unit("km"), Unit("cm")}
})

unit_selector = IQtUnitComboBox(selected_unit, available_units)
```

**Hooks:**
- `selected_unit`: Unit | None - The selected unit
- `available_units`: dict[Dimension, set[Unit]] - Available units by dimension

#### IQtRealUnitedScalar
Full unit-aware numeric entry with unit conversion.

```python
from integrated_widgets import IQtRealUnitedScalar
from united_system import RealUnitedScalar, Unit, Dimension

# Create nexpy with a united value
distance = XValue( RealUnitedScalar(100.0, Unit("m")))

# Define available units
unit_options = {
    Dimension("L"): {Unit("m"), Unit("km"), Unit("cm"), Unit("mm")}
}
units_nexpy = XValue( unit_options)

widget = IQtRealUnitedScalar(
    value=distance,
    display_unit_options=units_nexpy
)
```

**Hooks:**
- `value`: RealUnitedScalar - The unit-aware numeric value
- `display_unit_options`: dict[Dimension, set[Unit]] - Available units for display

### Layout Widgets

#### IQtLayoutedWidget
Base widget with customizable layout strategies.

```python
from integrated_widgets import IQtLayoutedWidget
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

def custom_layout(parent: QWidget, payload) -> QWidget:
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(QLabel("Status:"))
    layout.addWidget(payload.label)
    return widget

status = XValue( "Ready")
display = IQtLayoutedWidget(
    status,
    layout_strategy=custom_layout
)
```

## Controllers

Controllers manage the bidirectional binding between nexpys and Qt widgets. They provide:

- **Data Synchronization**: Automatic updates between nexpys and widgets
- **Signal Handling**: Qt signal processing and nexpy updates
- **Lifecycle Management**: Proper initialization and cleanup
- **Debouncing**: Configurable input debouncing for smooth UX
- **Validation**: Built-in validation support
- **Feedback Prevention**: Internal update contexts prevent infinite loops

### Base Controller Classes

#### BaseController
Abstract base class for all controllers.

```python
from integrated_widgets.util.base_controller import BaseController

class MyController(BaseController):
    def __init__(self, value: XValue, **kwargs):
        super().__init__(nexus_manager=nexus_manager, **kwargs)
        # Initialize your controller
```

#### BaseSingleHookController
For controllers managing a single nexpy.

```python
from integrated_widgets.util.base_single_hook_controller import BaseSingleHookController

class MySingleController(BaseSingleHookController):
    def __init__(self, value: XValue, **kwargs):
        super().__init__(hook_source=value, **kwargs)
```

#### BaseComplexHookController
For controllers managing multiple nexpys.

```python
from integrated_widgets.util.base_complex_hook_controller import BaseComplexHookController

class MyComplexController(BaseComplexHookController):
    def __init__(self, values: dict, **kwargs):
        super().__init__(initial_component_values=values, **kwargs)
```

### Using Controllers Directly

```python
from integrated_widgets.controllers import CheckBoxController
from nexpy import XValue

# Create nexpy
enabled = XValue( True)

# Create controller directly
controller = CheckBoxController(
    value_or_hook_or_nexpy=enabled,
    text="Enable Feature"
)

# Access the widget
checkbox_widget = controller.widget_check_box
layout.addWidget(checkbox_widget)

# Clean up
controller.dispose()
```

### Creating Custom Controllers

```python
from integrated_widgets.util.base_single_hook_controller import BaseSingleHookController
from PySide6.QtWidgets import QSpinBox

class SpinBoxController(BaseSingleHookController):
    def __init__(self, value: XValue[int], **kwargs):
        self._spin_box = QSpinBox()
        
        super().__init__(
            hook_source=value,
            observing_widget=self._spin_box,
            **kwargs
        )
        
        # Connect widget signals
        self._spin_box.valueChanged.connect(self._on_value_changed)
    
    def _invalidate_widgets_impl(self) -> None:
        """Update widget from nexpy"""
        with self._internal_widget_update():
            self._spin_box.setValue(self.get_value())
    
    def _on_value_changed(self, new_value: int) -> None:
        """Update nexpy from widget"""
        self.submit(new_value)
    
    @property
    def widget_spin_box(self) -> QSpinBox:
        return self._spin_box
```

## Demos

The project includes comprehensive demo applications showcasing all widgets and features.

### 🎯 Featured Demos

#### Dynamic Range Slider (`demo_range_slider.py`)
Interactive range slider with real-time value updates and customizable bounds.

**Features:**
- Two-handle range selection
- Real-time value display
- Configurable range bounds
- Smooth dragging experience
- Observable synchronization

```python
# Run the demo
python demos/demo_range_slider.py
```

#### Real United Scalar Widget (`demo_real_united_scalar.py`)
Advanced unit-aware numeric entry with automatic unit conversion.

**Features:**
- Physical unit support (length, mass, time, etc.)
- Automatic unit conversion
- Dimension validation
- Real-time unit switching
- Scientific notation support

```python
# Run the demo
python demos/demo_real_united_scalar.py
```

### 📋 Complete Demo List

#### Basic Widgets
- `demo_check_box.py` - Boolean checkbox with label
- `demo_float_entry.py` - Floating-point number entry
- `demo_integer_entry.py` - Integer number entry
- `demo_text_entry.py` - Single-line text input

#### Selection Widgets
- `demo_radio_buttons.py` - Exclusive selection buttons
- `demo_selection_option.py` - Dropdown selection
- `demo_selection_optional_option.py` - Optional dropdown selection
- `demo_single_list_selection.py` - Single list selection
- `demo_dict_optional_selection.py` - Dictionary-based optional selection

#### Advanced Widgets
- `demo_range_slider.py` - **Featured**: Dynamic range slider
- `demo_unit_combo_box.py` - Unit selection with validation
- `demo_real_united_scalar.py` - **Featured**: Unit-aware numeric entry

#### Display Widgets
- `demo_display_value.py` - Read-only value display with formatting

### 🚀 Running Demos

```bash
# Navigate to the demos folder
cd demos

# Run individual demos
python demo_range_slider.py
python demo_real_united_scalar.py
python demo_check_box.py

# Or run all demos
for demo in *.py; do
    echo "Running $demo..."
    python "$demo"
done
```

## Advanced Features

### Hook System

IQT widgets expose **hooks** for flexible data binding:

```python
checkbox = IQtCheckBox(initial_value=True, text="Enable")

# Get hook for the value
value_hook = checkbox.get_hook("value")

# Connect to another nexpy
other_nexpy = XValue( False)
value_hook.connect_to_target(other_nexpy.get_hook("value"))

# Now they stay in sync!
```

### Custom Layout Strategies

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

### Working with Plain Values

IQT widgets don't require nexpys - you can use plain values:

```python
# Use a plain value
checkbox = IQtCheckBox(True, text="Enabled")

# Later, connect to an nexpy
checkbox.get_hook("value").connect_to_target(nexpy.get_hook("value"))
```

### Debounce Configuration

Configure debouncing for smooth user experience:

```python
# Global configuration
import integrated_widgets
integrated_widgets.DEFAULT_DEBOUNCE_MS = 250

# Per-widget configuration
entry = IQtFloatEntry(
    value_nexpy,
    debounce_ms=50  # Faster response
)
```

### Thread Safety

All widgets use Qt's signal/slot mechanism with queued connections to ensure thread-safe updates from nexpys to widgets.

### Lifecycle Management

IQT widgets automatically manage their lifecycle:

1. **Initialization**: Creates controller, sets up data bindings
2. **Active**: Bidirectional updates between nexpys and widgets
3. **Disposal**: Clean disconnection, observers removed, resources freed

```python
widget = IQtCheckBox(value_nexpy)

# ... use the widget ...

# Clean up (automatic, but can be manual)
widget.dispose()
```

## API Reference

### IQT Widget Classes

#### Input Widgets
- `IQtCheckBox(value, text=None, **kwargs)`
- `IQtFloatEntry(value, validator=None, **kwargs)`
- `IQtIntegerEntry(value, validator=None, **kwargs)`
- `IQtTextEntry(value, validator=None, strip_whitespace=True, **kwargs)`
- `IQtOptionalTextEntry(value, placeholder=None, **kwargs)`

#### Selection Widgets
- `IQtRadioButtons(selected_option, available_options, formatter=None, **kwargs)`
- `IQtSelectionOption(selected_option, available_options, formatter=None, **kwargs)`
- `IQtSelectionOptionalOption(selected_option, available_options, none_option_text="None", **kwargs)`
- `IQtSingleListSelection(selected_option, available_options, formatter=None, **kwargs)`
- `IQtDoubleListSelection(selected_options, available_options, **kwargs)`

#### Display Widgets
- `IQtDisplayValue(value, formatter=None, **kwargs)`

#### File/Path Widgets
- `IQtPathSelector(path, mode="file", dialog_title=None, **kwargs)`

#### Advanced Widgets
- `IQtRangeSlider(span_lower_relative_value, span_upper_relative_value, range_lower_value, range_upper_value, number_of_ticks=100, **kwargs)`
- `IQtUnitComboBox(selected_unit, available_units, **kwargs)`
- `IQtRealUnitedScalar(value, display_unit_options, **kwargs)`

### Common Parameters

All IQT widgets accept these common parameters:

- `debounce_ms: int | None` - Debounce timing in milliseconds
- `layout_strategy: Callable | None` - Custom layout strategy
- `nexus_manager: NexusManager` - Nexus manager for nexpys
- `logger: Logger | None` - Logger instance

### Controller Classes

#### Base Classes
- `BaseController` - Abstract base for all controllers
- `BaseSingleHookController` - For single nexpy controllers
- `BaseComplexHookController` - For multiple nexpy controllers

#### Specific Controllers
- `CheckBoxController` - Checkbox controller
- `FloatEntryController` - Float entry controller
- `IntegerEntryController` - Integer entry controller
- `TextEntryController` - Text entry controller
- `OptionalTextEntryController` - Optional text entry controller
- `RadioButtonController` - Radio button controller
- `SelectionOptionController` - Selection option controller
- `SelectionOptionalOptionController` - Optional selection controller
- `SingleListSelectionController` - Single list selection controller
- `DoubleListSelectionController` - Double list selection controller
- `DisplayValueController` - Display value controller
- `PathSelectorController` - Path selector controller
- `RangeSliderController` - Range slider controller
- `UnitComboBoxController` - Unit combo box controller
- `RealUnitedScalarController` - Real united scalar controller

## Contributing

This library is in active development. Contributions are welcome!

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd integrated-widgets

# Install in development mode
pip install -e .[test]

# Run tests
python tests/run_tests.py

# Run demos
cd demos
python demo_range_slider.py
```

### Guidelines

1. **Add Tests**: New widgets/controllers must have comprehensive tests
2. **Update Documentation**: Keep docs current with API changes
3. **Follow Style**: Use existing code style and patterns
4. **Type Hints**: Provide full type annotations
5. **Handle Errors**: Implement proper error handling and validation

### Testing

The project includes a comprehensive test suite with enhanced visualization:

```bash
# Run all tests with progress visualization
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py tests/controller_tests/
python tests/run_tests.py tests/iqt_widget_tests/

# Run individual test files
python tests/run_tests.py tests/controller_tests/test_check_box_controller.py
```

## License

- **Code**: Apache-2.0 (see `LICENSE`)
- **PySide6**: LGPL-3.0 (see `licenses/` for notices and license copy)

## Dependencies

- **PySide6**: Qt6 Python bindings (>=6.7)
- **nexpys**: Reactive nexpy pattern implementation (>=4.0.2)
- **united-system**: Physical units and dimensions system (>=0.2.2)

## Related Projects

- [nexpys](https://github.com/babrandes/nexpys) - Observable pattern for Python
- [united-system](https://github.com/babrandes/united-system) - Physical units system
