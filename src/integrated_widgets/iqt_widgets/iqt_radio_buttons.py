from typing import Optional, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableSelectionOptionLike
from dataclasses import dataclass, field

from integrated_widgets.widget_controllers.radio_buttons_controller import RadioButtonsController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for radio buttons widget."""
    radio_buttons: tuple[QWidget, ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate and register tuple of widgets."""
        # Use object.__setattr__ to bypass frozen restriction
        for widget in self.radio_buttons:
            if not isinstance(widget, QWidget): # type: ignore
                raise ValueError(f"All radio_buttons must be QWidgets, got {type(widget).__name__}")
        object.__setattr__(self, "_registered_widgets", set(self.radio_buttons))


class Controller_LayoutStrategy(LayoutStrategyBase[Controller_Payload], Generic[T]):
    """Default layout strategy for radio buttons widget."""
    def layout(self, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        for button in payload.radio_buttons:
            layout.addWidget(button)
        return widget


class IQtRadioButtons(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], T | set[T], Controller_Payload, RadioButtonsController[T]], Generic[T]):
    """
    A radio button group widget for exclusive selection with data binding.
    
    This widget provides a group of radio buttons for selecting one option from
    a set of available options. The buttons are dynamically created based on the
    available options and update automatically when options change. Supports
    custom formatting and sorting of options.
    
    Available hooks:
        - "selected_option": T - The currently selected option
        - "available_options": set[T] - The set of available options
    
    Properties:
        selected_option: T - Get or set the selected option (read/write)
        available_options: set[T] - Get or set the available options (read/write)
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
        """
        Initialize the radio buttons widget.
        
        Parameters
        ----------
        selected_option : T | HookLike[T] | ObservableSingleValueLike[T] | ObservableSelectionOptionLike[T]
            The initial selected option, or a hook/observable to bind to.
        available_options : set[T] | HookLike[set[T]] | ObservableSetLike[T] | None
            The initial set of available options, or a hook/observable to bind to. Can be None.
        formatter : Callable[[T], str], optional
            Function to format options for display. Default is str(item).
        sorter : Callable[[T], Any], optional
            Function to extract sort key from options. Default is str(item).
        layout_strategy : Controller_LayoutStrategy[T], optional
            Custom layout strategy for widget arrangement. If None, uses default vertical layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = RadioButtonsController[T](
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
    def selected_option(self) -> T:
        return self.get_value_of_hook("selected_option") # type: ignore

    @property
    def available_options(self) -> set[T]:
        return self.get_value_of_hook("available_options") # type: ignore

    @selected_option.setter
    def selected_option(self, value: T) -> None:
        self.controller.selected_option = value

    def change_selected_option(self, value: T) -> None:
        self.controller.selected_option = value

    @available_options.setter
    def available_options(self, value: set[T]) -> None:
        self.controller.available_options = value

    def change_selected_option_and_available_options(self, selected_option: T, available_options: set[T]) -> None:
        self.controller.change_selected_option_and_available_options(selected_option, available_options)