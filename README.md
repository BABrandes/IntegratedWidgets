# Integrated Widgets

A PySide6/Qt widget framework that integrates with `observable` and `united_system` to create reactive, unit-aware UI components with bidirectional data binding and advanced debouncing capabilities.

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
- Provide debounced input handling for smooth user experience
- Support configurable debounce timing for different use cases

**Base Classes:**
- `BaseController`: Abstract base for all controllers
- `BaseSingleHookController`: For controllers managing a single observable
- `BaseComplexHookController`: For controllers managing multiple observables

**Built-in Controllers:**
- `CheckBoxController`: Boolean values ↔ QCheckBox
- `IntegerEntryController`: Integer values ↔ QLineEdit with validation
- `FloatEntryController`: Float values ↔ QLineEdit with validation
- `TextEntryController`: String values ↔ QLineEdit
- `OptionalTextEntryController`: Optional string values ↔ QLineEdit with clear button
- `PathSelectorController`: File/directory paths ↔ QLineEdit with browse button
- `RadioButtonsController`: Enum selection ↔ QRadioButton group
- `SelectionOptionController`: Single selection from options ↔ QComboBox
- `SelectionOptionalOptionController`: Optional selection ↔ QComboBox with "None" option
- `SingleListSelectionController`: Single selection from list ↔ QListWidget
- `DoubleListSelectionController`: Multiple selection from list ↔ QListWidget
- `UnitComboBoxController`: Unit selection with dimension validation
- `RangeSliderController`: Range values ↔ custom two-handle slider with debounced movement
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

## Configuration

### Debounce Timing

The library provides configurable debouncing for user input to ensure smooth performance:

```python
import integrated_widgets

# Set global debounce timing (default: 100ms)
integrated_widgets.DEFAULT_DEBOUNCE_MS = 250  # 250ms for slower systems

# Or configure per-controller
controller = CheckBoxController(
    value=observable,
    debounce_ms=50  # Faster response for this controller
)
```

**Debouncing Benefits:**
- Prevents excessive updates during rapid user input
- Reduces CPU usage and improves responsiveness
- Configurable timing for different use cases
- Automatic cleanup and proper resource management

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
from integrated_widgets import CheckBoxController

# QApplication is required for all Qt widgets
app = QApplication([])
window = QWidget()
layout = QVBoxLayout(window)

# Create an observable
enabled_observable = Observable(True)

