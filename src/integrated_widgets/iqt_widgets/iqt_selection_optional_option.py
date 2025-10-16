from typing import Optional, TypeVar, Generic, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableOptionalSelectionOptionLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.selection_optional_option_controller import SelectionOptionalOptionController
from .layout_payload import BaseLayoutPayload

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a selection optional option widget."""
    combobox: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload], Generic[T]):
    """Default layout strategy for selection optional option widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.combobox


class IQtSelectionOptionalOption(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], Optional[T] | set[T], Controller_Payload, SelectionOptionalOptionController[T]], Generic[T]):
    """
    Available hooks:
        - "selected_option": Optional[T]
        - "available_options": set[T]
    """

    def __init__(
        self,
        selected_option: Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_text: str = "-",
        layout_strategy: Optional[Controller_LayoutStrategy[T]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = SelectionOptionalOptionController(
            selected_option=selected_option,
            available_options=available_options,
            formatter=formatter,
            none_option_text=none_option_text,
            logger=logger
        )

        payload = Controller_Payload(combobox=controller.widget_combobox)
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)

    @property
    def selected_option(self) -> Optional[T]:
        return self.get_value_of_hook("selected_option") # type: ignore

    @property
    def available_options(self) -> set[T]:
        return self.get_value_of_hook("available_options") # type: ignore
