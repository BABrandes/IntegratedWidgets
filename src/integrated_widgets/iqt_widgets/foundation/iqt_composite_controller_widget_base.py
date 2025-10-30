from typing import Generic, TypeVar, Any, Optional
from logging import Logger

from PySide6.QtWidgets import QWidget

from nexpy import Hook

from ...controllers.core.base_composite_controller import BaseCompositeController
from .iqt_controller_widget_base import IQtControllerWidgetBase
from .layout_payload_base import LayoutPayloadBase
from .layout_strategy_base import LayoutStrategyBase

HK = TypeVar("HK", bound=str)
HV = TypeVar("HV")
P = TypeVar("P", bound=LayoutPayloadBase)
C = TypeVar("C", bound=BaseCompositeController[Any, Any, Any, Any])


class IQtCompositeControllerWidgetBase(IQtControllerWidgetBase[HK, HV, P, C], Generic[HK, HV, P, C]):

    def __init__(
        self,
        controller: C,
        payload: P,
        *,
        layout_strategy: Optional[LayoutStrategyBase[P]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
        ) -> None:
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    def get_hook_keys(self) -> set[HK]:
        return self._controller._get_hook_keys() # type: ignore

    def get_hook_by_key(self, key: HK) -> Hook[HV]:
        """
        Get a hook from the controller by key.
        
        This is a convenience method that forwards to the controller's get_hook()
        method, allowing direct access to the controller's hooks without needing
        to access the controller property first.
        
        Parameters
        ----------
        key : HK
            The hook key (e.g., "value", "enabled")
        
        Returns
        -------
        Hook[HV]
            The hook instance that can be connected to other hooks
        
        Examples
        --------
        >>> hook = widget.get_hook("value")
        >>> hook.join(other_hook, initial_sync_mode="use_target_value")
        
        See Also
        --------
        controller : Access the controller directly
        get_value_of_hook : Get the current value instead of the hook
        """
        return self._controller._get_hook_by_key(key) # type: ignore

    def get_hook_value_by_key(self, key: HK) -> HV:
        """
        Get the current value of a hook from the controller.
        
        This is a convenience method that forwards to the controller's
        get_value_of_hook() method, providing quick access to hook values
        without needing to get the hook first.
        
        Parameters
        ----------
        key : HK
            The hook key (e.g., "value", "enabled")
        
        Returns
        -------
        HV
            The current value of the hook
        
        Examples
        --------
        >>> value = widget.get_value_of_hook("value")
        >>> enabled = widget.get_value_of_hook("enabled")
        
        See Also
        --------
        controller : Access the controller directly
        get_hook : Get the hook itself instead of just its value
        """
        return self._controller._get_value_by_key(key) # type: ignore