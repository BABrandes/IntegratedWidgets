# Integrated Widgets API Reference

> **⚠️ Development Status**: This library is in active development and is NOT production-ready. The API documented here may change without notice. This reference reflects the current state of the library.

## Core Classes

### BaseController

Abstract base class for all controllers providing common functionality.

```python
class BaseController:
    def __init__(
        self,
        submit_values_callback: Callable[[Mapping[str, Any]], tuple[bool, str]],
        *,
        nexus_manager: NexusManager,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

**Properties:**
- `is_blocking_signals: bool` - Controls whether widget signals are blocked
- `widget(): QWidget` - Returns the main widget managed by this controller

**Methods:**
- `dispose() -> None` - Clean up resources and disconnect from observables
- `_submit_values_debounced(value: Any, debounce_ms: Optional[int] = None) -> None` - Submit value with debouncing
- `_internal_widget_update() -> ContextManager` - Context for programmatic widget updates

### BaseSingleHookController

Base class for controllers managing a single observable.

```python
class BaseSingleHookController(BaseController):
    def __init__(
        self,
        hook_source: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        observing_widget: QWidget,
        *,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

**Abstract Methods:**
- `_invalidate_widgets_impl() -> None` - Update widget from observable value

### BaseComplexHookController

Base class for controllers managing multiple observables.

```python
class BaseComplexHookController(BaseController):
    def __init__(
        self,
        submit_values_callback: Callable[[Mapping[str, Any]], tuple[bool, str]],
        *,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

**Methods:**
- `submit_values(values: Mapping[str, Any]) -> tuple[bool, str]` - Submit multiple values
- `_invalidate_widgets_impl() -> None` - Update widgets from observable values

## Widget Controllers

### CheckBoxController

Manages boolean values with QCheckBox.

```python
class CheckBoxController(BaseSingleHookController):
    def __init__(
        self,
        value_or_hook_or_observable: bool | HookLike[bool] | ObservableSingleValueLike[bool],
        *,
        text: str = "",
        logger: Optional[Logger] = None,
    ) -> None
```

### IntegerEntryController

Manages integer values with QLineEdit and validation.

```python
class IntegerEntryController(BaseSingleHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### FloatEntryController

Manages float values with QLineEdit and validation.

```python
class FloatEntryController(BaseSingleHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        decimals: int = 6,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### TextEntryController

Manages string values with QLineEdit.

```python
class TextEntryController(BaseSingleHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        placeholder_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### OptionalTextEntryController

Manages optional string values with QLineEdit and clear button.

```python
class OptionalTextEntryController(BaseSingleHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        placeholder_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### PathSelectorController

Manages file/directory paths with QLineEdit and browse button.

```python
class PathSelectorController(BaseSingleHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        dialog_title: str = "Select File",
        file_filter: str = "All files (*.*)",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### RadioButtonsController

Manages enum selection with QRadioButton group.

```python
class RadioButtonsController(BaseComplexHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        options: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### SelectionOptionController

Manages single selection from options with QComboBox.

```python
class SelectionOptionController(BaseComplexHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        options: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### SelectionOptionalOptionController

Manages optional selection from options with QComboBox.

```python
class SelectionOptionalOptionController(BaseComplexHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        options: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        none_text: str = "None",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### SingleListSelectionController

Manages single selection from list with QListWidget.

```python
class SingleListSelectionController(BaseComplexHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        options: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### DoubleListSelectionController

Manages multiple selection from list with QListWidget.

```python
class DoubleListSelectionController(BaseComplexHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        options: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### UnitComboBoxController

Manages unit selection with dimension validation.

```python
class UnitComboBoxController(BaseComplexHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        dimension: str,
        *,
        label_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### RangeSliderController

Manages range values with custom two-handle slider.

```python
class RangeSliderController(BaseComplexHookController):
    def __init__(
        self,
        range_min: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        range_max: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        absolute_min: float,
        absolute_max: float,
        label_text: str = "",
        debounce_slider_movement_interval_ms: int = 50,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### RealUnitedScalarController

Manages unit-aware numeric values with full unit support.

```python
class RealUnitedScalarController(BaseComplexHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        unit: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        dimension: str,
        *,
        label_text: str = "",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
```

### DisplayValueController

Read-only value display with QLabel.

```python
class DisplayValueController(BaseSingleHookController):
    def __init__(
        self,
        value: OwnedHookLike[PHK, SHK, PHV, SHV, C],
        *,
        label_text: str = "",
        format_string: str = "{}",
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None
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
    value=observable,
    debounce_ms=50,  # Override global setting
    logger=custom_logger  # Custom logging
)
```

## Constants

- `DEFAULT_DEBOUNCE_MS: int = 100` - Default debounce timing in milliseconds

## Type Hints

The library provides comprehensive type hints for all classes and methods, supporting static type checking with tools like mypy or Pyright.
