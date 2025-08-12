## Integrated Widgets

Custom PySide6 Qt widgets integrating `united_system` and `observable`.

### Features

- UnitValueDisplay: QLabel that shows a United scalar value with units, bound to an observable
- ObservableQtBridge: thread-safe bridge from an observable to a Qt Signal

### Install

Editable for development:

```bash
pip install -e .[test]
```

### Usage

```python
from integrated_widgets.widgets import UnitValueDisplay
from observable import Observable
# from united_system import United  # depending on the actual API

# observable_united = Observable(United(10, "m"))
# widget = UnitValueDisplay(observable_united)
```

### License

- Code: Apache-2.0 (see `LICENSE`)
- PySide6: LGPL-3.0; see `licenses/` for notices and copy of the license


