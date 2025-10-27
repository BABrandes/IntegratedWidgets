from typing import Optional, TypeVar, Generic, Callable, Literal, AbstractSet
from PySide6.QtWidgets import QWidget
from logging import Logger
from nexpy import Hook, XSetProtocol, XSingleValueProtocol
from nexpy.core import WritableHookProtocol
from dataclasses import dataclass

from integrated_widgets.controllers.composite.single_set_select_controller import SingleSetSelectController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a selection option widget."""
    combobox: QWidget


class IQtComboboxSelect(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], T | AbstractSet[T], Controller_Payload, SingleSetSelectController[T]], Generic[T]):
    """
    A dropdown (combo box) widget for selecting one option from a set.
    
    This widget provides a standard dropdown for selecting a single option from
    available options. The options are dynamically updated when the available
    options change. Supports custom formatting for display. Bidirectionally
    synchronizes with observables.
    
    Available hooks:
        - "selected_option": T - The currently selected option
        - "available_options": frozenset[T] - The set of available options
    
    Properties:
        selected_option: T - Get or set the selected option (read/write)
        available_options: frozenset[T] - Get the available options (read-only)
    """

    def __init__(
        self,
        selected_option: T | Hook[T] | XSingleValueProtocol[T] | XSingleValueProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.combobox,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the selection option widget.
        
        Parameters
        ----------
        selected_option : T | Hook[T] | XSingleValueProtocol[T, Hook[T]] | XSelectionOptionsProtocol[T]
            The initial selected option, or a hook/observable to bind to.
        available_options : AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None
            The initial set of available options, or a hook/observable to bind to. Can be None.
        formatter : Callable[[T], str], optional
            Function to format options for display. Default is str(item).
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = SingleSetSelectController(
            selected_option=selected_option,
            available_options=available_options,
            controlled_widgets={"combobox"},
            formatter=formatter,
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
    def selected_option(self) -> T:
        return self.get_value_of_hook_by_key("selected_option") # type: ignore

    @property
    def available_options(self) -> AbstractSet[T]:
        return self.get_value_of_hook_by_key("available_options") # type: ignore

    @selected_option.setter
    def selected_option(self, value: T) -> None:
        hook: Hook[T] = self.get_hook_by_key("selected_option") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def change_selected_option(self, value: T) -> None:
        hook: Hook[T] = self.get_hook_by_key("selected_option") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    @available_options.setter
    def available_options(self, value: AbstractSet[T]) -> None:
        hook: Hook[AbstractSet[T]] = self.get_hook_by_key("available_options") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def set_selected_option_and_available_options(self, selected_option: T, available_options: frozenset[T]) -> None:
        self.controller.submit_values({"selected_option": selected_option, "available_options": available_options})