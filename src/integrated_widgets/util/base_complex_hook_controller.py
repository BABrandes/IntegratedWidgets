from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from typing import Optional, Callable, Mapping, final, TypeVar, Generic
from logging import Logger

from PySide6.QtWidgets import QWidget

# BAB imports
from observables.core import NexusManager, DEFAULT_NEXUS_MANAGER, BaseObservable

# Local imports
from ..util.resources import log_msg
from .base_controller import BaseController, DEFAULT_DEBOUNCE_MS

PHK = TypeVar("PHK")
"""Primary Hook Keys"""
SHK = TypeVar("SHK")
"""Secondary Hook Keys"""

PHV = TypeVar("PHV")
"""Primary Hook Values"""
SHV = TypeVar("SHV")
"""Secondary Hook Values"""

C = TypeVar('C', bound="BaseComplexHookController")

class BaseComplexHookController(BaseController, BaseObservable[PHK, SHK, PHV, SHV, C], Generic[PHK, SHK, PHV, SHV, C]):
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
        add_values_to_be_updated_callback: Optional[Callable[[BaseObservable[PHK, SHK, PHV, SHV, C], Mapping[PHK, PHV], Mapping[PHK, PHV]], Mapping[PHK, PHV]]] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,

    ) -> None:

        BaseController.__init__(
            self,
            submit_values_callback=lambda value: self.submit_values(value), #type: ignore
            nexus_manager=nexus_manager,
            debounce_ms=DEFAULT_DEBOUNCE_MS,
            logger=logger
        )
        BaseObservable.__init__(
            self,
            initial_component_values_or_hooks=initial_component_values,
            verification_method=verification_method,
            secondary_hook_callbacks=secondary_hook_callbacks,
            add_values_to_be_updated_callback=add_values_to_be_updated_callback,
            invalidate_callback=lambda: self._widget_invalidation_signal.trigger.emit(),
            logger=logger
        )
      
        with self._internal_update():
            self.is_blocking_signals = True
            self._initialize_widgets()
            self.is_blocking_signals = False

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
    # Lifecycle Management
    ###########################################################################

    @final
    def dispose_impl(self) -> None:
        """Dispose of the controller and clean up resources."""
        
        # Disconnect all hooks first to prevent further updates
        try:
            for hook in self.get_dict_of_hooks().values():
                hook.disconnect_hook()
        except Exception as e:
            log_msg(self, "dispose", self._logger, f"Error deactivating hooks: {e}")

    def __del__(self) -> None:
        """Ensure proper cleanup when the object is garbage collected."""
        if hasattr(self, '_is_disposed') and not self._is_disposed:
            self.dispose()