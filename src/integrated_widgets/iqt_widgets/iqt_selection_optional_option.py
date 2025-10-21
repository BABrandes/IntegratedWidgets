from typing import Optional, TypeVar, Generic, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from nexpy import Hook, XSetProtocol
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.x_objects.set_like.protocols import XOptionalSelectionOptionProtocol
from dataclasses import dataclass

from integrated_widgets.controllers.list_optional_selection_controller import ListOptionalSelectionController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a selection optional option widget."""
    combobox: QWidget


class IQtSelectionOptionalOption(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], Optional[T] | frozenset[T], Controller_Payload, ListOptionalSelectionController[T]], Generic[T]):
    """
    A dropdown (combo box) widget for selecting one option or None from a set.
    
    This widget provides a dropdown for selecting a single option from available
    options, with support for "None" selection. The None option appears at the
    top of the list with customizable text. Options are dynamically updated when
    the available options change. Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "selected_option": Optional[T] - The currently selected option (can be None)
        - "available_options": frozenset[T] - The set of available options
    
    Properties:
        selected_option: Optional[T] - Get or set the selected option (read/write, can be None)
        available_options: frozenset[T] - Get or set the available options (read/write)
    """

    def __init__(
        self,
        selected_option: Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T], Hook[Optional[T]]] | XOptionalSelectionOptionProtocol[T],
        available_options: frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_text: str = "-",
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.combobox,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the selection optional option widget.
        
        Parameters
        ----------
        selected_option : Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T], Hook[Optional[T]]] | XOptionalSelectionOptionProtocol[T]
            The initial selected option (can be None), or a hook/observable to bind to.
        available_options : frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T] | None
            The initial set of available options, or a hook/observable to bind to. Can be None.
        formatter : Callable[[T], str], optional
            Function to format options for display. Default is str(item).
        none_option_text : str, optional
            Text to display for the None option. Default is "-".
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = ListOptionalSelectionController(
            selected_option=selected_option,
            available_options=available_options,
            formatter=formatter,
            none_option_text=none_option_text,
            logger=logger
        )

        payload = Controller_Payload(combobox=controller.widget_combobox)
        
        super().__init__(controller, payload, layout_strategy, parent)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def selected_option_hook(self):
        """Hook for the selected option."""
        return self.controller.selected_option_hook
    
    @property
    def available_options_hook(self):
        """Hook for the available options."""
        return self.controller.available_options_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def selected_option(self) -> Optional[T]:
        return self.get_value_of_hook("selected_option") # type: ignore

    @property
    def available_options(self) -> frozenset[T]:
        return self.get_value_of_hook("available_options") # type: ignore

    @selected_option.setter
    def selected_option(self, value: Optional[T]) -> None:
        self.controller.selected_option = value

    def change_selected_option(self, value: Optional[T]) -> None:
        self.controller.selected_option = value

    @available_options.setter
    def available_options(self, value: frozenset[T]) -> None:
        self.controller.available_options = value
    
    def change_selected_option_and_available_options(self, selected_option: Optional[T], available_options: frozenset[T]) -> None:
        self.controller.change_selected_option_and_available_options(selected_option, available_options)