# Integrated Widgets

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/babrandes/integrated-widgets)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-in%20development-orange.svg)](https://github.com/babrandes/integrated-widgets)

> **⚠️ Development Status**: This library is currently in active development and is **NOT production-ready**. The API may change without notice, and there may be bugs or incomplete features. Use in production environments at your own risk.

A PySide6/Qt widget framework that integrates with `observables` and `united_system` to create reactive, unit-aware UI components with bidirectional data binding.

## ✨ Key Features

- **🔄 Reactive Data Binding**: Automatic bidirectional synchronization with observables
- **📏 Unit Awareness**: Built-in support for physical units and automatic conversion
- **🎨 Flexible Layouts**: Customizable layout strategies for widget composition
- **⚡ Debounced Input**: Smooth user experience with configurable debouncing
- **🛡️ Type Safety**: Full type hints and validation support
- **🧹 Clean Lifecycle**: Automatic resource management and cleanup

## 🚀 Quick Start

```python
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from observables import ObservableSingleValue
from integrated_widgets import IQtCheckBox, IQtFloatEntry, IQtSelectionOption

app = QApplication([])
window = QWidget()
layout = QVBoxLayout(window)

# Create observables
enabled = ObservableSingleValue(True)
distance = ObservableSingleValue(42.5)
fruit = ObservableSingleValue("apple")
fruits = ObservableSingleValue({"apple", "banana", "cherry"})

# Create IQT widgets - they stay in sync with observables automatically
layout.addWidget(IQtCheckBox(enabled, text="Enable Feature"))
layout.addWidget(IQtFloatEntry(distance))
layout.addWidget(IQtSelectionOption(fruit, fruits))

window.show()
app.exec()
```

That's it! Changes in observables update widgets, and user interactions update observables. No manual synchronization needed.

## 🎯 Featured Demos

### 🎚️ Dynamic Range Slider
Interactive two-handle range slider with real-time value updates and customizable bounds.

```bash
python demos/demo_range_slider.py
```

**Features**: Two-handle selection • Real-time display • Configurable bounds • Smooth dragging • Observable sync

### 🔬 Real United Scalar Widget
Advanced unit-aware numeric entry with automatic unit conversion and dimension validation.

```bash
python demos/demo_real_united_scalar.py
```

**Features**: Physical unit support • Automatic conversion • Dimension validation • Real-time switching • Scientific notation

### 📋 More Demos

Explore all demos in the `demos/` directory:

```bash
cd demos

# Basic widgets
python demo_check_box.py
python demo_float_entry.py
python demo_text_entry.py

# Selection widgets
python demo_radio_buttons.py
python demo_selection_option.py
python demo_single_list_selection.py
python demo_dict_optional_selection.py

# Display widgets
python demo_display_value.py

# Advanced widgets
python demo_unit_combo_box.py
```

See the **[Demo Guide](docs/DEMO_GUIDE.md)** for detailed walkthroughs.

## 📦 Installation

> **Note**: This library is in development. Installation instructions are provided for testing and development purposes.

### For Development

```bash
git clone <repository-url>
cd integrated-widgets
pip install -e .[test]
```

### For Production (Not Recommended)

```bash
pip install integrated-widgets
```

**Warning**: This library is not yet stable for production use. APIs may change without notice.

## 💡 Usage Examples

### Checkbox with Bidirectional Binding

```python
from integrated_widgets import IQtCheckBox
from observables import ObservableSingleValue

# Create observable
enabled = ObservableSingleValue(True)

# Create widget - automatically syncs
checkbox = IQtCheckBox(enabled, text="Enable Feature")
layout.addWidget(checkbox)

# Changes propagate both ways:
enabled.value = False  # Updates checkbox
# User clicking checkbox updates enabled.value
```

### Float Entry with Validation

```python
from integrated_widgets import IQtFloatEntry
from observables import ObservableSingleValue

temperature = ObservableSingleValue(20.0)

# Add validation
def valid_temp(value: float) -> bool:
    return -273.15 <= value <= 1000.0

entry = IQtFloatEntry(temperature, validator=valid_temp)
layout.addWidget(entry)

# Access current value
print(entry.controller.value)  # 20.0
```

### Selection from Options

```python
from integrated_widgets import IQtSelectionOption
from observables import ObservableSingleValue

# Create observables
selected_fruit = ObservableSingleValue("apple")
available_fruits = ObservableSingleValue({"apple", "banana", "cherry"})

# Create widget
selector = IQtSelectionOption(
    selected_fruit,
    available_fruits,
    formatter=lambda x: x.title()  # Display as "Apple", "Banana", etc.
)
layout.addWidget(selector)

# Add more options dynamically
available_fruits.value = {"apple", "banana", "cherry", "date"}
# Widget updates automatically!
```

### Unit-Aware Numeric Entry

```python
from integrated_widgets import IQtRealUnitedScalar
from united_system import RealUnitedScalar, Unit, Dimension
from observables import ObservableSingleValue

# Create observable with a united value
distance = ObservableSingleValue(RealUnitedScalar(100.0, Unit("m")))

# Define available units
unit_options = {
    Dimension("L"): {Unit("m"), Unit("km"), Unit("cm"), Unit("mm")}
}
units_observable = ObservableSingleValue(unit_options)

# Create widget
widget = IQtRealUnitedScalar(
    value=distance,
    display_unit_options=units_observable
)
layout.addWidget(widget)

# User can type "5.2 km" and it will be converted and validated
print(widget.controller.value)  # RealUnitedScalar(5200.0, Unit("m"))
```

### Display Value with Custom Formatting

```python
from integrated_widgets import IQtDisplayValue
from observables import ObservableSingleValue

status = ObservableSingleValue("Ready")

# Create display with custom formatter
display = IQtDisplayValue(
    status,
    formatter=lambda x: f"✓ {x}" if x == "Ready" else f"⚠ {x}"
)
layout.addWidget(display)

# Widget automatically updates when status changes
status.value = "Error"  # Display updates to "⚠ Error"
```

## 📚 Available Widgets

### Input Widgets
- **`IQtCheckBox`** - Boolean checkbox with label
- **`IQtFloatEntry`** - Floating-point number entry with validation
- **`IQtIntegerEntry`** - Integer number entry with validation
- **`IQtTextEntry`** - Single-line text input
- **`IQtOptionalTextEntry`** - Optional text input with clear button

### Selection Widgets
- **`IQtRadioButtons`** - Exclusive selection from multiple options
- **`IQtSelectionOption`** - Dropdown selection from options
- **`IQtSelectionOptionalOption`** - Dropdown with optional "None" selection
- **`IQtSingleListSelection`** - Single selection from a list
- **`IQtDoubleListSelection`** - Multiple selection from a list
- **`IQtDictOptionalSelection`** - Dictionary-based optional selection

### Display Widgets
- **`IQtDisplayValue`** - Read-only value display with formatting

### File/Path Widgets
- **`IQtPathSelector`** - File/directory path selection with browse dialog

### Advanced Widgets
- **`IQtRangeSlider`** - Two-handle range slider with value displays
- **`IQtUnitComboBox`** - Unit selection with dimension validation
- **`IQtRealUnitedScalar`** - Full unit-aware numeric entry with conversion

See the **[Complete Documentation](docs/README.md)** for detailed API reference.

## 🏗️ Architecture

Integrated Widgets uses a three-layer architecture:

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
        │ (Shared Data)│
        └─────────────┘
```

- **Observable & Controller**: Interface with the Nexus (shared data store)
- **Qt Widget**: Display layer that communicates with the controller
- **Nexus**: Hidden shared state - all connected components stay synchronized

Read more in the **[Architecture Guide](docs/ARCHITECTURE.md)**.

## 🧪 Testing

Run the comprehensive test suite with enhanced visualization:

```bash
# Run all tests with progress visualization
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py tests/controller_tests/

# Run individual test files
python tests/run_tests.py tests/controller_tests/test_check_box_controller.py
```

The test runner provides:
- 📊 Progress visualization with dots (`.` = pass, `F` = fail)
- 🎯 Real-time status updates
- 📈 Comprehensive summary with timing and success rates

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Complete Documentation](docs/README.md)** - Full API reference and usage guide
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Deep dive into the three-layer design
- **[Demo Guide](docs/DEMO_GUIDE.md)** - Step-by-step demo walkthrough

### Quick Links

- 🎯 **[Featured Demos](docs/DEMO_GUIDE.md#featured-demos)** - Start here!
- 🏗️ **[Architecture Overview](docs/ARCHITECTURE.md#overview)** - Understand the design
- 📖 **[API Reference](docs/README.md#iqt-widgets)** - Complete widget documentation
- 🧪 **[Testing Guide](docs/README.md#testing)** - Run and understand tests

## 🤝 Contributing

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

## 📄 License

- **Code**: Apache-2.0 (see `LICENSE`)
- **PySide6**: LGPL-3.0 (see `licenses/` for notices and license copy)

## 📦 Dependencies

- **[PySide6](https://pypi.org/project/PySide6/)** (>=6.7) - Qt6 Python bindings
- **[observables](https://github.com/babrandes/observables)** (>=4.0.2) - Reactive observable pattern
- **[united-system](https://github.com/babrandes/united-system)** (>=0.2.2) - Physical units system

## 🔗 Related Projects

- [observables](https://github.com/babrandes/observables) - Observable pattern for Python
- [united-system](https://github.com/babrandes/united-system) - Physical units and dimensions system

---

**Ready to get started?** Try the [featured demos](#-featured-demos) or dive into the [complete documentation](docs/README.md)!
