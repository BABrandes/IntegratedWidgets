from typing import Generic, TypeVar, Optional, Literal, Callable, Mapping, Any
from logging import Logger

from observables import ObservableSingleValueLike, HookLike
from observables.core import HookNexus, BaseCarriesHooks, NexusManager, DEFAULT_NEXUS_MANAGER, HookWithOwnerLike, OwnedHook

from ..util.resources import log_msg
from .base_controller import BaseController

T = TypeVar('T')
C = TypeVar('C', bound="BaseSingleHookController[Any, Any]")

class BaseSingleHookController(BaseController[Literal["value"], T, C], BaseCarriesHooks[Literal["value"], T, C], Generic[T, C]):

    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        *,
        verification_method: Optional[Callable[[T], tuple[bool, str]]] = None,
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        ) -> None:

        self._verification_method: Optional[Callable[[T], tuple[bool, str]]] = verification_method

        # ------------------------------------------------------------------------------------------------
        # Handle the provided value or hook or observable
        # ------------------------------------------------------------------------------------------------

        if isinstance(value_or_hook_or_observable, ObservableSingleValueLike):
            value_provided_value: T = value_or_hook_or_observable.value # type: ignore
            value_provided_hook: Optional[HookLike[T]] = value_or_hook_or_observable.hook # type: ignore

        elif isinstance(value_or_hook_or_observable, HookLike):
            value_provided_value = value_or_hook_or_observable.value # type: ignore
            value_provided_hook = value_or_hook_or_observable # type: ignore

        else:
            # It should be T
            value_provided_value = value_or_hook_or_observable # type: ignore
            value_provided_hook = None # type: ignore

        # ------------------------------------------------------------------------------------------------
        # Set the internal value hook
        # ------------------------------------------------------------------------------------------------

        self._internal_hook: OwnedHook[T] = OwnedHook[T](
            owner=self, 
            initial_value=value_provided_value, # type: ignore
            logger=logger,
            nexus_manager=nexus_manager
        )

        # ------------------------------------------------------------------------------------------------
        # Prepare the initialization of BaseController and BaseCarriesHooks
        # ------------------------------------------------------------------------------------------------

        # Step 1: Validate complete values in isolation callback
        def validate_complete_values_in_isolation_callback(_self: "BaseSingleHookController[Any, Any]", values: Mapping[Literal["value"], T]) -> tuple[bool, str]:
            """
            Check if the values are valid as part of the owner.
            """

            if _self._verification_method is None:
                return True, "Verification method is not set"

            try:
                value: T = values["value"] # type: ignore
                success, msg = _self._verification_method(value)

                if not success:
                    return False, msg
                else:
                    return True, "Verification method passed"

            except Exception as e:
                return False, f"Error validating value: {e}"

        # Step 2: Invalidate callback
        def invalidate_callback(_self: "BaseSingleHookController[Any, Any]") -> tuple[bool, str]:
            """Queue a widget invalidation request through the Qt event loop.
            
            Uses QueuedConnection to ensure widget updates happen asynchronously,
            preventing re-entrancy issues during hook system operations.
            
            Args:
                _self: Reference to the controller (weakref).
                calling_nexus_manager: The nexus manager calling this callback.
            """
            try:
                if _self is not None: # type: ignore
                    _self._widget_invalidation_signal.trigger.emit()
                else:
                    return False, "Controller has been garbage collected"

            except Exception as e:
                return False, f"Error invalidating widgets: {e}"

            return True, "Widgets invalidated"

        # ------------------------------------------------------------------------------------------------
        # Initialize BaseController and BaseCarriesHooks
        # ------------------------------------------------------------------------------------------------

        BaseController.__init__( # type: ignore
            self,
            submit_values_callback=lambda value: self._internal_hook.submit_value(value), #type: ignore
            nexus_manager=nexus_manager,
            debounce_ms=debounce_ms,
            logger=logger
        )

        BaseCarriesHooks.__init__( # type: ignore
            self,
            validate_complete_values_in_isolation_callback=validate_complete_values_in_isolation_callback,
            invalidate_callback=invalidate_callback,
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
        # Connect hooks, if provided
        # ------------------------------------------------------------------------------------------------

        if isinstance(value_provided_hook, HookLike):
            self._internal_hook.connect_hook(value_provided_hook, initial_sync_mode="use_target_value") # type: ignore

        # ------------------------------------------------------------------------------------------------
        # Initialize is done!
        # ------------------------------------------------------------------------------------------------

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "SingleHookController initialized")

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
            self.value_hook.disconnect_hook()
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
    # Convenience Properties and Methods
    ###########################################################################

    @property
    def value_hook(self) -> HookWithOwnerLike[T]:
        return self._internal_hook

    @property
    def value(self) -> T:
        return self._internal_hook.value

    @value.setter
    def value(self, value: T) -> None:
        self.submit(value)

    def change_value(self, value: T) -> None:
        self.submit(value)

    ###########################################################################
    # BaseCarriesHooks Interface Implementation
    ###########################################################################

    def _get_hook(self, key: Literal["value"]) -> HookWithOwnerLike[T]:
        """
        Get a hook by its key.
        """
        match key:
            case "value":
                return self._internal_hook # type: ignore

            case _: # type: ignore
                raise ValueError("Invalid key")
            
    def _get_value_reference_of_hook(self, key: Literal["value"]) -> T:
        """
        Get a value as a reference by its key.
        """
        match key:
            case "value":
                return self._internal_hook.value_reference

            case _: # type: ignore
                raise ValueError("Invalid key")
        
    def _get_hook_keys(self) -> set[Literal["value"]]:
        """
        Get all keys of the hooks.
        """
        return {"value"}

    def _get_hook_key(self, hook_or_nexus: HookWithOwnerLike[Any]|HookNexus[Any]) -> Literal["value"]:
        """
        Get the key of a hook or nexus.
        """

        if isinstance(hook_or_nexus, HookWithOwnerLike):
            match hook_or_nexus:
                case self._internal_hook:
                    return "value"

                case _:
                    raise ValueError("Invalid hook")
        elif isinstance(hook_or_nexus, HookNexus): # type: ignore
            match hook_or_nexus:
                case self._internal_hook.hook_nexus:
                    return "value"

                case _:
                    raise ValueError("Invalid nexus")
        else:
            raise ValueError("Invalid hook or nexus")

    ###########################################################################
    # Public API
    ###########################################################################


    def submit(self, value: T, *, debounce_ms: Optional[int] = None) -> None:
        """
        Submit the single value of this single hook controller with debouncing. (Shortcut for submit_values_debounced({"value": value}, debounce_ms=debounce_ms))
        """
        self._submit_values_debounced({"value": value}, debounce_ms=debounce_ms)