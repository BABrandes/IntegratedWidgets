from typing import Generic, TypeVar, Any, Optional, Callable, Mapping
from PySide6.QtCore import QObject
from logging import Logger
from .base_controller import BaseWidgetController
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode, ObservableSingleValue
from ..util.resources import log_bool

HK = TypeVar("HK")
EHK = TypeVar("EHK")

class BaseWidgetControllerWithDisable(BaseWidgetController[HK, EHK], Generic[HK, EHK]):
    """Base class for controllers that use hooks for data management and can be disabled."""

    def __init__(
            self,
            initial_component_values: dict[HK, Any],
            *,
            verification_method: Optional[Callable[[Mapping[HK, Any]], tuple[bool, str]]] = None,
            emitter_hook_callbacks: dict[EHK, Callable[[Mapping[HK, Any]], Any]] = {},
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

            for hook in self.hooks:
                hook.deactivate()

            with self._internal_update():
                self._disable_widgets()

        except Exception as e:
            self._is_disabled = False
            log_bool(self, "disable_widgets", self._logger, False, str(e))
            raise e

    def enable_widgets(self, initial_component_values: dict[HK, Any]) -> None:
        """
        Enable all widgets. This also activates all hooks and restores all bindings.
        """

        try:
            self._is_disabled = False

            for key, hook in self.primary_component_values.items():
                initial_value: Any = initial_component_values[key]
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
    
    def _enable_widgets(self, initial_component_values: dict[HK, Any]) -> None:
        """
        Enable all widgets.

        **REQUIRED OVERRIDE:** Controllers must implement this method to enable their widgets if they can be disabled.
        This is called automatically by the base controller when the controller is enabled.

        **What to do here:**
        - Enable all widgets
        - Use self._internal_update() context manager for widget modifications
        """
        raise NotImplementedError


        