from typing import Generic, TypeVar, Any, Literal, Optional
from logging import Logger

from PySide6.QtWidgets import QWidget

from nexpy import Hook

from ...controllers.core.base_singleton_controller import BaseSingletonController
from .iqt_controller_widget_base import IQtControllerWidgetBase
from .layout_payload_base import LayoutPayloadBase
from .layout_strategy_base import LayoutStrategyBase

T = TypeVar("T")
P = TypeVar("P", bound=LayoutPayloadBase)
C = TypeVar("C", bound=BaseSingletonController[Any])


class IQtSingletonControllerWidgetBase(IQtControllerWidgetBase[Literal["value"], T, P, C], Generic[T, P, C]):
    """
    Base class for IQT widgets that manage a single value through a controller.

    This class extends IQtControllerWidgetBase and provides convenient access to the single
    "value" hook that singleton controllers manage. It automatically exposes the value
    through properties and methods for easy access.

    Type Parameters
    --------------
    T : Any
        The type of the single value managed by the controller
    P : LayoutPayloadBase
        The payload type containing the widgets to be arranged
    C : BaseSingletonController
        The controller type that manages the single value

    Properties
    ----------
    hook : Hook[T]
        The "value" hook from the controller for direct hook access
    value : T
        Get or set the current value (convenience property)

    Methods
    -------
    change_value(value: T) -> None
        Change the value with proper validation and lifecycle handling

    Examples
    --------
    Creating a custom checkbox widget:

    >>> @dataclass(frozen=True)
    ... class CheckBoxPayload(LayoutPayloadBase):
    ...     check_box: QWidget
    >>>
    >>> class MyCheckBox(IQtSingletonControllerWidgetBase[bool, CheckBoxPayload, CheckBoxController]):
    ...     def __init__(self, value, **kwargs):
    ...         controller = CheckBoxController(value)
    ...         payload = CheckBoxPayload(check_box=controller.widget_check_box)
    ...         super().__init__(controller, payload, **kwargs)
    >>>
    >>> # Use it
    >>> checkbox = MyCheckBox(True, text="Enable")
    >>> checkbox.value = False  # Updates automatically
    """

    def __init__(
        self,
        controller: C,
        payload: P,
        *,
        layout_strategy: Optional[LayoutStrategyBase[P]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
        **layout_strategy_kwargs: Any
        ) -> None:
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger, **layout_strategy_kwargs)

    @property
    def hook(self) -> Hook[T]:
        return self.controller.value_hook

    @property
    def value(self) -> T:
        return self.controller.value

    @value.setter
    def value(self, value: T) -> None:
        self.controller.value = value

    def change_value(self, value: T) -> None:
        self.controller.change_value(value)