from typing import Generic, TypeVar, Optional, Literal, Callable, Mapping, Any, Self
from logging import Logger

from nexpy import Hook, XSingleValueProtocol, XBase
from nexpy.core import NexusManager, OwnedWritableHook, OwnedHookProtocol, Nexus
from nexpy import default as nexpy_default

from ...auxiliaries.resources import log_msg
from .base_controller import BaseController

T = TypeVar('T')
C = TypeVar('C', bound="BaseSingletonController[Any]")

class BaseSingletonController(BaseController[Literal["value"], T], XSingleValueProtocol[T], Generic[T]):

    def __init__(
        self,
        value: T | Hook[T] | XSingleValueProtocol[T],
        *,
        verification_method: Optional[Callable[[T], tuple[bool, str]]] = None,
        debounce_ms: int|Callable[[], int],
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        ) -> None:

        self._verification_method: Optional[Callable[[T], tuple[bool, str]]] = verification_method

        # ------------------------------------------------------------------------------------------------
        # Handle the provided value or hook or observable
        # ------------------------------------------------------------------------------------------------

        if isinstance(value, XSingleValueProtocol):
            value_provided_value: T = value.value # type: ignore
            value_provided_hook: Optional[Hook[T]] = value.value_hook # type: ignore

        elif isinstance(value, Hook):
            value_provided_value = value.value # type: ignore
            value_provided_hook = value # type: ignore

        else:
            # It should be T
            value_provided_value = value # type: ignore
            value_provided_hook = None # type: ignore

        # ------------------------------------------------------------------------------------------------
        # Set the internal value hook
        # ------------------------------------------------------------------------------------------------

        self._internal_hook: OwnedWritableHook[T, Self] = OwnedWritableHook[T, Self](
            owner=self, 
            value=value_provided_value, # type: ignore
            logger=logger,
            nexus_manager=nexus_manager
        )

        # ------------------------------------------------------------------------------------------------
        # Prepare the initialization of BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        # Step 1: Validate complete values in isolation callback
        def validate_complete_values_in_isolation_callback(values: Mapping[Literal["value"], T]) -> tuple[bool, str]:
            """
            Check if the values are valid as part of the owner.
            """

            if self._verification_method is None:
                return True, "Verification method is not set"

            try:
                value: T = values["value"] # type: ignore
                success, msg = self._verification_method(value)

                if not success:
                    return False, msg
                else:
                    return True, "Verification method passed"

            except Exception as e:
                return False, f"Error validating value: {e}"

        # Step 2: Invalidate callback
        def invalidate_callback() -> tuple[bool, str]:
            """Queue a widget invalidation request through the Qt event loop.
            
            Uses QueuedConnection to ensure widget updates happen asynchronously,
            preventing re-entrancy issues during hook system operations.
            
            Args:
                calling_nexus_manager: The nexus manager calling this callback.
            """
            try:
                if self is not None: # type: ignore
                    self._widget_invalidation_signal.trigger.emit()
                else:
                    return False, "Controller has been garbage collected"

            except Exception as e:
                return False, f"Error invalidating widgets: {e}"

            return True, "Widgets invalidated"

        # ------------------------------------------------------------------------------------------------
        # Initialize BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        BaseController.__init__( # type: ignore
            self,
            nexus_manager=nexus_manager,
            debounce_ms=debounce_ms,
            logger=logger
        )

        XBase.__init__( # type: ignore
            self,
            invalidate_after_update_callback=invalidate_callback,
            validate_complete_values_callback=validate_complete_values_in_isolation_callback,
            logger=logger,
            nexus_manager=nexus_manager
        )

        # ------------------------------------------------------------------------------------------------
        # Initialize widgets
        # ------------------------------------------------------------------------------------------------       

        with self._internal_update():
            self.is_blocking_signals = True
            self._initialize_widgets_impl()
            self.is_blocking_signals = False

        # ------------------------------------------------------------------------------------------------
        # Connect hooks, if provided
        # ------------------------------------------------------------------------------------------------

        if isinstance(value_provided_hook, Hook):
            self._internal_hook.join(value_provided_hook, initial_sync_mode="use_target_value") # type: ignore

        # ------------------------------------------------------------------------------------------------
        # Initialize is done - invalidate widgets for the first time
        # ------------------------------------------------------------------------------------------------

        self._invalidate_widgets()

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "SingletonController initialized")

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

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
        
        # Disconnect value hook
        try:
            self.value_hook.isolate()
        except Exception as e:
            log_msg(self, "dispose", self._logger, f"Error disconnecting value hook: {e}")

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

    def submit(self, value: T, *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """
        Submit the single value of this single hook controller with debouncing. (Shortcut for submit_values_debounced({"value": value}, debounce_ms=debounce_ms))
        """
        self._submit_values_debounced({"value": value}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)

    ###########################################################################
    # Serialization protocol implementation
    ###########################################################################
    
    def get_values_for_serialization(self) -> Mapping[Literal["value"], T]:
        """Get the values for serialization."""
        return {"value": self._internal_hook.value}

    def set_values_from_serialization(self, values: Mapping[Literal["value"], T]) -> None:
        """Set the values from serialization."""
        self._internal_hook.value = values["value"]

    ###########################################################################
    # XBase protocol implementation
    ###########################################################################

    def _get_value_by_key(self, key: Literal["value"]) -> T:
        """Get the value by key."""
        return self._internal_hook.value

    def _get_hook_by_key(self, key: Literal["value"]) -> OwnedHookProtocol[T, Self]:
        """Get the hook by key."""
        return self._internal_hook

    def _get_hook_keys(self) -> set[Literal["value"]]:
        """Get the hook keys."""
        return {"value"}

    def _get_key_by_hook_or_nexus(self, hook_or_nexus: OwnedHookProtocol[T, Self] | Nexus[T]) -> Literal["value"]:
        """Get the key by hook or nexus."""
        if isinstance(hook_or_nexus, OwnedHookProtocol):
            if not hook_or_nexus is self._internal_hook:
                raise ValueError(f"Invalid hook: {hook_or_nexus}")
            return "value"
        elif isinstance(hook_or_nexus, Nexus): # type: ignore
            if not hook_or_nexus is self._internal_hook.nexus:
                raise ValueError(f"Invalid nexus: {hook_or_nexus}")
            return "value"
        else:
            raise ValueError(f"Invalid hook or nexus: {hook_or_nexus}")

    ###########################################################################
    # XSingleValueProtocol methods
    ###########################################################################

    @property
    def value_hook(self) -> Hook[T]:
        return self._internal_hook

    @property
    def value(self) -> T:
        return self._internal_hook.value

    @value.setter
    def value(self, value: T) -> None:
        self._internal_hook.value = value

    def change_value(self, value: T, *, logger: Optional[Logger] = None, raise_submission_error_flag: bool = True) -> tuple[bool, str]:
        return self._internal_hook.change_value(value, logger=logger, raise_submission_error_flag=raise_submission_error_flag)