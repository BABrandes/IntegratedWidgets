from typing import Generic, TypeVar, Optional, Literal, Callable, Mapping, Any
from logging import Logger

from observables import ObservableSingleValueLike, HookLike
from observables.core import HookNexus, BaseCarriesHooks, NexusManager, DEFAULT_NEXUS_MANAGER, HookWithOwnerLike, OwnedHook

from ..util.resources import log_msg
from .base_controller import BaseController, DEFAULT_DEBOUNCE_MS

T = TypeVar('T')
C = TypeVar('C', bound="BaseSingleHookController")

class BaseSingleHookController(BaseController, BaseCarriesHooks[Literal["value", "enabled"], T|bool, C], Generic[T, C]):

    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        *,
        verification_method: Optional[Callable[[T], tuple[bool, str]]] = None,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        ) -> None:

        self._verification_method: Optional[Callable[[T], tuple[bool, str]]] = verification_method

        def validate_complete_values_in_isolation_callback(self_ref: "BaseSingleHookController", values: Mapping[Literal["value", "enabled"], T|bool]) -> tuple[bool, str]:
            """
            Check if the values are valid as part of the owner.
            """

            # Check if enabled is a boolean
            if not isinstance(values["enabled"], bool):
                return False, "Enabled must be a boolean"

            # Check if the value is valid
            if self._verification_method is None:
                return True, "Verification method is not set"
            value: T = values["value"] # type: ignore
            success, msg = self._verification_method(value)
            if not success:
                return False, msg
            return True, "Verification method passed"

        def invalidate_callback(self_ref: "BaseSingleHookController") -> tuple[bool, str]:
            """Queue a widget invalidation request through the Qt event loop.
            
            Uses QueuedConnection to ensure widget updates happen asynchronously,
            preventing re-entrancy issues during hook system operations.
            """
            try:
                self._widget_invalidation_signal.trigger.emit()
            except Exception as e:
                return False, f"Error invalidating widgets: {e}"
            return True, "Widgets invalidated"

        BaseController.__init__(
            self,
            submit_values_callback=lambda value: self._internal_hook.submit_value(value), #type: ignore
            nexus_manager=nexus_manager,
            debounce_ms=debounce_ms,
            logger=logger
        )

        BaseCarriesHooks.__init__(
            self,
            validate_complete_values_in_isolation_callback=validate_complete_values_in_isolation_callback,
            invalidate_callback=invalidate_callback,
            logger=logger
        )

        if isinstance(value_or_hook_or_observable, ObservableSingleValueLike):
            value: T = value_or_hook_or_observable.value
            hook: Optional[HookLike[T]] = value_or_hook_or_observable.hook
        elif isinstance(value_or_hook_or_observable, HookLike):
            value = value_or_hook_or_observable.value
            hook = value_or_hook_or_observable
        else:
            # It should be T
            value = value_or_hook_or_observable
            hook = None

        self._internal_hook: OwnedHook[T] = OwnedHook[T](
            owner=self, 
            initial_value=value,
            logger=logger,
            nexus_manager=nexus_manager
        )

        self._widget_enabled_hook = OwnedHook[bool](
            owner=self,
            initial_value=True,
            logger=logger,
            nexus_manager=nexus_manager
        )

        with self._internal_update():
            self.is_blocking_signals = True
            self._initialize_widgets()
            self.is_blocking_signals = False

        # Connect hook after widgets are initialized
        if isinstance(hook, HookLike):
            self._internal_hook.connect_hook(hook, initial_sync_mode="use_target_value") # type: ignore

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "SingleHookController initialized")

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    def dispose_impl(self) -> None:
        """Dispose of the controller and clean up resources."""
        
        # Disconnect value hook
        try:
            self.value_hook.disconnect_hook()
        except Exception as e:
            log_msg(self, "dispose", self._logger, f"Error disconnecting value hook: {e}")
        
        # Disconnect enabled hook
        try:
            self.enabled_hook.disconnect_hook()
        except Exception as e:
            log_msg(self, "dispose", self._logger, f"Error disconnecting enabled hook: {e}")

    def __del__(self) -> None:
        """Ensure proper cleanup when the object is garbage collected."""
        if hasattr(self, '_is_disposed') and not self._is_disposed:
            self.dispose()

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
        success, msg = self._internal_hook.submit_value(value)
        if not success:
            raise ValueError(msg)

    def change_value(self, value: T) -> None:
        success, msg = self._internal_hook.submit_value(value)
        if not success:
            raise ValueError(msg)

    @property
    def enabled_hook(self) -> HookWithOwnerLike[bool]:
        return self._widget_enabled_hook

    @property
    def enabled(self) -> bool:
        return self._widget_enabled_hook.value

    @enabled.setter
    def enabled(self, value: bool) -> None:
        success, msg = self._widget_enabled_hook.submit_value(value)
        if not success:
            raise ValueError(msg)

    def change_enabled(self, value: bool) -> None:
        success, msg = self._widget_enabled_hook.submit_value(value)
        if not success:
            raise ValueError(msg)

    ###########################################################################
    # BaseCarriesHooks Interface Implementation
    ###########################################################################

    def _get_hook(self, key: Literal["value", "enabled"]) -> HookWithOwnerLike[T|bool]:
        """
        Get a hook by its key.
        """

        if key == "value":
            return self._internal_hook # type: ignore
        elif key == "enabled":
            return self._widget_enabled_hook # type: ignore
        else:
            raise ValueError("Invalid key")

    def _get_value_reference_of_hook(self, key: Literal["value", "enabled"]) -> T|bool:
        """
        Get a value as a reference by its key.
        """
        if key == "value":
            return self._internal_hook.value_reference
        elif key == "enabled":
            return self._widget_enabled_hook.value_reference
        else:
            raise ValueError("Invalid key")
    
    def _get_hook_keys(self) -> set[Literal["value", "enabled"]]:
        """
        Get all keys of the hooks.
        """
        return {"value", "enabled"}

    def _get_hook_key(self, hook_or_nexus: HookWithOwnerLike[Any]|HookNexus[Any]) -> Literal["value", "enabled"]:
        """
        Get the key of a hook or nexus.
        """

        if isinstance(hook_or_nexus, HookWithOwnerLike):
            match hook_or_nexus:
                case self._internal_hook:
                    return "value"
                case self._widget_enabled_hook:
                    return "enabled"
                case _:
                    raise ValueError("Invalid hook")
        elif isinstance(hook_or_nexus, HookNexus):
            match hook_or_nexus:
                case self._internal_hook.hook_nexus:
                    return "value"
                case self._widget_enabled_hook.hook_nexus:
                    return "enabled"
                case _:
                    raise ValueError("Invalid nexus")
        else:
            raise ValueError("Invalid hook or nexus")