from typing import Generic, TypeVar, Any, Optional, Callable, Mapping, final
from PySide6.QtCore import QObject
from logging import Logger
from .base_widget_controller import BaseWidgetController
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode, ObservableSingleValue
from ..util.resources import log_bool, log_msg

PHK = TypeVar("PHK")
SHK = TypeVar("SHK")
PHV = TypeVar("PHV")
SHV = TypeVar("SHV")

class BaseWidgetControllerWithDisable(BaseWidgetController[PHK, SHK, PHV, SHV], Generic[PHK, SHK, PHV, SHV]):
    """Base class for controllers that use hooks for data management and can be disabled."""

    def __init__(
            self,
            initial_component_values: dict[PHK, PHV],
            *,
            verification_method: Optional[Callable[[Mapping[PHK, PHV]], tuple[bool, str]]] = None,
            emitter_hook_callbacks: dict[SHK, Callable[[Mapping[PHK, PHV]], SHV]] = {},
            parent: Optional[QObject] = None,
            logger: Optional[Logger] = None,

    ) -> None:
        
        super().__init__(
            initial_component_values=initial_component_values,
            verification_method=verification_method,
            secondary_hook_callbacks=emitter_hook_callbacks,
            parent=parent,
            logger=logger,
        )

    def disable_widgets(self) -> None:
        """
        Disable all widgets. This also deactivates all hooks and removes all bindings.
        """

        try:

            self.set_block_signals(self)

            self._is_disabled = True

            for hook in self.hook_dict.values():
                hook.deactivate()

            with self._internal_update():
                self._disable_widgets()

        except Exception as e:
            self._is_disabled = False
            log_bool(self, "disable_widgets", self._logger, False, str(e))
            raise e

    def enable_widgets(self, initial_component_values: dict[PHK, PHV]) -> None:
        """
        Enable all widgets. This also activates all hooks and restores all bindings.

        If the controller is already enabled, nothing will be done.
        """

        if not self._is_disabled:
            return

        try:
            self._is_disabled = False

            for key, hook in self.hook_dict.items():
                initial_value: PHV = initial_component_values[key] # type: ignore
                hook.activate(initial_value)

            with self._internal_update():
                self._enable_widgets(initial_component_values)

            self.set_unblock_signals(self)

        except Exception as e:
            self._is_disabled = True
            log_bool(self, "enable_widgets", self._logger, False, str(e))
            raise e
        
    def _disable_widgets(self) -> None:
        """
        Disable all widgets.

        **REQUIRED OVERRIDE:** Controllers must implement this method to disable their widgets if they can be disabled.
        This is called automatically by the base controller when the controller is disabled.

        **What to do here:**
        - Disable all widgets
        - Use self._internal_update() context manager for widget modifications
        """

        raise NotImplementedError
    
    def _enable_widgets(self, initial_component_values: dict[PHK, PHV]) -> None:
        """
        Enable all widgets.

        **REQUIRED OVERRIDE:** Controllers must implement this method to enable their widgets if they can be disabled.
        This is called automatically by the base controller when the controller is enabled.

        **What to do here:**
        - Enable all widgets
        - Use self._internal_update() context manager for widget modifications
        """
        raise NotImplementedError

    ###########################################################################
    # Overwriting BaseObservable methods that should be disabled when the controller is disabled
    ###########################################################################
    
    @final
    def _set_component_values(self, dict_of_values: dict[PHK, PHV], notify_binding_system: bool) -> None:
        """
        Override of the BaseObservable method to prevent setting component values when the controller is disabled.
        """

        if self._is_disabled:
            raise ValueError("Controller is disabled")
        log_msg(self, "_set_component_values", self._logger, f"Setting component values: {dict_of_values}")
        
        super()._set_component_values(dict_of_values, notify_binding_system)
        
        log_msg(self, "_set_component_values", self._logger, "Component values set")

    @final
    def get_value(self, key: PHK|SHK) -> PHV|SHV:
        """
        Override of the BaseObservable method to prevent getting component values when the controller is disabled.
        """

        if self._is_disabled:
            raise ValueError("Controller is disabled")
        return super().get_hook_value(key) 


        