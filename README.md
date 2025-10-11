# Integrated Widgets

A PySide6/Qt widget framework that integrates with `observable` and `united_system` to create reactive, unit-aware UI components with bidirectional data binding.

## Architecture Overview

The framework is built on three key concepts:

1. **Controllers**: Manage the bidirectional binding between observables and Qt widgets
2. **Controlled Widgets**: Specialized Qt widgets that prevent accidental feedback loops
3. **Observable Integration**: Thread-safe bridges for reactive programming

### Controllers

Controllers sit between your application logic (observables) and the UI (Qt widgets). They:

- Subscribe to observables and update widgets when data changes
- Listen to widget signals and update observables when users interact
- Prevent feedback loops through internal update contexts
- Manage lifecycle and proper cleanup

**Base Classes:**
- `BaseController`: Abstract base for all controllers
- `BaseSingleHookController`: For controllers managing a single observable
- `BaseComplexHookController`: For controllers managing multiple observables

**Built-in Controllers:**
- `CheckBoxController`: Boolean values ↔ QCheckBox
- `IntegerEntryController`: Integer values ↔ QLineEdit with validation
- `FloatEntryController`: Float values ↔ QLineEdit with validation
- `RadioButtonsController`: Enum selection ↔ QRadioButton group
- `SelectionOptionController`: Single selection from options ↔ QComboBox
- `SelectionOptionalOptionController`: Optional selection ↔ QComboBox with "None" option
- `UnitComboBoxController`: Unit selection with dimension validation
- `RangeSliderController`: Range values ↔ custom two-handle slider
- `RealUnitedScalarController`: Full unit-aware numeric entry and display
- `DisplayValueController`: Read-only value display

### Controlled Widgets

Controlled widgets are specialized Qt widgets that integrate with the controller architecture. They prevent direct programmatic modification outside of controller contexts, avoiding feedback loops.

**Available Controlled Widgets:**
- `ControlledLabel`: QLabel wrapper
- `ControlledLineEdit`: QLineEdit wrapper  
- `ControlledCheckBox`: QCheckBox wrapper
- `ControlledRadioButton`: QRadioButton wrapper
- `ControlledComboBox`: QComboBox wrapper
- `ControlledEditableComboBox`: Editable QComboBox wrapper
- `ControlledListWidget`: QListWidget wrapper
- `ControlledSlider`: QSlider wrapper
- `ControlledRangeSlider`: Custom two-handle range slider

**Key Features:**
- Block programmatic mutations (e.g., `clear()`, `addItem()`) outside controller context
- Raise `RuntimeError` if modified directly
- Allow normal user interaction
- Integrate seamlessly with controller internal update mechanisms

### BlankableWidget

A special wrapper widget that can hide its content while maintaining layout space:

```python
from integrated_widgets.controlled_widgets import BlankableWidget

inner_widget = QLineEdit()
wrapper = BlankableWidget(inner_widget)
layout.addWidget(wrapper)

# Hide the widget but keep its space
wrapper.blank()

# Show it again
wrapper.unblank()

# Access the inner widget
inner = wrapper.innerWidget()
```

**Use Cases:**
- Conditionally hide widgets without layout reflow
- Disable interaction while preserving UI structure
- Create placeholder spaces in dynamic layouts

## Installation

### For Development

```bash
pip install -e .[test]
```

### For Production

```bash
pip install integrated-widgets
```

## Usage Examples

### Basic Controller Usage

```python
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from observables import Observable
from integrated_widgets.widget_controllers import CheckBoxController

app = QApplication([])
window = QWidget()
layout = QVBoxLayout(window)

# Create an observable
enabled_observable = Observable(True)

# Create a controller (it creates and manages its own QCheckBox)
controller = CheckBoxController(
    value=enabled_observable,
    label_text="Enable Feature"
)

# Add the controller's widget to your layout
layout.addWidget(controller.widget())

# The checkbox and observable stay in sync automatically
enabled_observable.set(False)  # Updates checkbox
# User clicking checkbox updates observable

window.show()
app.exec()

# Clean up
controller.dispose()
```

### Unit-Aware Entry

```python
from united_system import Unit
from observables import Observable
from integrated_widgets.widget_controllers import RealUnitedScalarController

# Observable with a united value
distance = Observable(100.0)  # in meters
unit = Observable(Unit("m"))

controller = RealUnitedScalarController(
    value=distance,
    unit=unit,
    dimension="L",  # Length dimension
    label_text="Distance"
)

layout.addWidget(controller.widget())

# User can type "5.2 km" and it will be converted and validated
# Controller handles all unit conversion and validation
```

