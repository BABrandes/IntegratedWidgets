from typing import AbstractSet, Optional, TypeVar, Generic, Callable, Any, Literal
from logging import Logger
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from nexpy import Hook, XSetProtocol
from nexpy.core import NexusManager, WritableHookProtocol
from nexpy import default as nexpy_default

from ..controllers.composite.double_set_select_controller import DoubleSetSelectController
from ..auxiliaries.default import default_debounce_ms
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


class IQtDoubleListSelection(IQtControlledLayoutedWidget[Literal["selected_options", "available_options"], AbstractSet[T], Controller_Payload, DoubleSetSelectController[T]], Generic[T]):
    """
    A dual-list widget for selecting multiple options with move buttons.
    
    This widget provides two lists side by side: one for available options and
    one for selected options. Users can move items between lists using arrow
    buttons. Supports custom sorting of options. Both lists update dynamically
    when observables change. Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "selected_options": AbstractSet[T] - The set of selected options
        - "available_options": AbstractSet[T] - The set of all available options
    
    Properties:
        selected_options: AbstractSet[T] - Get or set the selected options (read/write)
        available_options: AbstractSet[T] - Get or set the available options (read/write)
        remaining_options: AbstractSet[T] - Get the unselected options (read-only)
    """

    def __init__(
        self,
        selected_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T],
        *,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        layout_strategy: LayoutStrategyBase[Controller_Payload] = layout_strategy,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the double list selection widget.
        
        Parameters
        ----------
        selected_options : frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T]
            The initial set of selected options, or a hook/observable to bind to.
        available_options : frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T]
            The initial set of all available options, or a hook/observable to bind to.
        order_by_callable : Callable[[T], Any], optional
            Function to extract sort key from options. Default is str(x).
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = DoubleSetSelectController(
            selected_options=selected_options,
            available_options=available_options,
            order_by_callable=order_by_callable,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(
            available_list=controller.widget_available_list,
            selected_list=controller.widget_selected_list,
            button_move_to_selected=controller.widget_button_move_to_selected,
            button_remove_from_selected=controller.widget_button_remove_from_selected
        )
        
        super().__init__(controller, payload, layout_strategy, parent=parent, logger=logger)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def selected_options_hook(self):
        """Hook for the selected options."""
        hook: Hook[AbstractSet[T]] = self.get_hook_by_key("selected_options") # type: ignore
        return hook
    
    @property
    def available_options_hook(self):
        """Hook for the available options."""
        hook: Hook[AbstractSet[T]] = self.get_hook_by_key("available_options") # type: ignore
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def selected_options(self) -> AbstractSet[T]:
        return self.get_hook_value_by_key("selected_options")

    @selected_options.setter
    def selected_options(self, value: AbstractSet[T]) -> None:
        hook = self.get_hook_by_key("selected_options")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def change_selected_options(self, value: AbstractSet[T]) -> None:
        hook = self.get_hook_by_key("selected_options")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    @property
    def available_options(self) -> AbstractSet[T]:
        return self.get_hook_value_by_key("available_options")

    @available_options.setter
    def available_options(self, value: AbstractSet[T]) -> None:
        hook = self.get_hook_by_key("available_options")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def change_available_options(self, value: AbstractSet[T]) -> None:
        hook = self.get_hook_by_key("available_options")
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    @property
    def remaining_options(self) -> AbstractSet[T]:
        return self.available_options - self.selected_options

    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------

    def change_selected_options_and_available_options(self, selected_options: AbstractSet[T], available_options: AbstractSet[T]) -> None:
        self.controller.submit_values({"selected_options": selected_options, "available_options": available_options})
