# Controlled Widgets

This module provides Qt widgets with "controlled" semantics: programmatic mutations of widget state (e.g., adding items to a combo box, changing text) are only allowed when performed inside an internal update context managed by a controller. This prevents feedback loops between the UI and observables while allowing normal user interaction.

## Why Controlled Widgets?

In reactive UI architectures with bidirectional binding, you can easily create feedback loops:

1. User changes widget → controller updates observable
2. Observable change triggers → controller updates widget
3. Widget change triggers signal → controller tries to update observable again
4. Infinite loop!

Controlled widgets solve this by:
- **Blocking programmatic mutations** outside of controller contexts
- **Allowing user interactions** to proceed normally
- **Raising clear errors** when misused

## Architecture

All controlled widgets inherit from `BaseControlledWidget` and wrap standard Qt widgets:

```
BaseControlledWidget
├── ControlledLabel (wraps QLabel)
├── ControlledLineEdit (wraps QLineEdit)
├── ControlledCheckBox (wraps QCheckBox)
├── ControlledRadioButton (wraps QRadioButton)
├── ControlledComboBox (wraps QComboBox)
├── ControlledEditableComboBox (wraps QComboBox, editable)
├── ControlledListWidget (wraps QListWidget)
├── ControlledSlider (wraps QSlider)
└── ControlledRangeSlider (custom two-handle slider)
```

## Usage with Controllers

Controlled widgets are designed to be used with controllers. The controller manages the internal update context:

```python
from integrated_widgets.widget_controllers import IntegerEntryController
from integrated_widgets.controlled_widgets import ControlledLineEdit
from observables import Observable

# Controller creates and manages the controlled widget internally
value_observable = Observable(42)
controller = IntegerEntryController(
    value=value_observable,
    label_text="Enter Value"
)

# The controller handles all synchronization
# You typically don't interact with the controlled widget directly
layout.addWidget(controller.widget())
```

## Internal Update Context

Controllers use the internal update mechanism to safely modify widgets:

```python
class MyController(BaseSingleHookController):
    def _invalidate_widgets_impl(self):
        """Update widget from observable"""
        # This context allows programmatic widget modification
        with self._internal_widget_update():
            self._controlled_line_edit.setText(str(self.get_value()))
```

The context manager temporarily sets `self._controller._internal_widget_update = True`, which controlled widgets check before allowing programmatic changes.

## Controlled Widget Behavior

### Guarded Operations

Certain operations are "guarded" and only work inside the internal update context:

**ControlledComboBox / ControlledEditableComboBox:**
- `clear()`
- `addItem()`
- `insertItem()`
- `removeItem()`

**ControlledLineEdit:**
- `setText()`

**ControlledListWidget:**
- `clear()`
- `addItem()`
- `insertItem()`
- `takeItem()`

**ControlledLabel:**
- `setText()`

### User Interactions

User interactions (typing, clicking, selecting) always work normally. Controlled widgets only block programmatic changes:

```python
# This works - user typing
controlled_line_edit.setFocus()
# User types "hello" → works fine

# This fails - programmatic change
controlled_line_edit.setText("world")  # RuntimeError!

# This works - inside controller context
with controller._internal_widget_update():
    controlled_line_edit.setText("world")  # OK
```

## BlankableWidget

A special wrapper that can hide widgets while maintaining their layout space:

```python
from integrated_widgets.controlled_widgets import BlankableWidget
from PySide6.QtWidgets import QLineEdit

# Create any Qt widget
line_edit = QLineEdit()

# Wrap it (automatically inherits parent from inner widget)
wrapper = BlankableWidget(line_edit)

# Add to layout
layout.addWidget(wrapper)

# Hide the widget but keep its space
wrapper.blank()  # Widget disappears, spacer maintains layout

# Show it again
wrapper.unblank()  # Widget reappears in same position

# Check state
if wrapper.isBlanked():
    print("Widget is blanked")

# Access inner widget
inner = wrapper.innerWidget()  # Returns the original QLineEdit
```

### BlankableWidget Features

**Blanking behavior:**
- Removes widget from layout, inserts spacer with same size policy
- Blocks signals: `blockSignals(True)`
- Disables interaction: `setEnabled(False)`
- Prevents mouse events: `WA_TransparentForMouseEvents`
- Makes invisible: `setVisible(False)`

