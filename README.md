# Integrated Widgets

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/babrandes/integrated-widgets)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-in%20development-orange.svg)](https://github.com/babrandes/integrated-widgets)

> **⚠️ Development Status**: This library is currently in active development and is **NOT production-ready**. The API may change without notice, and there may be bugs or incomplete features. Use in production environments at your own risk.

A PySide6/Qt widget framework that integrates with `nexpys` and `united_system` to create reactive, unit-aware UI components with bidirectional data binding.

## 🎯 Featured Demos

### 🎚️ Dynamic Range Slider
Interactive range slider with real-time value updates and customizable bounds.

```bash
python demos/demo_range_slider.py
```

**Features:**
- Two-handle range selection
- Real-time value display
- Configurable range bounds
- Smooth dragging experience
- Observable synchronization

### 🔬 Real United Scalar Widget
Advanced unit-aware numeric entry with automatic unit conversion.

```bash
python demos/demo_real_united_scalar.py
```

**Features:**
- Physical unit support (length, mass, time, etc.)
- Automatic unit conversion
- Dimension validation
- Real-time unit switching
- Scientific notation support

## Quick Start

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

# Create IQT widgets - they stay in sync with nexpys automatically
layout.addWidget(IQtCheckBox(enabled, text="Enable Feature"))
layout.addWidget(IQtFloatEntry(distance))
layout.addWidget(IQtSelectionOption(fruit, fruits))

window.show()
app.exec()
```

## What are IQT Widgets?

**IQT (Integrated Qt) Widgets** are high-level, ready-to-use widgets that combine Qt UI components with reactive data binding. They provide:

- **Automatic bidirectional synchronization** with nexpys and hooks
- **Hook-based architecture** for flexible data connections
- **Layout strategies** for customizable widget composition
- **Unit awareness** for physical quantities
- **Built-in validation** and error handling
- **Clean disposal** and resource management

### Key Features

1. **Hook System**: Connect to nexpys, hooks, or use plain values
2. **Layout Flexibility**: Customize how widgets are arranged using layout strategies
3. **Type Safety**: Full type hints for better IDE support and fewer runtime errors
4. **Observable Integration**: Works seamlessly with the `nexpys` library
5. **Unit System Integration**: Handles physical units via `united_system`
6. **Automatic Cleanup**: Proper resource disposal and lifecycle management

## Available IQT Widgets

### Input Widgets

- **`IQtCheckBox`**: Boolean checkbox with label
- **`IQtFloatEntry`**: Floating-point number entry with validation
- **`IQtIntegerEntry`**: Integer number entry with validation
- **`IQtTextEntry`**: Single-line text input
- **`IQtOptionalTextEntry`**: Optional text input with clear button

### Selection Widgets

- **`IQtRadioButtons`**: Exclusive selection from multiple options
- **`IQtSelectionOption`**: Dropdown selection from options
- **`IQtSelectionOptionalOption`**: Dropdown with optional "None" selection
- **`IQtSingleListSelection`**: Single selection from a list
- **`IQtDoubleListSelection`**: Multiple selection from a list

### Display Widgets

- **`IQtDisplayValue`**: Read-only value display with formatting

### File/Path Widgets

- **`IQtPathSelector`**: File/directory path selection with browse dialog

### Advanced Widgets

- **`IQtRangeSlider`**: Two-handle range slider with value displays
- **`IQtUnitComboBox`**: Unit selection with dimension validation
- **`IQtRealUnitedScalar`**: Full unit-aware numeric entry with unit conversion

### Layout Widgets

- **`IQtWidgetBase`**: Base widget with customizable layout strategies

## Installation

> **Note**: This library is in development. Installation instructions are provided for testing and development purposes.

### For Development

```bash
pip install -e .[test]
```

### For Production (Not Recommended)

```bash
pip install integrated-widgets
```

**Warning**: This library is not yet stable for production use. APIs may change without notice.

## Usage Examples

### Basic Checkbox

```python
from integrated_widgets import IQtCheckBox
from nexpy import XValue

# Create an nexpy
enabled = XValue("value", True)

# Create widget - automatically syncs with nexpy
checkbox = IQtCheckBox(enabled, text="Enable Feature")
layout.addWidget(checkbox)

# Changes propagate both ways:
enabled.submit_value("value", False)  # Updates checkbox
# User clicking checkbox updates nexpy
```

### Float Entry with Validation

```python
from integrated_widgets import IQtFloatEntry
from nexpy import XValue

temperature = XValue("value", 20.0)

# Add validation
def valid_temp(value: float) -> bool:
    return -273.15 <= value <= 1000.0

entry = IQtFloatEntry(
    temperature,
    validator=valid_temp
)
layout.addWidget(entry)

# Access current value
print(entry.value)  # 20.0
```

### Selection from Options

```python
from integrated_widgets import IQtSelectionOption
from nexpy import XValue

# Create nexpys
selected_fruit = XValue("value", "apple")
available_fruits = XValue("value", {"apple", "banana", "cherry"})

# Create widget
selector = IQtSelectionOption(
    selected_fruit,
    available_fruits,
    formatter=lambda x: x.title()  # Display as "Apple", "Banana", etc.
)
layout.addWidget(selector)

# Add more options dynamically
available_fruits.submit_value("value", {"apple", "banana", "cherry", "date"})
# Widget updates automatically!
```

### Display Value with Custom Formatting

```python
from integrated_widgets import IQtDisplayValue
from nexpy import XValue
from united_system import RealUnitedScalar, Unit

# Create nexpy for temperature
temperature = XValue(RealUnitedScalar(20.0, Unit("°C")))

# Easy connect with custom formatter
display = IQtDisplayValue(
    temperature,
    formatter=lambda x: f"{x.value():.1f} {x.unit}"
)
layout.addWidget(display)

# Widget automatically updates when temperature changes
temperature.value = RealUnitedScalar(25.0, Unit("°C"))  # Display updates to "25.0 °C"

# Use simplified submit method
display.submit(RealUnitedScalar(30.0, Unit("°C")))  # Clean API
# Instead of: display.submit_value("value", RealUnitedScalar(30.0, Unit("°C")))

# Or use the property
display.value = RealUnitedScalar(22.5, Unit("°C"))
```

With custom layout:

```python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

# Define custom layout strategy
def labeled_layout(parent, payload):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(QLabel("Current Status:"))
    layout.addWidget(payload.label)
    return widget

# Use custom layout
status = XValue("Ready")
display = IQtDisplayValue(
    status,
    formatter=lambda x: f"✓ {x}" if x == "Ready" else f"⚠ {x}",
    layout_strategy=labeled_layout
)
layout.addWidget(display)
```

### Unit-Aware Numeric Entry

```python
from integrated_widgets import IQtRealUnitedScalar
from united_system import RealUnitedScalar, Unit, Dimension
from nexpy import XValue

# Create nexpy with a united value
distance = XValue("value", RealUnitedScalar(100.0, Unit("m")))

# Define available units
unit_options = {
    Dimension("L"): {Unit("m"), Unit("km"), Unit("cm"), Unit("mm")}
}
units_nexpy = XValue("value", unit_options)

# Create widget
widget = IQtRealUnitedScalar(
    value=distance,
    display_unit_options=units_nexpy
)
layout.addWidget(widget)

# User can type "5.2 km" and it will be converted and validated
# Access the value
print(widget.value)  # RealUnitedScalar(5200.0, Unit("m"))
```

### Range Slider

```python
from integrated_widgets import IQtRangeSlider
from nexpy import XValue

# Define range bounds
range_lower = XValue("value", 0.0)
range_upper = XValue("value", 100.0)

# Define selected span
span_lower = XValue("value", 20.0)
span_upper = XValue("value", 80.0)

# Create widget
slider = IQtRangeSlider(
    number_of_ticks=100,
    span_lower_relative_value=span_lower,
    span_upper_relative_value=span_upper,
    range_lower_value=range_lower,
    range_upper_value=range_upper
)
layout.addWidget(slider)

# User can drag handles or the center span
# All values stay synchronized with nexpys
```

### Custom Layout Strategy

```python
from PySide6.QtWidgets import QWidget, QHBoxLayout
from integrated_widgets import IQtFloatEntry
from integrated_widgets.iqt_widgets.iqt_float_entry import Controller_LayoutStrategy, Controller_Payload

# Define custom layout
class HorizontalLayout(Controller_LayoutStrategy):
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(payload.line_edit)
        # Add custom widgets, styling, etc.
        return widget

# Use custom layout
entry = IQtFloatEntry(
    value_nexpy,
    layout_strategy=HorizontalLayout()
)
```

## Hook System

IQT widgets expose **hooks** for data binding. Hooks are named connection points that can be accessed via the widget:

```python
checkbox = IQtCheckBox(initial_value=True, text="Enable")

# Get hook for the value
value_hook = checkbox.get_hook("value")

# Connect to another nexpy
other_nexpy = XValue("value", False)
value_hook.connect_to_target(other_nexpy.get_hook("value"))

# Now they stay in sync!
```

### Available Hooks by Widget

Each widget documents its available hooks:

```python
# IQtCheckBox
# - "value": bool - the checked state
# - "enabled": bool - whether the widget is enabled

# IQtFloatEntry  
# - "value": float - the numeric value
# - "enabled": bool - whether the widget is enabled

# IQtSelectionOption
# - "selected_option": T - the currently selected item
# - "available_options": set[T] - the set of available items
```

## Advanced Features

### Working with Plain Values

IQT widgets don't require nexpys - you can use plain values:

```python
# Use a plain value
checkbox = IQtCheckBox(True, text="Enabled")

# Later, connect to an nexpy
checkbox.get_hook("value").connect_to_target(nexpy.get_hook("value"))
```

### Accessing Widget Components

For advanced customization, access the underlying controller and its widgets:

```python
entry = IQtFloatEntry(value_nexpy)

# Access the controller
controller = entry.controller

# Access specific widget components via the controller
line_edit = controller.widget_line_edit
line_edit.setStyleSheet("background-color: yellow;")
```

### Disposing Widgets

IQT widgets handle cleanup automatically, but you can manually dispose when needed:

```python
widget = IQtCheckBox(value_nexpy)

# ... use the widget ...

# Clean up
widget.dispose()
```

## Advanced Usage: Controllers

For full control over widget behavior and layout, you can use the underlying **Controllers** directly. Controllers manage the bidirectional binding between nexpys and Qt widgets.

### Controller Architecture

Controllers sit between your application logic (nexpys) and the UI (Qt widgets). They:

- Subscribe to nexpys and update widgets when data changes
- Listen to widget signals and update nexpys when users interact
- Prevent feedback loops through internal update contexts
- Manage lifecycle and proper cleanup
- Provide debounced input handling for smooth user experience

**Base Classes:**
- `BaseController`: Abstract base for all controllers
- `BaseSingleHookController`: For controllers managing a single nexpy
- `BaseComplexHookController`: For controllers managing multiple nexpys

### Using Controllers Directly

```python
from integrated_widgets.controllers.singleton.check_box_controller import CheckBoxController
from nexpy import XValue

# Create nexpy
enabled = XValue("value", True)

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

Subclass `BaseSingleHookController` or `BaseComplexHookController`:

```python
from integrated_widgets.controllers.core.base_singleton_controller import BaseSingletonController
from PySide6.QtWidgets import QSpinBox

class SpinBoxController(BaseSingletonController):
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
        self._submit_values_debounced(new_value)
    
    @property
    def widget_spin_box(self) -> QSpinBox:
        return self._spin_box
```

## Configuration

### Debounce Timing

The library provides configurable debouncing for user input:

```python
import integrated_widgets

# Set global debounce timing (default: 100ms)
integrated_widgets.DEFAULT_DEBOUNCE_MS = 250

# Or configure per-widget
entry = IQtFloatEntry(
    value_nexpy,
    debounce_ms=50  # Faster response
)
```

## 🚀 Demo Applications

Explore the comprehensive demo suite to see all widgets in action:

### 🎯 Featured Demos (Try These First!)

```bash
cd demos

# 🎚️ Dynamic Range Slider - Interactive range selection
python demo_range_slider.py

# 🔬 Real United Scalar - Unit-aware numeric entry
python demo_real_united_scalar.py
```

### 📋 Complete Demo List

#### Basic Input Widgets
```bash
python demo_check_box.py          # Boolean checkbox with label
python demo_float_entry.py        # Floating-point number entry
python demo_integer_entry.py      # Integer number entry
python demo_text_entry.py         # Single-line text input
```

#### Selection Widgets
```bash
python demo_radio_buttons.py                    # Exclusive selection buttons
python demo_selection_option.py                 # Dropdown selection
python demo_selection_optional_option.py        # Optional dropdown selection
python demo_single_list_selection.py           # Single list selection
python demo_dict_optional_selection.py          # Dictionary-based optional selection
```

#### Advanced Widgets
```bash
python demo_range_slider.py        # 🎚️ Dynamic range slider (FEATURED)
python demo_unit_combo_box.py      # Unit selection with validation
python demo_real_united_scalar.py  # 🔬 Unit-aware numeric entry (FEATURED)
```

#### Display Widgets
```bash
python demo_display_value.py       # Read-only value display with formatting
```

### 🎮 Interactive Features

Each demo showcases:
- **Real-time updates** between nexpys and widgets
- **Bidirectional data binding** - changes propagate both ways
- **Unit conversion** (where applicable)
- **Validation and error handling**
- **Custom formatting and styling**
- **Dynamic option updates**

### 🏃‍♂️ Quick Demo Tour

```bash
# Run all demos in sequence
cd demos
for demo in *.py; do
    echo "🎬 Running $demo..."
    python "$demo"
    echo "Press Enter to continue..."
    read
done
```

## Testing

Run the comprehensive test suite with enhanced visualization:

```bash
# Run all tests with progress visualization
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py tests/controller_tests/
python tests/run_tests.py tests/iqt_widget_tests/

# Run individual test files
python tests/run_tests.py tests/controller_tests/test_check_box_controller.py
```

The test runner provides:
- **📊 Progress visualization** with dots and percentages
- **🎯 Real-time status** updates as tests run
- **📈 Comprehensive summary** with timing and success rates
- **🔍 Detailed reporting** for failed tests

## Architecture Details

### Three-Layer Architecture

1. **IQT Widgets** (High-level API)
   - Ready-to-use widgets with layout strategies
   - Simple API accepting values, hooks, or nexpys
   - Flexible composition and customization

2. **Controllers** (Mid-level API)
   - Manage bidirectional data binding
   - Handle lifecycle and cleanup
   - Provide debouncing and validation

3. **Controlled Widgets** (Low-level API)
   - Specialized Qt widgets
   - Prevent accidental feedback loops
   - Block direct programmatic modification

### Thread Safety

All widgets use Qt's signal/slot mechanism with queued connections to ensure thread-safe updates from nexpys to widgets. Observable changes from any thread are safely marshaled to the Qt GUI thread.

### Lifecycle Management

IQT widgets automatically manage their lifecycle:

1. **Initialization**: Creates controller, sets up data bindings
2. **Active**: Bidirectional updates between nexpys and widgets
3. **Disposal**: Clean disconnection, observers removed, resources freed

### Preventing Feedback Loops

The internal update mechanism prevents infinite loops when programmatic changes trigger signal emissions that would trigger more changes.

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Complete Documentation](docs/README.md)** - Comprehensive guide with API reference
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Deep dive into the three-layer design
- **[Demo Guide](docs/DEMO_GUIDE.md)** - Step-by-step demo walkthrough

