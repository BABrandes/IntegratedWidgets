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
    """
    Base class for IQT widgets that manage multiple related values through a composite controller.

    This class extends IQtControllerWidgetBase and provides convenient access to multiple hooks
    managed by composite controllers. It offers methods to access hooks by key, making it easy
    to work with complex widgets that have multiple synchronized values.

    Type Parameters
    --------------
    HK : str
        The type of hook keys (usually literal strings like "value", "enabled", etc.)
    HV : Any
        The type of hook values
    P : LayoutPayloadBase
        The payload type containing the widgets to be arranged
    C : BaseCompositeController
        The composite controller type that manages multiple hooks

    Methods
    -------
    get_hook_keys() -> set[HK]
        Get all available hook keys from the controller
    get_hook_by_key(key: HK) -> Hook[HV]
        Get a specific hook by its key
    get_hook_value_by_key(key: HK) -> HV
        Get the current value of a specific hook

    Examples
    --------
    Creating a custom range slider widget with min/max values:

    >>> @dataclass(frozen=True)
    ... class RangeSliderPayload(LayoutPayloadBase):
    ...     slider: QWidget
    ...     min_display: QWidget
    ...     max_display: QWidget
    >>>
    >>> class MyRangeSlider(IQtCompositeControllerWidgetBase[Literal["min_value", "max_value"], float, RangeSliderPayload, RangeController]):
    ...     def __init__(self, min_val, max_val, **kwargs):
    ...         controller = RangeController(min_val=min_val, max_val=max_val)
    ...         payload = RangeSliderPayload(
    ...             slider=controller.slider_widget,
    ...             min_display=controller.min_display_widget,
    ...             max_display=controller.max_display_widget
    ...         )
    ...         super().__init__(controller, payload, **kwargs)
    >>>
    >>> # Access hooks
    >>> min_hook = slider.get_hook_by_key("min_value")
    >>> max_hook = slider.get_hook_by_key("max_value")
    >>> available_hooks = slider.get_hook_keys()  # {"min_value", "max_value"}
    """

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