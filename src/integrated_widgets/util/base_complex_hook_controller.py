from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from typing import Optional, Callable, Any, Mapping, final, TypeVar, Generic
from logging import Logger
from PySide6.QtCore import QObject

# BAB imports
from observables import BaseObservable, OwnedHookLike

# Local imports
from ..util.resources import log_bool, log_msg
from .base_controller import BaseController

PHK = TypeVar("PHK")
"""Primary Hook Keys"""
SHK = TypeVar("SHK")
"""Secondary Hook Keys"""

PHV = TypeVar("PHV")
"""Primary Hook Values"""
SHV = TypeVar("SHV")
"""Secondary Hook Values"""


class BaseComplexHookController(BaseController, BaseObservable[PHK, SHK, PHV, SHV], Generic[PHK, SHK, PHV, SHV]):
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
        initial_component_values: dict[PHK, PHV],
        *,
        verification_method: Optional[Callable[[Mapping[PHK, PHV]], tuple[bool, str]]] = None,
        secondary_hook_callbacks: dict[SHK, Callable[[Mapping[PHK, PHV]], SHV]] = {},
        parent: Optional[QObject] = None,
        logger: Optional[Logger] = None,

    ) -> None:

        BaseController.__init__(
            self,
            parent=parent,
            logger=logger
        )
        BaseObservable.__init__(
            self,
            initial_component_values_or_hooks=initial_component_values,
            verification_method=verification_method,
            secondary_hook_callbacks=secondary_hook_callbacks,
            act_on_invalidation_callback=lambda: self.invalidate_widgets(),
            logger=logger
        )
      
        with self._internal_update():
            self.set_block_signals(self)
            self._initialize_widgets()
            self.set_unblock_signals(self)

        with self._internal_update():
            self.invalidate_widgets()

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "ComplexHookController initialized")

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
    # Widget Update and Synchronization
    ###########################################################################

    @final
    def _submit_values_on_widget_changed(self, values: dict[PHK, PHV]) -> None:
        """
        Update the widgets from the currently set component values.
        
        **DO NOT OVERRIDE:** This method is part of the base controller's change notification system.
        Controllers should implement _invalidate_widgets_impl() instead.

        **This method is supposed to be called in the end of an _on_widget_..._changed() method.**

        """

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")
        
        complete_primary_component_values: dict[PHK, Any] = {**self.primary_values, **values}

        if self._verification_method is not None:
            success, msg = self._verification_method(complete_primary_component_values)
            if not success:
                log_bool(self, "_submit_values_on_widget_changed", self._logger, False, msg)
                self.invalidate_widgets()
                return
            
        self.set_block_signals(self)
            
        self._set_component_values(complete_primary_component_values, notify_binding_system=True)
        try:
            with self._internal_update():
                self.invalidate_widgets()
        except Exception as e:
            log_bool(self, "_submit_values_on_widget_changed", self._logger, False, str(e))
        finally:
            self.set_unblock_signals(self)
            log_bool(self, "_submit_values_on_widget_changed", self._logger, True, "Widgets updated")

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


    ###########################################################################
    # Public API Properties
    ###########################################################################

    def submit_single_value(self, hook_key: PHK, value: PHV) -> None:
        """Submit a single value to the controller."""
        hook: OwnedHookLike[PHV] = self.get_hook(hook_key) # type: ignore
        hook.submit_single_value(value)

    def submit_multiple_values(self, values: dict[PHK, PHV]) -> None:
        """Submit multiple values to the controller."""

        hooks_and_values: list[tuple[OwnedHookLike[PHV], PHV]] = []
        for hook_key, value in values.items():
            hook: OwnedHookLike[PHV] = self.get_hook(hook_key) # type: ignore
            hooks_and_values.append((hook, value))

        OwnedHookLike.submit_multiple_values(*hooks_and_values)