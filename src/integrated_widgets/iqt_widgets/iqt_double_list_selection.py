from typing import Optional, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from logging import Logger
from observables import HookLike, ObservableSetLike
from dataclasses import dataclass

from integrated_widgets.widget_controllers.double_list_selection_controller import DoubleListSelectionController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for double list selection widget."""
    available_list: QWidget
    selected_list: QWidget
    button_move_to_selected: QWidget
    button_remove_from_selected: QWidget


def layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    widget = QWidget()
    layout = QHBoxLayout(widget)

    # Available list
    available_layout = QVBoxLayout()
    available_layout.addWidget(QLabel("Available"))
    available_layout.addWidget(payload.available_list)
    layout.addLayout(available_layout)
    
    # Buttons in the middle
    button_layout = QVBoxLayout()
    button_layout.addStretch()
    button_layout.addWidget(payload.button_move_to_selected)
    button_layout.addWidget(payload.button_remove_from_selected)
    button_layout.addStretch()
    layout.addLayout(button_layout)
    
    # Selected list
    selected_layout = QVBoxLayout()
    selected_layout.addWidget(QLabel("Selected"))
    selected_layout.addWidget(payload.selected_list)
    layout.addLayout(selected_layout)
    
    return widget


class IQtDoubleListSelection(IQtControlledLayoutedWidget[Literal["selected_options", "available_options"], set[T], Controller_Payload, DoubleListSelectionController[T]], Generic[T]):
    """
    A dual-list widget for selecting multiple options with move buttons.
    
    This widget provides two lists side by side: one for available options and
    one for selected options. Users can move items between lists using arrow
    buttons. Supports custom sorting of options. Both lists update dynamically
    when observables change. Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "selected_options": set[T] - The set of selected options
        - "available_options": set[T] - The set of all available options
    
    Properties:
        selected_options: set[T] - Get or set the selected options (read/write)
        available_options: set[T] - Get or set the available options (read/write)
        remaining_options: set[T] - Get the unselected options (read-only)
    """

    def __init__(
        self,
        selected_options: set[T] | HookLike[set[T]] | ObservableSetLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T],
        *,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        layout_strategy: LayoutStrategyBase[Controller_Payload] = layout_strategy,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the double list selection widget.
        
        Parameters
        ----------
        selected_options : set[T] | HookLike[set[T]] | ObservableSetLike[T]
            The initial set of selected options, or a hook/observable to bind to.
        available_options : set[T] | HookLike[set[T]] | ObservableSetLike[T]
            The initial set of all available options, or a hook/observable to bind to.
        order_by_callable : Callable[[T], Any], optional
            Function to extract sort key from options. Default is str(x).
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = DoubleListSelectionController(
            selected_options=selected_options,
            available_options=available_options,
            order_by_callable=order_by_callable,
            logger=logger
        )

        payload = Controller_Payload(
            available_list=controller.widget_available_list,
            selected_list=controller.widget_selected_list,
            button_move_to_selected=controller.widget_button_move_to_selected,
            button_remove_from_selected=controller.widget_button_remove_from_selected
        )
        
        super().__init__(controller, payload, layout_strategy, parent)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def selected_options_hook(self):
        """Hook for the selected options."""
        return self.controller.selected_options_hook
    
    @property
    def available_options_hook(self):
        """Hook for the available options."""
        return self.controller.available_options_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def selected_options(self) -> set[T]:
        return self.get_value_of_hook("selected_options")

    @selected_options.setter
    def selected_options(self, value: set[T]) -> None:
        self.controller.selected_options = value

    def change_selected_options(self, value: set[T]) -> None:
        self.controller.selected_options = value

    @property
    def available_options(self) -> set[T]:
        return self.get_value_of_hook("available_options")

    @available_options.setter
    def available_options(self, value: set[T]) -> None:
        self.controller.available_options = value

    def change_available_options(self, value: set[T]) -> None:
        self.controller.available_options = value

    @property
    def remaining_options(self) -> set[T]:
        return self.available_options.difference(self.selected_options)

    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------

    def change_selected_options_and_available_options(self, selected_options: set[T], available_options: set[T]) -> None:
        self.controller.change_selected_options_and_available_options(selected_options, available_options)