### Selection from Options

```python
from observables import Observable
from integrated_widgets.widget_controllers import SelectionOptionController

options = Observable({"apple", "banana", "cherry"})
selected = Observable("apple")

controller = SelectionOptionController(
    value=selected,
    options=options,
    label_text="Choose Fruit"
)

layout.addWidget(controller.widget())

# Options and selection stay in sync with observables
options.set({"apple", "banana", "cherry", "date"})  # Updates combo box
# User selection updates the selected observable
```

### Range Slider

```python
from observables import Observable
from integrated_widgets.widget_controllers import RangeSliderController

min_value = Observable(20.0)
max_value = Observable(80.0)

controller = RangeSliderController(
    range_min=min_value,
    range_max=max_value,
    absolute_min=0.0,
    absolute_max=100.0,
    label_text="Value Range"
)

layout.addWidget(controller.widget())

# Bidirectional binding with range constraints
# User can drag handles or the center span
# Values are always kept in valid state
```

## Advanced Usage

### Creating Custom Controllers

Subclass `BaseSingleHookController` or `BaseComplexHookController`:

```python
from integrated_widgets.util.base_single_hook_controller import BaseSingleHookController
from observables import Observable
from PySide6.QtWidgets import QSpinBox

class SpinBoxController(BaseSingleHookController):
    def __init__(self, value: Observable[int], **kwargs):
        self._spin_box = QSpinBox()
        
        super().__init__(
            hook_source=value,
            observing_widget=self._spin_box,
            **kwargs
        )
        
        # Connect widget signals
        self._spin_box.valueChanged.connect(self._on_value_changed)
    
    def _invalidate_widgets_impl(self) -> None:
        """Update widget from observable"""
        with self._internal_widget_update():
            self._spin_box.setValue(self.get_value())
    
    def _on_value_changed(self, new_value: int) -> None:
        """Update observable from widget"""
        if not self._is_internal_update():
            self.set_value(new_value)
    
    def widget(self) -> QSpinBox:
        return self._spin_box
```

### Internal Update Context

When programmatically updating controlled widgets, use the internal update context:

```python
with controller._internal_widget_update():
    controlled_combo.clear()
    controlled_combo.addItem("Option 1")
    controlled_combo.addItem("Option 2")
```

This prevents the controller from treating programmatic changes as user input.

## Demo Applications

Run the included demos to see the controllers in action:

```bash
# Check box demo
python -m src.integrated_widgets.demos.demo_check_box_controller

# Unit combo box demo  
python -m src.integrated_widgets.demos.demo_unit_combo_box_controller

# Range slider demo
python -m src.integrated_widgets.demos.demo_range_slider_controller

# Integer entry demo
python -m src.integrated_widgets.demos.demo_integer_entry_controller

# Radio buttons demo
python -m src.integrated_widgets.demos.demo_radio_buttons_controller

# Selection combo demo
python -m src.integrated_widgets.demos.demo_selection_option_controller
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Architecture Details

### Controller Lifecycle

1. **Initialization**: Controller creates or accepts widgets, connects to observables
2. **Active**: Bidirectional updates between observables and widgets
3. **Disposal**: Clean disconnection, observers removed, resources freed

Always call `controller.dispose()` when done, or use controllers as context managers if supported.

### Thread Safety

Controllers use Qt's signal/slot mechanism with queued connections to ensure thread-safe updates from observables to widgets. Observable changes from any thread are safely marshaled to the Qt GUI thread.

### Preventing Feedback Loops

The internal update mechanism (`_internal_widget_update()` context) temporarily blocks the controller from reacting to its own programmatic widget updates, preventing infinite update loops.

## Contributing

Contributions welcome! Please:

1. Add tests for new controllers
2. Update documentation
3. Follow the existing code style
4. Ensure all tests pass

## License

- **Code**: Apache-2.0 (see `LICENSE`)
- **PySide6**: LGPL-3.0 (see `licenses/` for notices and license copy)

## Dependencies

- **PySide6**: Qt6 Python bindings
- **observables**: Reactive observable pattern implementation
- **united_system**: Physical units and dimensions system

## Related Projects

- [observables](https://github.com/yourusername/observables) - Observable pattern for Python
- [united_system](https://github.com/yourusername/united_system) - Physical units system
