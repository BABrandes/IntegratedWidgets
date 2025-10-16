"""
Base controller composition (widget‑free)
========================================

**`BaseControllerComposition`** is a minimal *composition root* for managing the
lifecycle of **controllers** and **observables**. The composition itself is **pure
Python**: it does **not** inherit from `QObject` and never owns or creates widgets.
This keeps your application architecture clean, testable, and free of lifetime tangles.

Why this exists
---------------
Complex screens typically consist of several controllers that each wrap a Qt widget
and connect to observables via hooks. Somebody has to:

* Compose controllers and observables in **any** order
* Expose controllers/widgets for Qt layout management
* Tear everything down deterministically

That "somebody" is the **composition**. The actual coordination between controllers
happens through the observables/hooks system, not through the composition.

Design goals
------------
* **Widget‑free**: views/layouts live elsewhere. The composition never calls
  `QWidget(...)`, never re‑parents widgets, never calls `deleteLater()`.
* **Non‑QObject**: no Qt inheritance, no accidental thread affinity, dead simple
  imports and unit tests.
* **Deterministic disposal**: controllers are disposed when `dispose()` is called.
  `dispose()` is **idempotent**.
* **Minimal API**: a few primitives (`register_controllers`, `auto_register_*`,
  `dispose`) are enough for most screens.
* **Order‑agnostic composition**: controllers can be created in any order; hooks/observables define the dataflow, the composition just manages lifecycle.
* **Qt signal integration**: Use `QtSignalHook` to emit Qt signals when you need Qt event integration for lifecycle or other composition events.

When to use a composition
-------------------------
* You have **multiple controllers** that need coordinated lifecycle management
* You want to **unit‑test** controller composition without importing Qt
* You need a clean way to expose controllers/widgets for Qt layout management

When *not* to use it
--------------------
* A trivial dialog with one controller does not need a composition
* If your app follows an existing MVVM/Redux architecture with a formal state
  store, use that store as the composition root instead

Quick start
-----------

```python
# Build controllers (each owns its own widget and connects to observables)
qty   = SelectionOptionalOptionController(...)
scale = SelectionOptionController(...)
unit  = UnitComboBoxController(...)
rng   = RangeSliderController(...)

# Compose them
comp = BaseControllerComposition()
comp.register_controllers(qty, scale, unit, rng)

# Expose widgets for Qt layout
layout.addWidget(qty.widget_combobox)
layout.addWidget(scale.widget_combobox)
layout.addWidget(unit.widget_combobox)
layout.addWidget(rng.widget_range_slider)

# Later, tear down (idempotent)
comp.dispose()
```

Qt signal integration
--------------------
If you need Qt signals for lifecycle events or other composition-level events, use `QtSignalHook`:

```python
from integrated_widgets.util.qt_signal_hook import QtSignalHook

# Create a signal hook for lifecycle events
lifecycle_hook = QtSignalHook(initial_value="created")

# Connect to the signal
lifecycle_hook.value_changed.connect(on_lifecycle_event)

# Use in your composition
comp = BaseControllerComposition()
comp.register_controllers(controller1, controller2, lifecycle_hook)

# Update the hook value to emit signals
lifecycle_hook.value = "disposed"  # This will emit the Qt signal
```

Controller coordination via observables
---------------------------------------
Controllers are connected through the observables/hooks system, not through the
composition. The composition only manages lifecycle:

```python
# Controllers connect to shared observables
shared_value = ObservableValue(42)
controller_a = SomeController(shared_value)
controller_b = AnotherController(shared_value)

# The composition just manages their lifecycle
comp = BaseControllerComposition()
comp.register_controllers(controller_a, controller_b)
# Controllers are now connected via the shared observable
```

Testing without Qt
------------------
Because the composition is pure Python, you can test controller composition without Qt:

```python
comp = BaseControllerComposition()
comp.register_controllers(mock_controller1, mock_controller2)
assert len(comp.controllers) == 2
comp.dispose()  # Clean teardown
```

Anti‑patterns (what not to do)
------------------------------
* **Do not** store or parent widgets here (keep widgets in controllers or views)
* **Do not** emit Qt signals from the composition (it's not a QObject)
* **Do not** put business logic here (use observables/hooks for coordination)
* **Do not** re‑expose every controller method; the composition manages lifecycle only

Lifecycle summary
-----------------
* `register_controllers(...)` records controllers for lifecycle management
* `dispose()` calls each controller's `dispose()` and is safe to call multiple times
* Controllers handle their own Qt cleanup (timers, signals, widgets)

FAQ
---
**Q: What qualifies as a *controller*?**
A: Any object with a `dispose()` method. The composition doesn't care about concrete
   types; duck typing keeps it flexible.

**Q: How do controllers communicate with each other?**
A: Through the observables/hooks system.

**Q: Can I nest compositions?**
A: Yes. Register a child composition like any controller; it will be disposed in
   reverse order.

**Q: Why doesn't the composition handle GUI thread operations?**
A: Each controller already has its own `gui_invoke` method that handles GUI thread
   marshaling. The composition is pure Python and doesn't need GUI thread operations
   for its core purpose of lifecycle management.

**Q: Can I get Qt signals for lifecycle events?**
A: Yes! Use `QtSignalHook` to create standalone hooks that emit Qt signals when
   they react to value changes. Connect these hooks to observables or other hooks
   in the observables system. This keeps the composition pure Python while providing
   Qt signal integration for applications that need it.

**Q: How do I emit Qt signals from the composition?**
A: The composition itself is pure Python and doesn't emit Qt signals. If you need
   Qt signals for lifecycle events or other composition-level events, use `QtSignalHook`
   to create hooks that emit Qt signals when they react to value changes. This
   maintains the composition's pure Python nature while providing Qt signal integration.
"""
from __future__ import annotations

