from typing import Generic, TypeVar, Optional, Literal, final, Callable
from logging import Logger
from PySide6.QtWidgets import QWidget
from observables import OwnedHook, HookLike, InitialSyncMode, ObservableSingleValueLike, OwnedHookLike, OwnedHookLike, HookNexus
from observables._utils.carries_hooks import CarriesHooks
from abc import abstractmethod
from ..util.resources import log_msg, log_bool
from .base_controller import BaseController

T = TypeVar('T')

class BaseSingleHookController(BaseController, ObservableSingleValueLike[T], CarriesHooks[Literal["value"], T], Generic[T]):
    
    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        *,
        verification_method: Optional[Callable[[T], tuple[bool, str]]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None) -> None:

        self._verification_method: Optional[Callable[[T], tuple[bool, str]]] = verification_method

        BaseController.__init__(
            self,
            parent=parent,
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

        def invalidate_callback() -> tuple[bool, str]:
            if self._is_disposed:
                raise RuntimeError("Controller has been disposed")
            # Only invalidate if widgets are initialized
            if hasattr(self, '_widgets_initialized') and self._widgets_initialized:
                # Use the proper invalidate_widgets method which sets up the context
                self.invalidate_widgets()
            return True, "Invalidate callback called"

        self._internal_hook: OwnedHook[T] = OwnedHook[T](
            self, 
            value,
            lambda _: invalidate_callback(),
            logger=logger)

        with self._internal_update():
            self.set_block_signals(self)
            self._initialize_widgets()
            self.set_unblock_signals(self)

        # Mark widgets as initialized
        self._widgets_initialized = True

        # Connect hook after widgets are initialized
        if isinstance(hook, HookLike):
            self._internal_hook.connect(hook, initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)

        # Automatically update widgets after initialization to ensure they display current values
        # Only do this if we're not connected to an external hook (to avoid double updates)
        if not isinstance(hook, HookLike):
            with self._internal_update():
                self.invalidate_widgets()

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

        success, msg = self._internal_hook.is_valid_value_for_submission(value)
        if not success:
            log_bool(self, "_submit_values_on_widget_changed", self._logger, False, msg)
            self.invalidate_widgets()
            return
            
        self.set_block_signals(self)
                
        self._internal_hook.submit_single_value(value)
        try:
            with self._internal_update():
                self.invalidate_widgets()
        except Exception as e:
            log_bool(self, "_submit_values_on_widget_changed", self._logger, False, str(e))
        finally:
            self.set_unblock_signals(self)
            log_bool(self, "_submit_values_on_widget_changed", self._logger, True, "Widgets updated")

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

    ###########################################################################
    # ObservableSingleValueLike Interface Implementation
    ###########################################################################

    @property
    def hook(self) -> OwnedHookLike[T]:
        return self._internal_hook

    @property
    def value(self) -> T:
        return self._internal_hook.value

    @value.setter
    def value(self, value: T) -> None:
        self._internal_hook.submit_single_value(value)

    def change_value(self, value: T) -> None:
        self._internal_hook.submit_single_value(value)

    ###########################################################################
    # CarriesHooks Interface Implementation
    ###########################################################################

    def get_hook(self, key: Literal["value"]) -> OwnedHook[T]:
        """
        Get a hook by its key.

        Args:
            key: The key of the hook to get

        Returns:
            The hook
        """
        
        return self._internal_hook

    def get_hook_value_as_reference(self, key: Literal["value"]) -> T:
        """
        Get a value as a reference by its key.

        ** The returned value is a reference, so modifying it will modify the observable.

        Args:
            key: The key of the hook to get

        Returns:
            The value
        """
        return self._internal_hook.value_reference

    def get_hook_keys(self) -> set[Literal["value"]]:
        """
        Get all keys of the hooks.
        """
        return {"value"}

    def get_hook_key(self, hook_or_nexus: OwnedHookLike[T]|HookNexus[T]) -> Literal["value"]:
        """
        Get the key of a hook or nexus.
        """
        return "value"

    def connect(self, hook: OwnedHookLike[T], to_key: Literal["value"], initial_sync_mode: InitialSyncMode) -> None:
        """
        Connect a hook to another hook.
        """
        self._internal_hook.connect(hook, initial_sync_mode=initial_sync_mode)

    def disconnect(self, key: Optional[Literal["value"]]) -> None:
        """
        Disconnect a hook by its key.
        """
        self._internal_hook.disconnect()

    def is_valid_hook_value(self, hook_key: Literal["value"], value: T) -> tuple[bool, str]:
        """
        Check if a value is valid for a hook.

        Args:
            hook_key: The key of the hook to check
            value: The value to check

        Returns:
            A tuple containing a boolean indicating if the value is valid and a string explaining why
        """

        if self._verification_method is not None:
            success, msg = self._verification_method(value)
            if not success:
                return False, msg
        return True, "Value is valid"

    def invalidate_hooks(self) -> tuple[bool, str]:
        """
        Invalidate all hooks.
        """
        self._internal_hook.invalidate()
        return True, "Hooks invalidated"

    def destroy(self) -> None:
        self.disconnect(None)
        self.dispose()