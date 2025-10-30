# Integrated Widgets API Reference

> **⚠️ Development Status**: This library is in active development and is NOT production-ready. The API documented here may change without notice. This reference reflects the current state of the library.

## Core Classes

### BaseController

Abstract base class for all controllers providing common functionality.

```python
class BaseController(Generic[HK, HV]):
    def __init__(
        self,
        *,
        nexus_manager: NexusManager,
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

**Properties:**
- `is_blocking_signals: bool` - Controls whether widget signals are blocked
- `widget(): QWidget` - Returns the main widget managed by this controller

**Methods:**
- `dispose() -> None` - Clean up resources and disconnect from nexpys
- `_submit_values_debounced(value: Any, debounce_ms: Optional[int] = None) -> None` - Submit value with debouncing
- `_internal_widget_update() -> ContextManager` - Context for programmatic widget updates

### BaseSingletonController

Base class for controllers managing a single observable value.

```python
class BaseSingletonController(BaseController[Literal["value"], T], Generic[T]):
    def __init__(
        self,
        value: T | Hook[T] | XSingleValueProtocol[T],
        *,
        verification_method: Optional[Callable[[T], tuple[bool, str]]] = None,
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

**Abstract Methods:**
- `_invalidate_widgets_impl() -> None` - Update widget from nexpy value

### BaseCompositeController

Base class for controllers managing multiple observable values.

```python
class BaseCompositeController(BaseController[PHK|SHK, PHV|SHV], Generic[PHK, SHK, PHV, SHV]):
    def __init__(
        self,
        *,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

**Methods:**
- `submit_values(values: UpdateFunctionValues) -> None` - Submit multiple values
- `_invalidate_widgets_impl() -> None` - Update widgets from observable values

## High-Level IQt Widgets

The IQt widgets provide a simplified, high-level API for creating UI components with automatic nexpy binding. These widgets compose the lower-level controllers with flexible layout strategies.

### IQtDisplayValue

Read-only display widget with custom formatting and automatic nexpy synchronization.

```python
class IQtDisplayValue(Generic[T]):
    def __init__(
        self,
        value_or_hook_or_nexpy: T | Hook[T] | XValueProtocol[T],
        formatter: Optional[Callable[[T], str]] = None,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None
```

**Parameters:**
- `value_or_hook_or_nexpy`: Value, hook, or nexpy to display
- `formatter`: Optional custom formatting function (defaults to `str()`)
- `layout_strategy`: Optional custom layout (defaults to simple label display)
- `parent`: Parent widget
- `logger`: Optional logger instance

**Properties:**
- `value: T` - Get or set the displayed value
- `value_hook` - Access the underlying hook for advanced use
- `controller: DisplayValueController[T]` - Access the underlying controller

**Methods:**
- `submit(value: T)` - Update the displayed value (simplified API)
- `change_value(value: T)` - Alternative name for submit

**Key Features:**
- **Easy Connect**: Pass nexpys directly for automatic synchronization
- **Custom Formatting**: Flexible formatters for any value type  
- **Simple Submit**: Use `submit(value)` instead of `submit_value("value", value)`
- **Custom Layouts**: Optional layout strategies for flexible UI design

**Examples:**

Basic usage with nexpy:
```python
from nexpy import XValue
from integrated_widgets import IQtDisplayValue

# Simple counter display
counter = XValue(0)
display = IQtDisplayValue(counter, formatter=lambda x: f"Count: {x}")

# Widget automatically updates when counter changes
counter.value = 10  # Display shows "Count: 10"
```

Easy connect with temperature:
```python
from united_system import RealUnitedScalar, Unit

temperature = XValue(RealUnitedScalar(20.0, Unit("°C")))
display = IQtDisplayValue(
    temperature,
    formatter=lambda x: f"{x.value():.1f} {x.unit}"
)
```

Using simplified submit:
```python
display.submit(25.0)  # Clean and simple
# Instead of: display.submit_value("value", 25.0)

# Or use the property
display.value = 30.0
```

Custom layout with label prefix:
```python
def labeled_layout(parent, payload):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(QLabel("Status:"))
    layout.addWidget(payload.label)
    return widget

display = IQtDisplayValue(
    status_nexpy,
    layout_strategy=labeled_layout
)
```

Connecting to range slider:
```python
from integrated_widgets import IQtRangeSlider

percentage = XValue(0.5)
display = IQtDisplayValue(percentage, formatter=lambda x: f"{x*100:.1f}%")

# Easy connect to slider's lower span hook
slider = IQtRangeSlider(...)
slider.controller.span_lower_relative_value_hook.connect_hook(
    percentage, 
    initial_sync_mode="use_target_value"
)
```

---

## Widget Controllers

### CheckBoxController

Manages boolean values with QCheckBox.

```python
class CheckBoxController(BaseSingletonController[bool]):
    def __init__(
        self,
        value: bool | Hook[bool] | XSingleValueProtocol[bool],
        *,
        text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### IntegerEntryController

Manages integer values with QLineEdit and validation.

```python
class IntegerEntryController(BaseSingletonController[int]):
    def __init__(
        self,
        value: int | Hook[int] | XSingleValueProtocol[int],
        *,
        label_text: str = "",
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### FloatEntryController

Manages float values with QLineEdit and validation.

```python
class FloatEntryController(BaseSingletonController[float]):
    def __init__(
        self,
        value: float | Hook[float] | XSingleValueProtocol[float],
        *,
        label_text: str = "",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        decimals: int = 6,
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### TextEntryController

Manages string values with QLineEdit.

```python
class TextEntryController(BaseSingletonController[str]):
    def __init__(
        self,
        value: str | Hook[str] | XSingleValueProtocol[str],
        *,
        label_text: str = "",
        placeholder_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### OptionalTextEntryController

Manages optional string values with QLineEdit and clear button.

```python
class OptionalTextEntryController(BaseSingletonController[str]):
    def __init__(
        self,
        value: str | Hook[str] | XSingleValueProtocol[str],
        *,
        label_text: str = "",
        placeholder_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### PathSelectorController

Manages file/directory paths with QLineEdit and browse button.

```python
class PathSelectorController(BaseSingletonController[str]):
    def __init__(
        self,
        value: str | Hook[str] | XSingleValueProtocol[str],
        *,
        label_text: str = "",
        dialog_title: str = "Select File",
        file_filter: str = "All files (*.*)",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### RadioButtonsController

Manages enum selection with QRadioButton group.

```python
class RadioButtonsController(BaseCompositeController[Literal["selected_option", "available_options"], T, AbstractSet[T], AbstractSet[T]], Generic[T]):
    def __init__(
        self,
        selected_option: T | Hook[T] | XSingleValueProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        *,
        label_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### SelectionOptionController

Manages single selection from options with QComboBox.

```python
class SelectionOptionController(BaseCompositeController[Literal["selected_option", "available_options"], T, AbstractSet[T], AbstractSet[T]], Generic[T]):
    def __init__(
        self,
        selected_option: T | Hook[T] | XSingleValueProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        *,
        label_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### SelectionOptionalOptionController

Manages optional selection from options with QComboBox.

```python
class SelectionOptionalOptionController(BaseCompositeController[Literal["selected_option", "available_options"], Optional[T], AbstractSet[T], AbstractSet[T]], Generic[T]):
    def __init__(
        self,
        selected_option: Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T]],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        *,
        label_text: str = "",
        none_text: str = "None",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### SingleListSelectionController

Manages single selection from list with QListWidget.

```python
class SingleListSelectionController(BaseCompositeController[Literal["selected_option", "available_options"], Optional[T], AbstractSet[T], AbstractSet[T]], Generic[T]):
    def __init__(
        self,
        selected_option: Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T]],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        *,
        label_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### DoubleListSelectionController

Manages multiple selection from list with QListWidget.

```python
class DoubleListSelectionController(BaseCompositeController[Literal["selected_options", "available_options"], AbstractSet[T], AbstractSet[T], AbstractSet[T]], Generic[T]):
    def __init__(
        self,
        selected_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        *,
        label_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### UnitComboBoxController

Manages unit selection with dimension validation.

```python
class UnitComboBoxController(BaseCompositeController[Literal["selected_unit", "available_units"], Any, Any, Any]):
    def __init__(
        self,
        selected_unit: Any,
        available_units: Any,
        *,
        label_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### RangeSliderController

Manages range values with custom two-handle slider.

```python
class RangeSliderController(BaseCompositeController[Literal["span_lower_relative_value", "span_upper_relative_value", "range_lower_value", "range_upper_value"], float, float, float]):
    def __init__(
        self,
        span_lower_relative_value: float | Hook[float] | XSingleValueProtocol[float],
        span_upper_relative_value: float | Hook[float] | XSingleValueProtocol[float],
        range_lower_value: float | Hook[float] | XSingleValueProtocol[float],
        range_upper_value: float | Hook[float] | XSingleValueProtocol[float],
        *,
        number_of_ticks: int = 100,
        label_text: str = "",
        debounce_slider_movement_interval_ms: int = 50,
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### RealUnitedScalarController

Manages unit-aware numeric values with full unit support.

```python
class RealUnitedScalarController(BaseCompositeController[Literal["value", "unit_options"], Any, Any, Any]):
    def __init__(
        self,
        value: Any,
        unit_options: Any,
        *,
        label_text: str = "",
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

### DisplayValueController

Read-only value display with QLabel and custom formatting.

```python
class DisplayValueController(BaseSingletonController[T], Generic[T]):
    def __init__(
        self,
        value: T | Hook[T] | XSingleValueProtocol[T],
        formatter: Optional[Callable[[T], str]] = None,
        debounce_ms: int | Callable[[], int] = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None
```

**Parameters:**
- `value`: Initial value, hook, or observable to display
- `formatter`: Optional function to format the value for display (defaults to `str()`)
- `debounce_ms`: Debounce delay in milliseconds or callable returning delay
- `logger`: Optional logger instance
- `nexus_manager`: Nexus manager for observable coordination

**Properties:**
- `value: T` - Get or set the displayed value
- `formatter: Optional[Callable[[T], str]]` - Get or set the formatter function
- `widget_label: ControlledLabel` - The read-only label widget

**Methods:**
- `submit(value: T) -> None` - Update the displayed value (alias: `change_value()`)
- `change_formatter(formatter: Callable[[T], str]) -> None` - Change the formatter

**Examples:**

Basic usage:
```python
from nexpy import XValue
from integrated_widgets.controllers.singleton.display_value_controller import DisplayValueController

# Simple display
counter = XValue(42)
controller = DisplayValueController(counter)
```

With custom formatting:
```python
# Format temperature
temperature = XValue(20.5)
controller = DisplayValueController(
    temperature,
    formatter=lambda t: f"{t:.1f}°C"
)
```

Easy connect to nexpys:
```python
# Connect to any nexpy
sensor_value = XValue(0.0)
controller = DisplayValueController(
    sensor_value,
    formatter=lambda x: f"{x*100:.1f}%"
)
# Widget automatically updates when sensor_value changes
```

Using the simplified submit method:
```python
# Instead of submit_value("value", new_value)
controller.submit(new_value)  # Clean, simple API
```

## Controlled Widgets

### ControlledLabel

QLabel wrapper that prevents direct modification.

```python
class ControlledLabel(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledLineEdit

QLineEdit wrapper that prevents direct modification.

```python
class ControlledLineEdit(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledCheckBox

QCheckBox wrapper that prevents direct modification.

```python
class ControlledCheckBox(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledRadioButton

QRadioButton wrapper that prevents direct modification.

```python
class ControlledRadioButton(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledComboBox

QComboBox wrapper that prevents direct modification.

```python
class ControlledComboBox(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledEditableComboBox

Editable QComboBox wrapper that prevents direct modification.

```python
class ControlledEditableComboBox(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledListWidget

QListWidget wrapper that prevents direct modification.

```python
class ControlledListWidget(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledSlider

QSlider wrapper that prevents direct modification.

```python
class ControlledSlider(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### ControlledRangeSlider

Custom two-handle range slider.

```python
class ControlledRangeSlider(BlankableWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None
```

### BlankableWidget

Base class for controlled widgets that can be hidden while maintaining layout space.

```python
class BlankableWidget(QWidget):
    def __init__(self, inner_widget: QWidget, parent: Optional[QWidget] = None) -> None
    
    def blank(self) -> None  # Hide the inner widget
    def unblank(self) -> None  # Show the inner widget
    def innerWidget(self) -> QWidget  # Get the inner widget
```

## Configuration

### Global Configuration

```python
import integrated_widgets

# Set global debounce timing (default: 100ms)
integrated_widgets.DEFAULT_DEBOUNCE_MS = 250
```

### Per-Controller Configuration

```python
controller = CheckBoxController(
    value=nexpy,
    debounce_ms=50,  # Override global setting
    logger=custom_logger  # Custom logging
)
```

## Constants

- `DEFAULT_DEBOUNCE_MS: int = 100` - Default debounce timing in milliseconds

## Type Hints

The library provides comprehensive type hints for all classes and methods, supporting static type checking with tools like mypy or Pyright.
