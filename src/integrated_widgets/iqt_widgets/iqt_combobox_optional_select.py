from typing import Optional, TypeVar, Generic, Callable, Literal, AbstractSet
from PySide6.QtWidgets import QWidget
from logging import Logger
from nexpy import Hook, XSetProtocol, XSingleValueProtocol
from nexpy.core import WritableHookProtocol
from dataclasses import dataclass

from ..controllers.composite.single_set_optional_select_controller import SingleSetOptionalSelectController
from .foundation.iqt_composite_controller_widget_base import IQtCompositeControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase
from ..auxiliaries.default import default_debounce_ms
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a selection optional option widget."""
    combobox: QWidget


class IQtComboboxOptionalSelect(IQtCompositeControllerWidgetBase[Literal["selected_option", "available_options"], Optional[T] | AbstractSet[T], Controller_Payload, SingleSetOptionalSelectController[T]], Generic[T]):
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
        selected_option: Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T]] | XSingleValueProtocol[Optional[T]],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_text: str = "-",
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.combobox,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the selection optional option widget.
        
        Parameters
        ----------
        selected_option : Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T], Hook[Optional[T]]] | XOptionalSelectionOptionProtocol[T]
            The initial selected option (can be None), or a hook/observable to bind to.
        available_options : AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None
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

        controller = SingleSetOptionalSelectController(
            selected_option=selected_option,
            available_options=available_options,
            controlled_widgets={"combobox"},
            formatter=formatter,
            none_option_text=none_option_text,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(combobox=controller.widget_combobox)
        
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def selected_option_hook(self) -> Hook[Optional[T]]:
        """Hook for the selected option."""
        return self.get_hook_by_key("selected_option") # type: ignore
    
    @property
    def available_options_hook(self) -> Hook[AbstractSet[T]]:
        """Hook for the available options."""
        return self.get_hook_by_key("available_options") # type: ignore

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def selected_option(self) -> Optional[T]:
        return self.get_hook_value_by_key("selected_option") # type: ignore

    @property
    def available_options(self) -> AbstractSet[T]:
        return self.get_hook_value_by_key("available_options") # type: ignore

    @selected_option.setter
    def selected_option(self, value: Optional[T]) -> None:
        hook: Hook[Optional[T]] = self.get_hook_by_key("selected_option") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def change_selected_option(self, value: Optional[T]) -> None:
        hook: Hook[Optional[T]] = self.get_hook_by_key("selected_option") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    @available_options.setter
    def available_options(self, value: frozenset[T]) -> None:
        hook: Hook[AbstractSet[T]] = self.get_hook_by_key("available_options") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")
    
    def change_selected_option_and_available_options(self, selected_option: Optional[T], available_options: frozenset[T]) -> None:
        self.controller.submit_values({"selected_option": selected_option, "available_options": available_options})