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

Nested compositions
-------------------
You can nest compositions to create hierarchical controller management:

```python
# Create child compositions
child_comp_a = BaseControllerComposition()
child_comp_a.register_controllers(controller_a1, controller_a2)

child_comp_b = BaseControllerComposition()
child_comp_b.register_controllers(controller_b1, controller_b2)

# Create parent composition
parent_comp = BaseControllerComposition()
parent_comp.register_controllers(child_comp_a, child_comp_b, standalone_controller)

# Auto-registration will also find nested compositions
parent_comp.auto_register_controllers()  # Finds any unregistered controllers

# Disposal happens in hierarchical order (type-based):
# 1. All BaseController instances disposed first (leaf nodes)
# 2. Then all BaseControllerComposition instances disposed (parent nodes)
# This ensures proper cleanup regardless of registration order
parent_comp.dispose()
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
A: Only `BaseController` and `BaseControllerComposition` instances can be registered.
   This ensures proper disposal order and type safety. The composition maintains
   hierarchical disposal order based on type relationships, not registration order.

**Q: How do controllers communicate with each other?**
A: Through the observables/hooks system.

**Q: Can I nest compositions?**
A: Yes. Register a child composition like any controller. Disposal order is based
   on type hierarchy: BaseController instances are disposed first (leaf nodes),
   then BaseControllerComposition instances (parent nodes). This ensures proper
   cleanup regardless of registration order.

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

**Q: What does the "unregistered controllers" warning mean?**
A: This warning appears when controllers are found during disposal that weren't
   explicitly registered via `register_controllers()`. This usually indicates a
   developer oversight where controllers were created and stored as attributes
   but not properly registered for lifecycle management. The composition will
   auto-register and dispose these controllers, but you should fix the code to
   explicitly register all controllers to ensure proper resource cleanup.

**Q: How can I disable the unregistered controllers warning?**
A: Set `warn_on_unregistered_controllers=False` when creating the composition.
   This disables the global Python warning while keeping local logging.
"""
from __future__ import annotations

import warnings
from typing import Any, final, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_controller import BaseController

class BaseControllerComposition:
    """Owns controllers and disposes them safely.

    The composition is a **lifecycle management** layer:
    it knows *which controllers exist* and manages their lifecycle.
    It does not own widgets and it is not a QObject.

    **IMPORTANT:** When using this composition, you must explicitly register all controllers via `register_controllers()` or `auto_register_controllers()`. Failure to do so will result in unregistered controllers being disposed during disposal, which can lead to resource leaks and unexpected behavior.

    Parameters
    ----------
    logger:
        Optional logger; either a standard `logging.Logger` or a function
        `(level: str, message: str) -> None`.
    warn_on_unregistered_controllers:
        If True (default), emit Python warnings when unregistered controllers
        are found during disposal. Set to False to disable global warnings
        while keeping local logging.
    """

    # --- lifecycle ---------------------------------------------------------
    def __init__(
        self,
        *,
        logger: Any | None = None,
        warn_on_unregistered_controllers: bool = True,
    ) -> None:
    
        self._controllers: list[BaseController | BaseControllerComposition] = []
        self._disposed: bool = False
        self._logger = logger
        self._warn_on_unregistered_controllers = warn_on_unregistered_controllers

    # Context manager convenience
    def __enter__(self) -> "BaseControllerComposition":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401 (standard CM signature)
        self.dispose()

    ###########################################################################
    # Type Validation
    ###########################################################################

    def _is_valid_registrable_type(self, obj: Any) -> bool:
        """Check if an object is a valid type for registration.
        
        Only BaseController and BaseControllerComposition instances are allowed.
        This ensures proper disposal order and type safety.
        """
        # Check if it's a BaseControllerComposition
        if isinstance(obj, BaseControllerComposition):
            return True
        
        # Check if it's a BaseController or subclass
        try:
            from .base_controller import BaseController
            if isinstance(obj, BaseController):
                return True
        except ImportError:
            pass
        
        return False

    ###########################################################################
    # Controller Registration
    ###########################################################################

    @final
    def register_controllers(self, *controllers: BaseController | BaseControllerComposition) -> None:
        """Register one or more controllers for lifecycle management.

        Only BaseController and BaseControllerComposition instances are allowed.
        Registration order does not matter for disposal - the composition
        maintains proper hierarchical disposal order based on type relationships.
        Controllers communicate via the hook system, not direct references.
        
        Parameters
        ----------
        *controllers : BaseController | BaseControllerComposition
            Controllers and compositions to register for lifecycle management.
            
        Raises
        ------
        TypeError
            If any argument is not a BaseController or BaseControllerComposition instance.
        """
        for controller in controllers:
            if not self._is_valid_registrable_type(controller):
                raise TypeError(
                    f"Only BaseController and BaseControllerComposition instances can be registered. "
                    f"Got: {type(controller).__name__}"
                )
            self._controllers.append(controller)

    def auto_register_controllers(self, source: Any | None = None) -> int:
        """Heuristically discover controllers on an object and register them."""
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
            # Only register valid types and avoid duplicates
            if (self._is_valid_registrable_type(value) and 
                id(value) not in seen_before):
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

        # Perform the auto registration of controllers, just to be safe!
        number_of_found_unregistered_controllers = self.auto_register_controllers()
        if number_of_found_unregistered_controllers > 0:
            warning_msg = f"Found {number_of_found_unregistered_controllers} unregistered controllers during disposal. This may indicate controllers were created but not properly registered via register_controllers(). Consider explicitly registering all controllers to ensure proper resource cleanup."
            
            # Log the warning locally
            self._log("warning", warning_msg)
            
            # Also emit a global Python warning for better visibility (if enabled)
            if self._warn_on_unregistered_controllers:
                warnings.warn(
                    warning_msg,
                    UserWarning,
                    stacklevel=2
                )
        
        # Dispose controllers in proper hierarchical order
        # 1. First dispose all BaseController instances (leaf nodes)
        # 2. Then dispose all BaseControllerComposition instances (parent nodes)
        # This ensures proper cleanup hierarchy regardless of registration order
        
        # Separate controllers by type
        base_controllers = []
        compositions = []
        
        for controller in self._controllers:
            if isinstance(controller, BaseControllerComposition):
                compositions.append(controller)
            else:
                # Must be a BaseController (type validation ensures this)
                base_controllers.append(controller)
        
        # Dispose base controllers first (leaf nodes)
        for controller in base_controllers:
            try:
                controller.dispose()
            except Exception as exc:  # pragma: no cover - best‑effort cleanup
                self._log("warning", f"BaseController dispose raised: {exc!r}")
        
        # Then dispose compositions (parent nodes)
        for composition in compositions:
            try:
                composition.dispose()
            except Exception as exc:  # pragma: no cover - best‑effort cleanup
                self._log("warning", f"BaseControllerComposition dispose raised: {exc!r}")
        
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