**Unblanking behavior:**
- Removes spacer, reinserts widget at same position
- Restores original enabled state
- Restores original signal blocking state
- Restores original mouse event handling
- Makes visible: `setVisible(True)`

**Parent management:**
- BlankableWidget inherits the inner widget's parent
- Inner widget is then reparented to BlankableWidget
- This allows seamless integration into existing layouts

**Use cases:**
- Conditional UI sections that shouldn't reflow layout
- Placeholder widgets during async loading
- Disabled state that maintains visual space
- Dynamic forms with optional fields

## ControlledRangeSlider

A custom slider widget with two handles for selecting a range:

```python
from integrated_widgets.controlled_widgets import ControlledRangeSlider
from integrated_widgets.widget_controllers import RangeSliderController

# The controller manages the controlled range slider
controller = RangeSliderController(
    range_min=Observable(20.0),
    range_max=Observable(80.0),
    absolute_min=0.0,
    absolute_max=100.0
)
```

**Features:**
- **Two handles**: Independently draggable min/max handles
- **Center span**: Drag the span between handles to move both together
- **Minimum gap**: Configurable minimum distance between handles
- **Keyboard support**: Arrow keys, PageUp/Down, Home/End
- **Prevents crossing**: Handles cannot pass each other
- **Visual feedback**: Different colors for handles, span, and track

## Creating Custom Controlled Widgets

Extend `BaseControlledWidget` and override guarded methods:

```python
from integrated_widgets.controlled_widgets import BaseControlledWidget
from PySide6.QtWidgets import QWidget

class MyControlledWidget(BaseControlledWidget, QWidget):
    def __init__(self, controller, logger=None):
        BaseControlledWidget.__init__(self, controller, logger)
        QWidget.__init__(self)
    
    def dangerousMethod(self):
        """A method that should only be called by the controller"""
        if not self._is_internal_update():
            raise RuntimeError(
                "dangerousMethod can only be called inside "
                "controller internal update context"
            )
        # Safe to proceed
        self._do_dangerous_thing()
```

## Best Practices

### DO:
- ✅ Use controllers to manage controlled widgets
- ✅ Modify widgets inside `_internal_widget_update()` context
- ✅ Let users interact with widgets normally
- ✅ Use `BlankableWidget` for conditional visibility with layout preservation
- ✅ Dispose controllers properly to clean up connections

### DON'T:
- ❌ Call guarded methods directly from application code
- ❌ Bypass the controller architecture
- ❌ Try to manually manage the internal update flag
- ❌ Forget to handle widget lifecycle and disposal

## Error Messages

If you see:

```
RuntimeError: Direct programmatic modification of combo box is not allowed; 
perform changes within the controller's internal update context
```

**Cause**: You're trying to modify a controlled widget directly

**Solution**: 
1. Use a controller to manage the widget
2. If creating a custom controller, use `_internal_widget_update()` context
3. Review your code for direct widget manipulation

## Thread Safety

Controlled widgets themselves are not thread-safe (like all Qt widgets). However:

- Controllers handle thread-safe bridging from observables
- Use controllers' queued signal connections for cross-thread updates
- Never modify controlled widgets directly from non-GUI threads

## Testing Controlled Widgets

When testing:

```python
def test_controlled_widget():
    from integrated_widgets.util.base_controller import BaseController
    
    # Create a mock controller
    controller = BaseController(...)
    
    # Create controlled widget
    widget = ControlledLineEdit(controller)
    
    # Test with internal update context
    with controller._internal_widget_update():
        widget.setText("test")
        assert widget.text() == "test"
    
    # Test that direct modification fails
    with pytest.raises(RuntimeError):
        widget.setText("fail")
```

## Performance Considerations

- Controlled widgets have minimal overhead
- The internal update check is a simple attribute lookup
- `BlankableWidget` maintains a spacer for fast blanking/unblanking
- No performance impact on user interactions

## Migration from Direct Qt Widgets

If migrating from direct Qt widget usage:

**Before:**
```python
combo = QComboBox()
combo.clear()
combo.addItem("Option 1")
layout.addWidget(combo)
```

**After:**
```python
options = Observable({"Option 1", "Option 2"})
selected = Observable("Option 1")
controller = SelectionOptionController(
    value=selected,
    options=options
)
layout.addWidget(controller.widget())
```

The controller handles all synchronization, validation, and prevents feedback loops automatically.