### Quick Links

- **🎯 [Featured Demos](docs/DEMO_GUIDE.md#featured-demos)** - Start here to see the best features
- **🏗️ [Architecture Overview](docs/ARCHITECTURE.md#overview)** - Understand the design
- **📖 [API Reference](docs/README.md#api-reference)** - Complete API documentation
- **🧪 [Testing Guide](docs/README.md#testing)** - Run and understand tests

## Contributing

**Note**: This library is in active development. Contributions are welcome, but be aware that significant API changes may occur.

When contributing, please:

1. **Add tests** for new widgets/controllers
2. **Update documentation** in `docs/` directory
3. **Follow existing code style** and patterns
4. **Ensure all tests pass** with `python tests/run_tests.py`
5. **Be prepared for API changes** during the development phase

### Development Setup

```bash
# Clone and install
git clone <repository-url>
cd integrated-widgets
pip install -e .[test]

# Run tests
python tests/run_tests.py

# Run demos
cd demos
python demo_range_slider.py
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

## Imports and Organization

### Typical Usage (Widgets)
Most users will only need top-level widget imports:

```python
from integrated_widgets import IQtCheckBox, IQtTextEntry, IQtFloatEntry, ... # Etc.
```

### Custom Layouts/Widget Composition (Payloads)
To compose widgets or customize layouts, use payloads (structure descriptors for controller widgets):

```python
from integrated_widgets.payloads import CheckBoxPayload, TextEntryPayload, ...
```

### Advanced/Core API
For building custom containers, advanced composition, or custom layouting:

```python
from integrated_widgets.core import (
    IQtControllerWidgetBase,
    IQtWidgetBase,
    default,  # System-wide utility
    DEFAULT_DEBOUNCE_MS,
    LayoutStrategyBase,
    LayoutPayloadBase,
)
```

### Signal Hooks
The `IQtSignalHook` can be imported directly from the main package for integrating with other Qt or observable systems:

```python
from integrated_widgets import IQtSignalHook
```
