from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, Callable, Any, Mapping, final, TypeVar, Generic
from logging import Logger
from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget

# BAB imports
from observables import BaseObservable

# Local imports
from ..util.resources import log_bool, log_msg

HK = TypeVar("HK")
EHK = TypeVar("EHK")

class _Forwarder(QObject):
    trigger = Signal()

class BaseWidgetController(BaseObservable[HK, EHK], Generic[HK, EHK]):
    """Base class for controllers that use hooks for data management.

    **ARCHITECTURE SUMMARY:**
    Controllers inherit from this base class and implement ONLY 4 methods:
    
    1. `initialize_widgets()` - Create widgets (REQUIRED - abstract)
    2. `_fill_widgets_from_component_values()` - Update UI from data (REQUIRED - abstract)
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
    2. `_fill_widgets_from_component_values()` - Update widgets when component values change (REQUIRED)
    3. `_set_component_values()` - Custom logic for setting component values (OPTIONAL - can override)

    **DO NOT override (marked with @final):**
    - `_on_component_values_changed()` - Base controller handles change notifications
    - `dispose()`, `dispose_before_children()`, `dispose_after_children()` - Base controller handles lifecycle
    - `set_block_signals()`, `_internal_update()` - Base controller manages signal handling
    - Any other methods - Base controller provides complete functionality

    **How it works:**
    1. Base controller automatically calls `_on_component_values_changed()` when values change
    2. This triggers `apply_component_values_to_widgets()` to update the UI
    3. Widget changes trigger `_set_component_values()` to update data
    4. All change notifications and binding updates are handled automatically
    """

    def __init__(
            self,
            initial_component_values: dict[HK, Any],
            *,
            verification_method: Optional[Callable[[Mapping[HK, Any]], tuple[bool, str]]] = None,
            emitter_hook_callbacks: dict[EHK, Callable[[Mapping[HK, Any]], Any]] = {},
            parent: Optional[QObject] = None,
            logger: Optional[Logger] = None,

    ) -> None:
        # Initialize BaseObservable with empty component values and hooks
        super().__init__(
            initial_component_values=initial_component_values,
            verification_method=verification_method,
            emitter_hook_callbacks=emitter_hook_callbacks,
            logger=logger
        )
        
        self._parent: Optional[QObject] = parent
        # tie the forwarder to the parent for safe disposal
        self._forwarder = _Forwarder(parent)
        self._forwarder.trigger.connect(self.__on_component_values_changed, Qt.ConnectionType.QueuedConnection)
        self._blocking_objects: set[object] = set()
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        self._logger: Optional[Logger] = logger
      
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
        
        with self._internal_update():
            self.set_block_signals(self)
            self._initialize_widgets()
            self.set_unblock_signals(self)

        # Automatically update widgets after initialization to ensure they display current values
        self.__internal_apply_component_values_to_widgets(self._component_values)
        
        # Mark initialization as complete
        self._is_initializing = False

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "Controller initialized")

    ###########################################################################
    # Forwarding - DO NOT OVERRIDE THESE METHODS
    ###########################################################################

    def _act_on_invalidation(self, keys: set[HK]) -> None:
        self.__on_component_values_changed()

    @final
    @Slot()
    def __on_component_values_changed(self) -> None:
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

        **This method is only supposed to be called by the base controller.**

        """
        if self._blocking_objects or getattr(self, '_is_initializing', False):
            return
        self.set_block_signals(self)
        self.apply_component_values_to_widgets()

    def apply_component_values_to_widgets(self) -> None:
        """
        Update the widgets from the currently set component values.
        
        **DO NOT OVERRIDE:** This method is part of the base controller's change notification system.
        Controllers should implement _fill_widgets_from_component_values() instead.

        This method ensures that filling the widgets does not trigger a change notification.
        """

        # Calling the internal method with an empty dict will update the widgets from the current component values.
        self.__internal_apply_component_values_to_widgets({})

    def _update_component_values_and_widgets(self, altered_component_values: dict[HK, Any]) -> None:
        """
        Update the widgets from the currently set component values.
        
        **DO NOT OVERRIDE:** This method is part of the base controller's change notification system.
        Controllers should implement _fill_widgets_from_component_values() instead.

        **This method is upposed to be called in the end of an _on_widget_..._changed() method.**

        """
        self.__internal_apply_component_values_to_widgets(altered_component_values)
        self._set_component_values(altered_component_values, notify_binding_system=True)

    def __internal_apply_component_values_to_widgets(self, altered_component_values: dict[HK, Any]) -> None:
        """
        Update the widgets from the component values.

        This method combines the altered component values with the current component values and then calls _fill_widgets_from_component_values().

        This method should be called when widgets have been changed and before the notifications are sent.
        
        **DO NOT OVERRIDE:** This method is part of the base controller's change notification system.
        Controllers should implement _fill_widgets_from_component_values() instead.

        **This method is only supposed to be called by the base controller.**
        """

        complete_component_values: dict[HK, Any] = {**self._component_values, **altered_component_values}

        if self._verification_method is not None:
            success, msg = self._verification_method(complete_component_values)
            if not success:
                log_bool(self, "apply_component_values_to_widgets", self._logger, False, msg)
                self.apply_component_values_to_widgets()
                return

        self.set_block_signals(self)
        try:
            with self._internal_update():
                self._fill_widgets_from_component_values(complete_component_values)
        except Exception as e:
            log_bool(self, "apply_component_values_to_widgets", self._logger, False, str(e))
        finally:
            self.set_unblock_signals(self)
            log_bool(self, "apply_component_values_to_widgets", self._logger, True, "Widgets updated")

    def disable_widgets(self) -> None:
        """
        Disable all widgets. This also deactivates all hooks and removes all bindings.
        """

        self.set_block_signals(self)

        for hook in self._component_hooks.values():
            hook.deactivate()

        with self._internal_update():
            self._disable_widgets()

    def enable_widgets(self, initial_component_values: dict[HK, Any]) -> None:
        """
        Enable all widgets. This also activates all hooks and restores all bindings.
        """
        for key, hook in self._component_hooks.items():
            initial_value: Any = initial_component_values[key]
            hook.activate(initial_value)

        with self._internal_update():
            self._enable_widgets(initial_component_values)

        self.set_unblock_signals(self)

    @property
    @final
    def owner_widget(self) -> QWidget:
        """
        Get the owner widget.
        """
        return self._owner_widget

    ###########################################################################
    # To be implemented by subclasses
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
        - Don't update widget values from component values (that's handled by update_widgets_from_component_values)
        - Don't set up bindings (base controller handles this)
        - Don't call update methods (base controller calls them automatically)
        - Don't call self._internal_update() (base controller handles this)
        - Don't use block_signals() or unblock_signals() (base controller handles this)
        """
        raise NotImplementedError

    @abstractmethod
    def _fill_widgets_from_component_values(self, component_values: dict[HK, Any]) -> None:
        """Update widgets when component values change.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to update their widgets.
        This is called automatically by the base controller when component values change.
        
        **What to do here:**
        - Read current component values using self._get_component_value("key")
        - Update widget properties (text, checked state, etc.) to match component values
        
        **What NOT to do here:**
        - Don't modify component values (that creates infinite loops)
        - Don't call _set_component_values() (base controller handles this)
        - Don't emit signals (base controller handles notifications)

        Args:
            component_values: The component values to update the widgets from.

        """
        raise NotImplementedError
    
    def _disable_widgets(self) -> None:
        """
        Disable all widgets.

        **REQUIRED OVERRIDE:** Controllers must implement this method to disable their widgets.
        This is called automatically by the base controller when the controller is disabled.

        **What to do here:**
        - Disable all widgets
        - Use self._internal_update() context manager for widget modifications
        """

        raise NotImplementedError
    
    def _enable_widgets(self, initial_component_values: dict[HK, Any]) -> None:
        """
        Enable all widgets.

        **REQUIRED OVERRIDE:** Controllers must implement this method to enable their widgets.
        This is called automatically by the base controller when the controller is enabled.

        **What to do here:**
        - Enable all widgets
        - Use self._internal_update() context manager for widget modifications
        """
        raise NotImplementedError

    def dispose_before_children(self) -> None:
        """
        **OPTIONAL OVERRIDE:** Method for controllers to disconnect signals before children are deleted.
        
        Controllers should implement this method to disconnect signals before children are deleted.
        This method is called by the base controller when the controller is disposed.
        """
        pass

    def dispose_after_children(self) -> None:
        """
        **OPTIONAL OVERRIDE:** Method for controllers to perform actions after children were scheduled for deletion.
        
        Controllers should implement this method to perform actions after children were scheduled for deletion.
        This method is called by the base controller when the controller is disposed.
        """
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

        log_bool(self, f"{self.__class__.__name__} disposed", self._logger, True)