from typing import Any, final

class BaseControllerComposition:
    """Owns controllers and disposes them safely.

    The composition is a **lifecycle management** layer:
    it knows *which controllers exist* and manages their lifecycle.
    It does not own widgets and it is not a QObject.

    Parameters
    ----------
    logger:
        Optional logger; either a standard `logging.Logger` or a function
        `(level: str, message: str) -> None`.
    """

    # --- lifecycle ---------------------------------------------------------
    def __init__(
        self,
        *,
        logger: Any | None = None,
    ) -> None:
    
        self._controllers: list[Any] = []
        self._disposed: bool = False
        self._logger = logger

    # Context manager convenience
    def __enter__(self) -> "BaseControllerComposition":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401 (standard CM signature)
        self.dispose()

    ###########################################################################
    # Controller Registration
    ###########################################################################

    @final
    def register_controllers(self, *controllers: Any) -> None:
        """Register one or more controllers for lifecycle management.

        Controllers are stored for disposal. Order does not matter since
        controllers communicate via the hook system, not direct references.
        """
        for c in controllers:
            self._controllers.append(c)

    def auto_register_controllers(self, source: Any | None = None) -> int:
        """Heuristically discover controllers on an object and register them.

        A *controller* is any attribute whose value has a callable `dispose`.
        Methods and private names (`_foo`) are ignored. Returns the number of
        **new** registrations performed by this call.
        """
        if source is None:
            source = self

        seen_before = set(map(id, self._controllers))
        new_count = 0
        for name in dir(source):
            if name.startswith("_"):
                continue
            try:
                value = getattr(source, name)
            except Exception:
                continue
            if callable(value):
                continue
            dispose = getattr(value, "dispose", None)
            if callable(dispose) and id(value) not in seen_before:
                self.register_controllers(value)
                new_count += 1
        return new_count


    ###########################################################################
    # Disposal
    ###########################################################################

    @final
    def dispose(self) -> None:
        """Dispose registered controllers. Idempotent.

        Exceptions during individual controller disposal are caught and logged,
        and cleanup proceeds with the remaining controllers. Calling `dispose()`
        multiple times is safe.
        
        Note: This method disposes controllers synchronously. If controllers have
        pending Qt operations (timers, queued signals), they should handle their
        own cleanup in their dispose() methods.
        """
        if self._disposed:
            return
        self._disposed = True
        
        # Dispose all controllers (order doesn't matter in this architecture)
        for c in self._controllers:
            try:
                dispose = getattr(c, "dispose", None)
                if callable(dispose):
                    dispose()
            except Exception as exc:  # pragma: no cover - best‑effort cleanup
                self._log("warning", f"Controller dispose raised: {exc!r}")
        
        # Clear the list after all controllers are disposed
        self._controllers.clear()

    ###########################################################################
    # Utility Properties and Methods
    ###########################################################################

    @property
    def controllers(self) -> tuple[Any, ...]:
        """Tuple view of registered controllers in registration order."""
        return tuple(self._controllers)

    @property
    def is_disposed(self) -> bool:
        """Whether `dispose()` has been called."""
        return self._disposed

    def _log(self, level: str, msg: str) -> None:
        lg = self._logger
        if lg is None:
            return
        # Accept both function‑style and logging.Logger‑style
        try:
            method = getattr(lg, level)
        except Exception:
            method = None
        if callable(method):
            method(msg)
        elif callable(lg):  # type: ignore[truthy-function]
            lg(level, msg)  # type: ignore[misc]
