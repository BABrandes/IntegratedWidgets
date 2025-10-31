from typing import Optional, TypeVar, Generic, Callable, Any, Literal, AbstractSet
from logging import Logger
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QVBoxLayout

from nexpy import Hook, XSetProtocol, XSingleValueProtocol
from nexpy.core import WritableHookProtocol, NexusManager
from nexpy import default as nexpy_default

from integrated_widgets.controlled_widgets.controlled_radio_button_group import ControlledRadioButtonGroup

from ..controllers.composite.single_set_select_controller import SingleSetSelectController
from ..auxiliaries.default import default_debounce_ms
from .foundation.iqt_composite_controller_widget_base import IQtCompositeControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for radio buttons widget."""
    radio_button_group: ControlledRadioButtonGroup


def layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)

    def rebuild_layout():
        # Clear existing items
        while layout.count():
            item = layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)  # or keep for reuse
        # Re-add in controller order (sort by ID if needed)
        for b in sorted(payload.radio_button_group.buttons(), key=lambda btn: payload.radio_button_group.id(btn)):
            layout.addWidget(b)

    payload.radio_button_group.contentChanged.connect(rebuild_layout) # type: ignore

    return widget


class IQtRadioButtonsSelect(IQtCompositeControllerWidgetBase[Literal["selected_option", "available_options"], T | AbstractSet[T], Controller_Payload, SingleSetSelectController[T]], Generic[T]):
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
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
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
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
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
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(radio_button_group=controller.widget_radio_button_group)
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    def __str__(self) -> str:
        selected = self.selected_option
        count = len(self.available_options)
        selected_str = str(selected)
        if len(selected_str) > 15:
            selected_str = selected_str[:12] + "..."
        return f"{self.__class__.__name__}(selected={selected_str!r}, options={count})"

    def __repr__(self) -> str:
        selected = self.selected_option
        count = len(self.available_options)
        selected_str = str(selected)
        if len(selected_str) > 15:
            selected_str = selected_str[:12] + "..."
        return f"{self.__class__.__name__}(selected={selected_str!r}, options={count}, id={hex(id(self))})"

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