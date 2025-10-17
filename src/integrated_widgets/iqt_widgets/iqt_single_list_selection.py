from typing import Optional, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableOptionalSelectionOptionLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.single_list_selection_controller import SingleListSelectionController
from .layout_payload import BaseLayoutPayload

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a single list selection widget."""
    list_widget: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload], Generic[T]):
    """Default layout strategy for single list selection widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.list_widget


class IQtSingleListSelection(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], Optional[T] | set[T], Controller_Payload, SingleListSelectionController[T]], Generic[T]):
    """
    A list widget for selecting one option from a list.
    
    This widget provides a scrollable list for selecting a single option from
    available options. Supports optional deselection (allowing None selection)
    and custom formatting/sorting. Options are dynamically updated when the
    available options change. Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "selected_option": Optional[T] - The currently selected option (can be None)
        - "available_options": set[T] - The set of available options
    
    Properties:
        selected_option: Optional[T] - Get or set the selected option (read/write, can be None)
        available_options: set[T] - Get or set the available options (read/write)
    """

    def __init__(
        self,
        selected_option: Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        formatter: Callable[[T], str] = str,
        allow_deselection: bool = True,
        layout_strategy: Optional[Controller_LayoutStrategy[T]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the single list selection widget.
        
        Parameters
        ----------
        selected_option : Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T]
            The initial selected option (can be None), or a hook/observable to bind to.
        available_options : set[T] | HookLike[set[T]] | ObservableSetLike[T] | None
            The initial set of available options, or a hook/observable to bind to. Can be None.
        order_by_callable : Callable[[T], Any], optional
            Function to extract sort key from options. Default is str(x).
        formatter : Callable[[T], str], optional
            Function to format options for display. Default is str.
        allow_deselection : bool, optional
            If True, allows deselecting (None selection). Default is True.
        layout_strategy : Controller_LayoutStrategy[T], optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = SingleListSelectionController(
            selected_option=selected_option,
            available_options=available_options,
            order_by_callable=order_by_callable,
            formatter=formatter,
            allow_deselection=allow_deselection,
            logger=logger
        )

        payload = Controller_Payload(list_widget=controller.widget_list)
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)

    @property
    def selected_option(self) -> Optional[T]:
        return self.get_value_of_hook("selected_option") # type: ignore

    @property
    def available_options(self) -> set[T]:
        return self.get_value_of_hook("available_options") # type: ignore

    @selected_option.setter
    def selected_option(self, value: Optional[T]) -> None:
        self.controller.selected_option = value

    def set_selected_option(self, value: Optional[T]) -> None:
        self.controller.selected_option = value

    @available_options.setter
    def available_options(self, value: set[T]) -> None:
        self.controller.available_options = value
    def set_selected_option_and_available_options(self, selected_option: Optional[T], available_options: set[T]) -> None:
        self.controller.submit_values({"selected_option": selected_option, "available_options": available_options})