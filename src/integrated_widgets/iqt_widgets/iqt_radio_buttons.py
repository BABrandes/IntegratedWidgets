from typing import Optional, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableSelectionOptionLike
from dataclasses import dataclass, field

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.radio_buttons_controller import RadioButtonsController
from .layout_payload import BaseLayoutPayload

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for radio buttons widget."""
    radio_buttons: tuple[QWidget, ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate and register tuple of widgets."""
        # Use object.__setattr__ to bypass frozen restriction
        for widget in self.radio_buttons:
            if not isinstance(widget, QWidget):
                raise ValueError(f"All radio_buttons must be QWidgets, got {type(widget).__name__}")
        object.__setattr__(self, "_registered_widgets", set(self.radio_buttons))


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload], Generic[T]):
    """Default layout strategy for radio buttons widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        for button in payload.radio_buttons:
            layout.addWidget(button)
        return widget


class IQtRadioButtons(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], T | set[T], Controller_Payload, RadioButtonsController[T]], Generic[T]):
    """
    Available hooks:
        - "selected_option": T
        - "available_options": set[T]
    """

    def __init__(
        self,
        selected_option: T | HookLike[T] | ObservableSingleValueLike[T] | ObservableSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        sorter: Callable[[T], Any] = lambda item: str(item),
        layout_strategy: Optional[Controller_LayoutStrategy[T]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = RadioButtonsController(
            selected_option=selected_option,
            available_options=available_options,
            formatter=formatter,
            sorter=sorter,
            logger=logger
        )

        payload = Controller_Payload(radio_buttons=tuple(controller.widget_radio_buttons))
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)

    @property
    def selected_option(self) -> T:
        return self.get_value_of_hook("selected_option") # type: ignore

    @property
    def available_options(self) -> set[T]:
        return self.get_value_of_hook("available_options") # type: ignore