# Create a controller (it creates and manages its own QCheckBox)
controller = CheckBoxController(
    enabled_observable,  # First parameter: observable/hook/value
    text="Enable Feature"  # Named parameter: label text
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
from integrated_widgets import RealUnitedScalarController

# Observable with a united value
distance = Observable(100.0)  # in meters
unit = Observable(Unit("m"))

controller = RealUnitedScalarController(
    distance,  # First parameter: value observable
    unit,      # Second parameter: unit observable
    "L",       # Third parameter: dimension
    label_text="Distance"  # Named parameter: label text
)

layout.addWidget(controller.widget())

# User can type "5.2 km" and it will be converted and validated
# Controller handles all unit conversion and validation
```

### Selection from Options

```python
from observables import Observable
from integrated_widgets import SelectionOptionController

options = Observable({"apple", "banana", "cherry"})
selected = Observable("apple")

controller = SelectionOptionController(
    selected,  # First parameter: selected value observable
    options,   # Second parameter: options observable
    label_text="Choose Fruit"  # Named parameter: label text
)

layout.addWidget(controller.widget())

# Options and selection stay in sync with observables
options.set({"apple", "banana", "cherry", "date"})  # Updates combo box
# User selection updates the selected observable
```

### Range Slider

```python
from observables import Observable
from integrated_widgets import RangeSliderController

min_value = Observable(20.0)
max_value = Observable(80.0)

controller = RangeSliderController(
    min_value,  # First parameter: minimum value observable
    max_value,  # Second parameter: maximum value observable
    absolute_min=0.0,    # Named parameter: absolute minimum
    absolute_max=100.0,  # Named parameter: absolute maximum
    label_text="Value Range"  # Named parameter: label text
)

layout.addWidget(controller.widget())

# Bidirectional binding with range constraints
# User can drag handles or the center span
# Values are always kept in valid state
```

### Path Selection with File Dialog

```python
from observables import Observable
from integrated_widgets import PathSelectorController

file_path = Observable("")

controller = PathSelectorController(
    file_path,  # First parameter: file path observable
    label_text="Select File",
    dialog_title="Choose a file",
    file_filter="Text files (*.txt);;All files (*.*)"
)

layout.addWidget(controller.widget())

# User can type path directly or use browse button
# Controller handles file dialog and validation
```

### Configuring Debounce Timing

```python
import integrated_widgets
from integrated_widgets import TextEntryController
from observables import Observable

# Set global debounce timing
integrated_widgets.DEFAULT_DEBOUNCE_MS = 200  # 200ms for all controllers

# Or configure specific controller
text_observable = Observable("")
controller = TextEntryController(
    text_observable,  # First parameter: text observable
    debounce_ms=50,   # Named parameter: faster response
    label_text="Fast Response"  # Named parameter: label text
)

# Debouncing prevents excessive updates during typing
# Only commits value after user stops typing for specified time
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
        """Update observable from widget using debounced submission"""
        # Use the built-in debounced submission
        self._submit_values_debounced(new_value)
    
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

Run the included demos to see the controllers in action. All demos are located in the `demos/` folder:

```bash
# Navigate to the demos folder
cd demos

# Check box demo
python demo_check_box_controller.py

# Unit combo box demo  
python demo_unit_combo_box_controller.py

# Range slider demo
python demo_range_slider_controller.py

# Integer entry demo
python demo_integer_entry_controller.py

# Radio buttons demo
python demo_radio_buttons_controller.py

# Selection combo demo
python demo_selection_option_controller.py

# Display real united scalar demo
python demo_display_real_united_scalar_controller.py

# Selection optional option demo
python demo_selection_optional_option_controller.py

# Single list selection demo
python demo_single_list_selection_controller.py
```

**Demo Features:**
- Comprehensive examples of all controller types
- Real-time logging of all interactions
- Observable integration demonstrations
- Unit-aware widget examples
- Debounced input handling examples

## Testing

Run the test suite:

```bash
pytest tests/
```

## Architecture Details

### Controller Lifecycle

1. **Initialization**: Controller creates or accepts widgets, connects to observables, sets up debouncing
2. **Active**: Bidirectional updates between observables and widgets with debounced user input
3. **Disposal**: Clean disconnection, observers removed, timers stopped, resources freed

Always call `controller.dispose()` when done, or use controllers as context managers if supported.

### Debounced Input Handling

The framework provides sophisticated debouncing capabilities:

- **Centralized Debouncing**: All controllers use a unified debouncing system
- **Configurable Timing**: Global and per-controller debounce configuration
- **Automatic Cleanup**: Timers are properly managed and cleaned up
- **Exception Safety**: Robust error handling during disposal
- **Performance Optimized**: Reduces unnecessary updates during rapid user input

### Thread Safety

Controllers use Qt's signal/slot mechanism with queued connections to ensure thread-safe updates from observables to widgets. Observable changes from any thread are safely marshaled to the Qt GUI thread.

### Preventing Feedback Loops

The internal update mechanism (`_internal_widget_update()` context) temporarily blocks the controller from reacting to its own programmatic widget updates, preventing infinite update loops.

### Signal Blocking

Controllers use a simplified boolean-based signal blocking mechanism:
- `controller.is_blocking_signals = True` - Blocks all widget signals
- `controller.is_blocking_signals = False` - Allows widget signals
- Automatic management during programmatic updates

## Recent Improvements

### v0.1.102+ - Major Architecture Enhancements

**Centralized Debouncing System:**
- Unified debouncing across all controllers
- Configurable timing with `DEFAULT_DEBOUNCE_MS`
- Automatic timer management and cleanup
- Exception-safe disposal handling

**Simplified Signal Blocking:**
- Replaced complex object tracking with simple boolean flag
- `is_blocking_signals` property for easy control
- Consistent behavior across all controllers

**Enhanced Error Handling:**
- Robust exception handling in disposal methods
- Graceful handling of Qt object lifecycle
- Improved logging with success/failure messages

**Cleaner Package Structure:**
- Demos moved to project root for better organization
- Removed unnecessary `parent_of_widgets` parameters
- Streamlined controller initialization

**Performance Optimizations:**
- Reduced memory overhead
- Faster signal blocking/unblocking
- Optimized debouncing implementation

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
