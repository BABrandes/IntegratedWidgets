from typing import Optional, TypeVar, Generic, Callable, Any, Literal, AbstractSet
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from nexpy import Hook, XSetProtocol
from nexpy.core import WritableHookProtocol
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from dataclasses import dataclass, field

from integrated_widgets.controllers.composite.single_set_select_controller import SingleSetSelectController
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


def layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    for button in payload.radio_buttons:
        layout.addWidget(button)
    return widget


class IQtRadioButtons(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], T | AbstractSet[T], Controller_Payload, SingleSetSelectController[T]], Generic[T]):
    """
    A radio button group widget for exclusive selection with data binding.
    
    This widget provides a group of radio buttons for selecting one option from
    a set of available options. The buttons are dynamically created based on the
    available options and update automatically when options change. Supports
    custom formatting and sorting of options.
    
    Available hooks:
        - "selected_option": T - The currently selected option
        - "available_options": frozenset[T] - The set of available options
    
    Properties:
        selected_option: T - Get or set the selected option (read/write)
        available_options: frozenset[T] - Get or set the available options (read/write)
    """

    def __init__(
        self,
        selected_option: T | Hook[T] | XSingleValueProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        sorter: Callable[[T], Any] = lambda item: str(item),
        layout_strategy: LayoutStrategyBase[Controller_Payload] = layout_strategy,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the radio buttons widget.
        
        Parameters
        ----------
        selected_option : T | Hook[T] | XSingleValueProtocol[T]
            The initial selected option, or a hook/observable to bind to.
        available_options : AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None
            The initial set of available options, or a hook/observable to bind to. Can be None.
        formatter : Callable[[T], str], optional
            Function to format options for display. Default is str(item).
        sorter : Callable[[T], Any], optional
            Function to extract sort key from options. Default is str(item).
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. If None, uses default vertical layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = SingleSetSelectController[T](
            selected_option=selected_option,
            available_options=available_options,
            controlled_widgets={"radio_buttons"},
            formatter=formatter,
            sorter=sorter,
            logger=logger
        )

        payload = Controller_Payload(radio_buttons=tuple(controller.widget_radio_buttons))
        
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
        return self.get_hook_value_by_key("selected_option") # type: ignore

    @property
    def available_options(self) -> frozenset[T]:
        return self.get_hook_value_by_key("available_options") # type: ignore

    @selected_option.setter
    def selected_option(self, value: T) -> None:
        hook = self.get_hook_by_key("selected_option")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def change_selected_option(self, value: T) -> None:
        hook = self.get_hook_by_key("selected_option")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    @available_options.setter
    def available_options(self, value: frozenset[T]) -> None:
        hook = self.get_hook_by_key("available_options")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def change_selected_option_and_available_options(self, selected_option: T, available_options: frozenset[T]) -> None:
        hook = self.get_hook_by_key("selected_option")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(selected_option)
        else:
            raise ValueError(f"Hook {hook} is not writable")
        hook = self.get_hook_by_key("available_options")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(available_options)
        else:
            raise ValueError(f"Hook {hook} is not writable")