## Guarded Widgets

This module provides Qt widgets with "guarded" semantics: programmatic mutations of the widget state (e.g., adding items to a combo box) are only allowed when performed inside an internal update context managed by a controller or owner widget. This avoids feedback loops between the UI and observables.

### GuardedEditableComboBox

- Editable `QComboBox`
- Guards model mutations (`clear`, `addItem`, `insertItem`, `removeItem`)
- End-users can type freely; programmatic text changes must be wrapped by the owner's internal update context

### UnitComboBox

- Built on `GuardedEditableComboBox`
- Accepts an `observable` for single selection, a `Unit`, or a `Dimension`
- Displays available units and keeps them in sync with the observable
- When the user types a new unit string, it validates it against the known `Dimension`. If valid, it is added to the options and selected. Otherwise the edit is reverted

### GuardedRangeSlider

- A single-widget, two-handle range slider
- Prevents crossing, supports a minimum gap, and allows a draggable center handle to move the entire selected range
- Keyboard support: arrows/PageUp/PageDown/Home/End

### Internal update context

Guarded widgets allow programmatic mutations only inside an internal update
context. Controllers should set an attribute `_internal_widget_update=True`
on their owner during programmatic sync. A shared helper is available:

```python
from integrated_widgets.util.general import InternalUpdateHelper

helper = InternalUpdateHelper(owner_widget)
with helper.context():
    guarded_combo.clear()
    guarded_combo.addItem("One")
```

### Threading and disposal

Controllers connect to observables and forward updates onto the Qt thread via
queued signals. When disposing controllers, the owner widget and helper flag
are safe to leave behind; guarded widgets simply fall back to blocking model
mutations when the flag is absent or False.

### Controllers

Controllers mirror the guarded widgets with application-level behavior, e.g.
`UnitComboBoxController` validates typed unit strings against a dimension and
keeps the observable in sync.


