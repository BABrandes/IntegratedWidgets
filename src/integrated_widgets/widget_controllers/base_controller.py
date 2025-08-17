from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, Callable, Any, Mapping, final

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget

from observables import BaseObservable


class _Forwarder(QObject):
    trigger = Signal()


class BaseObservableController(BaseObservable):
    """Base class for controllers that use hooks for data management.

    **ARCHITECTURE SUMMARY:**
    Controllers inherit from this base class and implement ONLY 4 methods:
    
    1. `initialize_widgets()` - Create widgets (REQUIRED - abstract)
    2. `update_widgets_from_component_values()` - Update UI from data (REQUIRED - abstract)
    3. `update_component_values_from_widgets()` - Update data from UI (REQUIRED - abstract)
    4. `_set_component_values()` - Custom value setting logic (OPTIONAL - can override)
    
    The base controller handles ALL other functionality automatically:
    - Change notifications and binding updates
    - Widget update scheduling and signal management
    - Lifecycle management and disposal
    - Hook synchronization and error handling

    Inherits from BaseObservable and provides hook-based data synchronization
    with automatic change notifications and bidirectional bindings.

    **Architecture Rules:**
    Controllers should ONLY override these 4 methods:
    1. `initialize_widgets()` - Create and set up widget instances (REQUIRED)
    2. `update_widgets_from_component_values()` - Update widgets when component values change (REQUIRED)
    3. `update_component_values_from_widgets()` - Update component values from widget changes (REQUIRED)
    4. `_set_component_values()` - Custom logic for setting component values (OPTIONAL - can override)

    **DO NOT override (marked with @final):**
    - `_on_component_values_changed()` - Base controller handles change notifications
    - `dispose()`, `dispose_before_children()`, `dispose_after_children()` - Base controller handles lifecycle
    - `set_block_signals()`, `_internal_update()` - Base controller manages signal handling
    - Any other methods - Base controller provides complete functionality

    **How it works:**
    1. Base controller automatically calls `_on_component_values_changed()` when values change
    2. This triggers `update_widgets_from_component_values()` to update the UI
    3. Widget changes trigger `update_component_values_from_widgets()` to update data
    4. All change notifications and binding updates are handled automatically
    """

    def __init__(
            self,
            initial_component_values: dict[str, Any],
            *,
            verification_method: Optional[Callable[[Mapping[str, Any]], tuple[bool, str]]] = None,
            parent: Optional[QObject] = None,
            
    ) -> None:
        # Initialize BaseObservable with empty component values and hooks
        super().__init__(
            initial_component_values=initial_component_values,
            verification_method=verification_method
        )
        
        self._parent: Optional[QObject] = parent
        # tie the forwarder to the parent for safe disposal
        self._forwarder = _Forwarder(parent)
        self._forwarder.trigger.connect(self._on_component_values_changed, Qt.ConnectionType.QueuedConnection)
        self._blocking_objects: set[object] = set()
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        
        # Create owner widget before initializing widgets
        self._owner_widget: QWidget = self._parent if isinstance(self._parent, QWidget) else QWidget()
        
        # Auto-dispose when parent is destroyed (if QObject parent provided)
        if parent is not None:
            try:
                parent.destroyed.connect(lambda *_: self.dispose())  # type: ignore[attr-defined]
            except Exception:
                pass
        
        # Mark as initializing to prevent recursive widget updates
        self._is_initializing = True
        
        self.initialize_widgets()
        # Automatically update widgets after initialization to ensure they display current values
        self.update_widgets_from_component_values()
        
        # Mark initialization as complete
        self._is_initializing = False

    ###########################################################################
    # Forwarding - DO NOT OVERRIDE THESE METHODS
    ###########################################################################

    def _act_on_invalidation(self, keys: set[str]) -> None:
        self._on_component_values_changed()

    @final
    @Slot()
    def _on_component_values_changed(self) -> None:
        """Handle component value changes and trigger widget updates.
        
        **DO NOT OVERRIDE:** This method is part of the base controller's change notification system.
        Controllers should implement update_widgets_from_component_values() instead.
        
        **What this method does:**
        - Checks if updates should be blocked (initialization, signal blocking)
        - Calls update_widgets_from_component_values() to update the UI
        - Manages signal blocking to prevent infinite loops
        
        **If you need custom change handling:**
        - Override update_widgets_from_component_values() instead
        - Use the _internal_update() context manager for widget modifications
        - Don't call this method directly
        """
        if self._blocking_objects or getattr(self, '_is_initializing', False):
            return
        self.set_block_signals(self)
        try:
            self.update_widgets_from_component_values()
        finally:
            self.set_unblock_signals(self)

    ###########################################################################
    # To be implemented by subclasses
    ###########################################################################

    @abstractmethod
    def initialize_widgets(self) -> None:
        """Create and set up widget instances.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to create their widgets.
        This is called during initialization before any other operations.
        
        **What to do here:**
        - Create all widget instances (QWidget, QLabel, etc.)
        - Set up widget properties and initial states
        - Connect widget signals to internal handlers
        - Store widgets as instance attributes (e.g., self._label, self._button)
        
        **What NOT to do here:**
        - Don't update widget values from component values (that's handled by update_widgets_from_component_values)
        - Don't set up bindings (base controller handles this)
        - Don't call update methods (base controller calls them automatically)
        """
        raise NotImplementedError

    @abstractmethod
    def update_widgets_from_component_values(self) -> None:
        """Update widgets when component values change.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to update their widgets.
        This is called automatically by the base controller when component values change.
        
        **What to do here:**
        - Read current component values using self._get_component_value("key")
        - Update widget properties (text, checked state, etc.) to match component values
        - Use self._internal_update() context manager for widget modifications
        
        **What NOT to do here:**
        - Don't modify component values (that creates infinite loops)
        - Don't call _set_component_values() (base controller handles this)
        - Don't emit signals (base controller handles notifications)
        """
        raise NotImplementedError

    @abstractmethod
    def update_component_values_from_widgets(self) -> None:
        """Update component values from widget changes.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to read from widgets.
        This is called when widgets emit change signals (e.g., textChanged, stateChanged).
        
        **What to do here:**
        - Read current widget states (text, checked state, etc.)
        - Call self._set_component_values(("key", value), notify_binding_system=True)
        - Handle any validation or conversion logic
        
        **What NOT to do here:**
        - Don't update widgets (that's handled by update_widgets_from_component_values)
        - Don't call update_widgets_from_component_values() (base controller handles this)
        - Don't emit signals (base controller handles notifications)
        """
        raise NotImplementedError
    
    ###########################################################################
    # Lifecycle
    ###########################################################################
    
    @final
    def dispose_before_children(self) -> None:
        """Hook for controllers to disconnect signals before children are deleted."""
        pass

    @final
    def dispose_after_children(self) -> None:
        """Hook after children were scheduled for deletion."""
        pass

    ###########################################################################
    # Blocking
    ###########################################################################

    @final
    @property
    def is_blocking_signals(self) -> bool:
        return bool(self._blocking_objects)

    @final
    def set_block_signals(self, obj: object) -> None:
        self._blocking_objects.add(obj)

    @final
    def set_unblock_signals(self, obj: object) -> None:
        if obj in self._blocking_objects:
            self._blocking_objects.remove(obj)

    @final
    @contextmanager
    def _internal_update(self):
        """Context manager for internal widget updates."""
        self._internal_widget_update = True
        try:
            yield
        finally:
            self._internal_widget_update = False

    ###########################################################################
    # Lifecycle
    ###########################################################################

    @final
    def dispose(self) -> None:
        """Dispose of the controller and clean up resources."""
        if self._is_disposed:
            return
        
        self._is_disposed = True
        
        # Disconnect forwarder
        if hasattr(self, '_forwarder'):
            self._forwarder.trigger.disconnect()
        
        # Call disposal hooks
        self.dispose_before_children()
        self.dispose_after_children()




