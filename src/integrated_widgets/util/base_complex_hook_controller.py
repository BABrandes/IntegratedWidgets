from __future__ import annotations

# Standard library imports
from typing import Optional, Callable, Mapping, final, TypeVar, Generic, Any, cast
from logging import Logger

# BAB imports
from observables.core import NexusManager, DEFAULT_NEXUS_MANAGER, ComplexObservableBase

# Local imports
from ..util.resources import log_msg
from .base_controller import BaseController

PHK = TypeVar("PHK", bound=str)
"""Primary Hook Keys"""
SHK = TypeVar("SHK", bound=str)
"""Secondary Hook Keys"""

PHV = TypeVar("PHV")
"""Primary Hook Values"""
SHV = TypeVar("SHV")
"""Secondary Hook Values"""

C = TypeVar('C', bound="BaseComplexHookController[Any, Any, Any, Any, Any]")

class BaseComplexHookController(BaseController[PHK|SHK, PHV|SHV, C], ComplexObservableBase[PHK, SHK, PHV, SHV, C], Generic[PHK, SHK, PHV, SHV, C]):
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
        secondary_hook_callbacks: Mapping[SHK, Callable[[Mapping[PHK, PHV]], SHV]] = {},
        add_values_to_be_updated_callback: Optional[Callable[[ComplexObservableBase[PHK, SHK, PHV, SHV, C], Mapping[PHK, PHV], Mapping[PHK, PHV]], Mapping[PHK, PHV]]] = None,
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,

    ) -> None:

        # ------------------------------------------------------------------------------------------------
        # Prepare the initialization of BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        def invalidate_callback(_self: "BaseComplexHookController[Any, Any, Any, Any, Any]"):
            # Check if the controller has been garbage collected
            if _self is not None: # type: ignore
                _self._widget_invalidation_signal.trigger.emit()

        # ------------------------------------------------------------------------------------------------
        # Initialize BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        BaseController.__init__( # type: ignore
            self,
            nexus_manager=nexus_manager,
            debounce_ms=debounce_ms,
            logger=logger
        )

        ComplexObservableBase.__init__( # type: ignore
            self,
            initial_component_values_or_hooks=initial_component_values,
            verification_method=verification_method,
            secondary_hook_callbacks=secondary_hook_callbacks,
            add_values_to_be_updated_callback=add_values_to_be_updated_callback,
            invalidate_callback=lambda: invalidate_callback(self),
            logger=logger
        )
      
        # ------------------------------------------------------------------------------------------------
        # Initialize widgets
        # ------------------------------------------------------------------------------------------------

        with self._internal_update():
            self.is_blocking_signals = True
            self._initialize_widgets_impl()
            self.is_blocking_signals = False


        # ------------------------------------------------------------------------------------------------
        # Initialize is done!
        # ------------------------------------------------------------------------------------------------

        log_msg(self, f"{cast(Any, self).__class__.__name__} initialized", self._logger, "ComplexHookController initialized")

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    @final
    def dispose_impl(self) -> None:
        """Dispose of the controller and clean up resources."""
        
        # Check if we're in a safe state for cleanup
        # During garbage collection, some objects may be in an unstable state
        try:
            from PySide6.QtWidgets import QApplication
            if QApplication.instance() is None:
                # Qt application has been destroyed, skip cleanup that might use Qt
                return
        except (ImportError, RuntimeError):
            # Qt is shutting down or unavailable
            return
        
        # Disconnect all hooks first to prevent further updates
        try:
            for hook in self.get_dict_of_hooks().values():
                try:
                    hook.disconnect_hook()
                except Exception as e:
                    log_msg(self, "dispose", self._logger, f"Error disconnecting hook '{hook}': {e}")
        except Exception as e:
            log_msg(self, "dispose", self._logger, f"Error disconnecting hooks: {e}")

    def __del__(self) -> None:
        """Mark object as being garbage collected.
        
        Note: We intentionally don't call dispose() here because Qt cleanup
        during garbage collection can crash. Controllers should be explicitly
        disposed before going out of scope, or rely on Qt's parent-child cleanup.
        """
        pass

    ###########################################################################
    # Public API
    ###########################################################################

    def submit_primary_values(self, values: Mapping[PHK, PHV], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        return BaseController.submit_values(self, values, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore