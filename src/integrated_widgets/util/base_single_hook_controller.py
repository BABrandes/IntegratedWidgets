from typing import Generic, TypeVar, Optional, Literal, final, Callable, Mapping, Any
from logging import Logger
from PySide6.QtWidgets import QWidget
from observables import BaseCarriesHooks, OwnedHook, HookLike, InitialSyncMode, ObservableSingleValueLike, OwnedHookLike, OwnedHookLike, HookNexus, CarriesHooksLike, NexusManager, DEFAULT_NEXUS_MANAGER
from abc import abstractmethod

from ..util.resources import log_msg, log_bool
from .base_controller import BaseController

T = TypeVar('T')
C = TypeVar('C', bound="BaseSingleHookController")

class BaseSingleHookController(BaseController, BaseCarriesHooks[Literal["value", "enabled"], T|bool, C], Generic[T, C]):
    
    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        *,
        verification_method: Optional[Callable[[T], tuple[bool, str]]] = None,
        parent: Optional[QWidget] = None,
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
            try:
                self.invalidate_widgets()
            except Exception as e:
                return False, f"Error invalidating widgets: {e}"
            return True, "Widgets invalidated"

        BaseController.__init__(
            self,
            parent=parent,
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

        self._widget_enabled_hook: OwnedHook[bool] = OwnedHook[bool](
            owner=self,
            initial_value=True,
            logger=logger,
            nexus_manager=nexus_manager
        )

        with self._internal_update():
            self.set_block_signals(self)
            self._initialize_widgets()
            self.set_unblock_signals(self)

        # Connect hook after widgets are initialized
        if isinstance(hook, HookLike):
            self._internal_hook.connect_hook(hook, initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "SingleHookController initialized")

    ###########################################################################
    # Widget Update and Synchronization
    ###########################################################################

    @final
    def _submit_values_on_widget_changed(self, value: T) -> None:
        """
        Update the widgets from the currently set component values.
        
        **DO NOT OVERRIDE:** This method is part of the base controller's change notification system.
        Controllers should implement _invalidate_widgets_impl() instead.

        **This method is supposed to be called in the end of an _on_widget_..._changed() method.**

        """

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")

        self.set_block_signals(self)
        success, msg = self._internal_hook.submit_value(value)
        self.set_unblock_signals(self)

        if not success:
            log_bool(self, "_submit_values_on_widget_changed", self._logger, False, msg)
            # Reset the state of the widget
            self.invalidate_widgets()
            return

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    @final
    def dispose(self) -> None:
        """Dispose of the controller and clean up resources."""
        if self._is_disposed:
            return
        
        self._is_disposed = True
        
        # Disconnect hooks safely
        try:
            self.value_hook.disconnect()
        except Exception as e:
            log_bool(self, "dispose", self._logger, False, f"Error disconnecting value hook: {e}")
            
        try:
            self.enabled_hook.disconnect()
        except Exception as e:
            log_bool(self, "dispose", self._logger, False, f"Error disconnecting enabled hook: {e}")
        
        # Disconnect forwarder signal
        if hasattr(self, '_forwarder') and self._forwarder is not None:
            try:
                # Check if the forwarder trigger still exists and is valid
                if hasattr(self._forwarder, 'trigger') and self._forwarder.trigger is not None:
                    # Additional check: try to access a property to see if the object is still valid
                    if hasattr(self._forwarder.trigger, 'blockSignals'):
                        self._forwarder.trigger.disconnect()
            except (RuntimeError, AttributeError) as e:
                # Qt object may have been deleted already during shutdown
                log_bool(self, "dispose", self._logger, False, f"Error disconnecting forwarder: {e}")
        
        # Clean up Qt object and all its children
        if hasattr(self, '_qt_object'):
            try:
                # Check if the Qt object is still valid before trying to delete it
                if hasattr(self._qt_object, 'isVisible'):  # Quick check if object is still valid
                    self._qt_object.deleteLater()
            except (RuntimeError, AttributeError) as e:
                # Qt object may have been deleted already during shutdown
                log_bool(self, "dispose", self._logger, False, f"Error deleting Qt object: {e}")

        log_bool(self, f"{self.__class__.__name__} disposed", self._logger, True)

    def __del__(self) -> None:
        """Ensure proper cleanup when the object is garbage collected."""
        if not self._is_disposed:
            self.dispose()

    ###########################################################################
    # Convenience Properties and Methods
    ###########################################################################

    @property
    def value_hook(self) -> OwnedHookLike[T]:
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
    def enabled_hook(self) -> OwnedHookLike[bool]:
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

    def _get_hook(self, key: Literal["value", "enabled"]) -> OwnedHookLike[T|bool]:
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

    def _get_hook_key(self, hook_or_nexus: OwnedHookLike[Any]|HookNexus[Any]) -> Literal["value", "enabled"]:
        """
        Get the key of a hook or nexus.
        """

        if isinstance(hook_or_nexus, OwnedHookLike):
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