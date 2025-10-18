"""
Qt signal hook for observables integration
=========================================

**`QtSignalHook`** is a standalone hook that can be connected to observables and
other hooks in the observables system. When the hook reacts to value changes,
it emits Qt signals, allowing Qt applications to integrate with the observables
system.

The hook inherits from `QObject` and provides a `value_changed` signal that
emits whenever the hook's value changes through the observables system.

Usage
-----

```python
from PySide6.QtCore import QObject, Signal

# Create the signal hook
signal_hook = QtSignalHook(initial_value=42)

# Connect to the signal
signal_hook.value_changed.connect(on_value_changed)

# Connect to other hooks or observables
other_hook.connect_hook(signal_hook)

# When other_hook's value changes, signal_hook will react and emit the signal
```

Design principles
-----------------
* **Standalone**: The hook is independent and can be connected to any observable
* **Qt integration**: Emits Qt signals when reacting to value changes
* **Observables system**: Fully integrates with the observables/hooks system
* **Reactive**: Uses the hook system's reaction mechanism to emit signals
"""

from __future__ import annotations

from typing import Optional, TypeVar, Generic
from logging import Logger

from PySide6.QtCore import QObject, Signal, SignalInstance

from observables import Hook
from observables.core import DEFAULT_NEXUS_MANAGER, NexusManager, ListeningBase
from observables._hooks.hook_bases.full_hook_base import FullHookBase

T = TypeVar("T")

# Custom metaclass to resolve the conflict between QObject and Protocol metaclasses
class IQtSignalHookMeta(type(QObject), type(FullHookBase)): # type: ignore
    pass

class IQtSignalHook(QObject, FullHookBase[T], Generic[T], metaclass=IQtSignalHookMeta):
    """
    Standalone hook that emits Qt signals when reacting to value changes.
    
    This hook can be connected to any observable or other hook in the observables
    system. When the connected observable changes, this hook will react and emit
    a Qt signal with the new value.
    """
    
    # Qt signal that emits when the hook's value changes
    value_changed = Signal(object)  # Emits the new value
    
    def __init__(
        self,
        initial_value_or_hook: T | Hook[T],
        *,
        signal: Optional[SignalInstance] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
    ) -> None:

        # Initialize QObject first
        QObject.__init__(self)
        
        # Override the signal if provided (must be done after QObject.__init__)
        if signal is not None:
            self.value_changed = signal
        
        # Initialize ListeningBase
        ListeningBase.__init__(self, logger) # type: ignore

        if isinstance(initial_value_or_hook, Hook):
            initial_value: T = initial_value_or_hook.value # type: ignore
        else:
            initial_value = initial_value_or_hook
        
        # Initialize Hook with the initial value
        FullHookBase.__init__( # type: ignore
            self,
            value=initial_value,
            nexus_manager=nexus_manager,
            logger=logger
        )

        if isinstance(initial_value_or_hook, Hook):
            self.connect_hook(initial_value_or_hook, initial_sync_mode="use_target_value") # type: ignore

    def react_to_value_changed(self) -> None:
        """React to value changes by emitting the Qt signal."""
        value: T = self.value
        self.value_changed.emit(value)
    
    def dispose(self) -> None:
        """Dispose of the hook and clean up Qt resources."""
        # Disconnect from the observables system first
        try:
            self.disconnect_hook()
        except Exception:
            # Hook may already be disconnected or in an invalid state
            pass
        
        # Clean up Qt object
        try:
            self.deleteLater()
        except RuntimeError:
            # Qt object may have been deleted already
            pass
    
    def __del__(self) -> None:
        """Ensure proper cleanup when the object is garbage collected."""
        try:
            self.dispose()
        except Exception:
            # Ignore errors during garbage collection
            pass