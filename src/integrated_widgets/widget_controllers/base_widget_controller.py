from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, Callable, Any, Mapping, final, TypeVar, Generic
from logging import Logger
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QWidget

# BAB imports
from observables import BaseObservable

# Local imports
from ..util.resources import log_bool, log_msg

PHK = TypeVar("PHK")
"""Primary Hook Keys"""
SHK = TypeVar("SHK")
"""Secondary Hook Keys"""

class _Forwarder(QObject):
    trigger = Signal()

class BaseWidgetController(BaseObservable[PHK, SHK], Generic[PHK, SHK]):
    """Base class for controllers that use hooks for data management.

    **ARCHITECTURE SUMMARY:**
    Controllers inherit from this base class and implement ONLY 4 methods:
    
    1. `initialize_widgets()` - Create widgets (REQUIRED - abstract)
    2. `_invalidate_widgets_impl()` - Update UI from data (REQUIRED - abstract)
    3. `_set_component_values()` - Custom value setting logic (OPTIONAL - can override)
    
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
    2. `_invalidate_widgets_impl()` - Update widgets when component values change (REQUIRED)
    3. `_set_component_values()` - Custom logic for setting component values (OPTIONAL - can override)

    **DO NOT override (marked with @final):**
    - `invalidate_widgets()` - Base controller handles change notifications
    - `dispose()`, `dispose_before_children()`, `dispose_after_children()` - Base controller handles lifecycle
    - `set_block_signals()`, `_internal_update()` - Base controller manages signal handling
    - Any other methods - Base controller provides complete functionality

    **How it works:**
    1. Base controller automatically calls `invalidate_widgets()` when values change
    2. This triggers `_invalidate_widgets_impl()` to update the UI
    3. Widget changes trigger `_set_component_values()` to update data
    4. All change notifications and binding updates are handled automatically
    """

    def __init__(
        self,
        initial_component_values: dict[PHK, Any],
        *,
        verification_method: Optional[Callable[[Mapping[PHK, Any]], tuple[bool, str]]] = None,
        secondary_hook_callbacks: dict[SHK, Callable[[Mapping[PHK, Any]], Any]] = {},
        parent: Optional[QObject] = None,
        logger: Optional[Logger] = None,

    ) -> None:
        # Initialize BaseObservable with empty component values and hooks
        super().__init__(
            initial_component_values_or_hooks=initial_component_values,
            verification_method=verification_method,
            secondary_hook_callbacks=secondary_hook_callbacks,
            act_on_invalidation_callback=lambda: self.invalidate_widgets(),
            logger=logger
        )

        # Store parent reference for internal use
        self._parent: Optional[QObject] = parent
        
        # Create a QObject to handle Qt parent-child relationships
        self._qt_object = QObject(parent)
        
        # Create forwarder as child of the Qt object for proper cleanup
        self._forwarder = _Forwarder(self._qt_object)
        self._forwarder.trigger.connect(self.invalidate_widgets, Qt.ConnectionType.QueuedConnection)
        
        # Initialize internal state
        self._blocking_objects: set[object] = set()
        self._internal_widget_update: bool = False
        self._is_disabled: bool = False
        self._is_disposed: bool = False
        self._logger: Optional[Logger] = logger
      
        # Create owner widget as child of the Qt object
        if isinstance(parent, QWidget):
            self._owner_widget = parent
        else:
            # Create a new QWidget as child of the parent (or None if no parent)
            self._owner_widget = QWidget(parent)  # type: ignore[arg-type]
        
        # Mark as initializing to prevent recursive widget updates
        self._is_initializing = True
        
        with self._internal_update():
            self.set_block_signals(self)
            self._initialize_widgets()
            self.set_unblock_signals(self)

        # Automatically update widgets after initialization to ensure they display current values
        with self._internal_update():
            self.invalidate_widgets()
        
        # Mark initialization as complete
        self._is_initializing = False

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "Controller initialized")

    ###########################################################################
    # Abstract Methods - To be implemented by subclasses
    ###########################################################################

    @abstractmethod
    def _initialize_widgets(self) -> None:
        """Create and set up widget instances.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to create their widgets.
        This is called during initialization before any other operations.
        
        **What to do here:**
        - Create all widget instances (QWidget, QLabel, etc.)
        - Set up widget properties and initial states
        - Connect widget signals to internal handlers
        - Store widgets as instance attributes (e.g., self._label, self._button)
        
        **What NOT to do here:**
        - Don't update widget values from component values (that's handled by invalidate_widgets)
        - Don't set up bindings (base controller handles this)
        - Don't call update methods (base controller calls them automatically)
        - Don't call self._internal_update() (base controller handles this)
        - Don't use block_signals() or unblock_signals() (base controller handles this)
        """
        raise NotImplementedError

    @abstractmethod
    def _invalidate_widgets_impl(self) -> None:
        """
        Invalidate the widgets implementation.

        **REQUIRED OVERRIDE:** Controllers must implement this method to invalidate their widgets.
        This is called automatically by the base controller when the component values have been changed.
        """
        raise NotImplementedError

    ###########################################################################
    # Public API Properties
    ###########################################################################

    @property
    @final
    def owner_widget(self) -> QWidget:
        """
        Get the owner widget.
        """
        return self._owner_widget

    @property
    def is_disabled(self) -> bool:
        return self._is_disabled
    
    @property
    def is_enabled(self) -> bool:
        return not self._is_disabled

    ###########################################################################
    # Signal Management and Blocking
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
    # Widget Update and Synchronization
    ###########################################################################

    @final
    def invalidate_widgets(self) -> None:
        """
        Invalidate the widgets.

        This method is called automatically by the base controller when component values have been changed and the widgets should be invalidated.
        It automatically wraps the actual implementation in the internal update context.

        **DO NOT OVERRIDE:** Controllers should implement _invalidate_widgets_impl() instead.
        """
        if self._is_disposed:
            return  # Silently return if disposed to avoid errors during cleanup
        
        with self._internal_update():
            self.set_block_signals(self)
            try:
                log_msg(self, "invalidate_widgets", self._logger, f"Invalidating widgets with component values: {self.primary_values}")
                self._invalidate_widgets_impl()
            finally:
                self.set_unblock_signals(self)

    @final
    def _set_incomplete_primary_component_values(self, incomplete_primary_component_values: dict[PHK, Any]) -> None:
        """
        Update the widgets from the currently set component values.
        
        **DO NOT OVERRIDE:** This method is part of the base controller's change notification system.
        Controllers should implement invalidate_widgets() instead.

        **This method is supposed to be called in the end of an _on_widget_..._changed() method.**

        """

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")
        if self._is_disabled:
            raise ValueError("Controller is disabled")
        
        complete_primary_component_values: dict[PHK, Any] = {**self.primary_values, **incomplete_primary_component_values}

        if self._verification_method is not None:
            success, msg = self._verification_method(complete_primary_component_values)
            if not success:
                log_bool(self, "_set_incomplete_primary_component_values", self._logger, False, msg)
                self.invalidate_widgets()
                return
            
        self.set_block_signals(self)
            
        self._set_component_values(complete_primary_component_values, notify_binding_system=True)
        try:
            with self._internal_update():
                self.invalidate_widgets()
        except Exception as e:
            log_bool(self, "_set_incomplete_primary_component_values", self._logger, False, str(e))
        finally:
            self.set_unblock_signals(self)
            log_bool(self, "_set_incomplete_primary_component_values", self._logger, True, "Widgets updated")

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    @final
    def dispose(self) -> None:
        """Dispose of the controller and clean up resources."""
        if self._is_disposed:
            return
        
        self._is_disposed = True
        
        # Disconnect all hooks first to prevent further updates
        try:
            for hook in self.hook_dict.values():
                hook.deactivate()
        except Exception as e:
            log_bool(self, "dispose", self._logger, False, f"Error deactivating hooks: {e}")
        
        # Disconnect forwarder signal
        if hasattr(self, '_forwarder'):
            try:
                self._forwarder.trigger.disconnect()
            except Exception as e:
                log_bool(self, "dispose", self._logger, False, f"Error disconnecting forwarder: {e}")
        
        # Clean up Qt object and all its children
        if hasattr(self, '_qt_object'):
            try:
                self._qt_object.deleteLater()
            except Exception as e:
                log_bool(self, "dispose", self._logger, False, f"Error deleting Qt object: {e}")

        log_bool(self, f"{self.__class__.__name__} disposed", self._logger, True)

    def __del__(self) -> None:
        """Ensure proper cleanup when the object is garbage collected."""
        if not self._is_disposed:
            self.dispose()

