from typing import TypeVar, Generic, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import Hook, ObservableSingleValueProtocol, ObservableSelectionDict
from dataclasses import dataclass

from integrated_widgets.controllers.dict_selection_controller import DictSelectionController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase

K = TypeVar("K")
V = TypeVar("V")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a dict selection widget."""
    combobox: QWidget
    label: QWidget


class IQtDictSelection(IQtControlledLayoutedWidget[Literal["dict", "selected_key", "selected_value"], dict[K, V] | K | V, Controller_Payload, DictSelectionController[K, V]], Generic[K, V]):
    """
    A dropdown (combo box) widget for selecting one key from a dictionary.
    
    This widget provides a dropdown for selecting a single key from a dictionary.
    Keys are dynamically updated when the dictionary changes. The widget also 
    displays the selected value in a label. Bidirectionally synchronizes with 
    observables and provides dict-like interface.
    
    A key must always be selected, and the dictionary cannot be empty.
    
    Available hooks:
        - "dict": dict[K, V] - The dictionary of key-value pairs
        - "selected_key": K - The currently selected key
        - "selected_value": V - The value corresponding to the selected key
    
    Properties:
        dict_value: dict[K, V] - Get or set the dictionary (read/write)
        selected_key: K - Get or set the selected key (read/write)
        selected_value: V - Get the selected value (read-only, synchronized with selected_key)
    """

    def __init__(
        self,
        dict_value: dict[K, V] | Hook[dict[K, V]] | ObservableSelectionDict[K, V],
        selected_key: K | Hook[K] | ObservableSingleValueProtocol[K] | None = None,
        selected_value: V | Hook[V] | ObservableSingleValueProtocol[V] | None = None,
        *,
        formatter: Callable[[K], str] = lambda key: str(key),
        debounce_ms: int | None = None,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.combobox,
        parent: QWidget | None = None,
        logger: Logger | None = None
    ) -> None:
        """
        Initialize the dict selection widget.
        
        Parameters
        ----------
        dict_value : dict[K, V] | Hook[dict[K, V]] | ObservableDictProtocol[K, V] | ObservableSelectionDict[K, V]
            The initial dictionary (must not be empty), or a hook/observable to bind to.
        selected_key : K | Hook[K] | ObservableSingleValueProtocol[K] | None
            The initial selected key, or a hook/observable to bind to. If None, the first key is selected.
        selected_value : V | Hook[V] | ObservableSingleValueProtocol[V] | None
            The initial selected value, or a hook/observable to bind to. Can be None.
        formatter : Callable[[K], str], optional
            Function to format keys for display. Default is str(key).
        debounce_ms : int, optional
            Debounce time in milliseconds for value updates. If None, uses default debounce time.
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = DictSelectionController(
            dict_value=dict_value,
            selected_key=selected_key,
            selected_value=selected_value,
            formatter=formatter,
            debounce_ms=debounce_ms,
            logger=logger
        )

        payload = Controller_Payload(combobox=controller.widget_combobox, label=controller.widget_label)
        
        super().__init__(controller, payload, layout_strategy, parent)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def dict_hook(self):
        """Hook for the dictionary."""
        return self.controller.dict_hook
    
    @property
    def selected_key_hook(self):
        """Hook for the selected key."""
        return self.controller.selected_key_hook
    
    @property
    def selected_value_hook(self):
        """Hook for the selected value."""
        return self.controller.selected_value_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def dict_value(self) -> dict[K, V]:
        return self.get_value_of_hook("dict") # type: ignore

    @property
    def selected_key(self) -> K:
        return self.get_value_of_hook("selected_key") # type: ignore

    @property
    def selected_value(self) -> V:
        return self.get_value_of_hook("selected_value") # type: ignore

    @dict_value.setter
    def dict_value(self, value: dict[K, V]) -> None:
        self.controller.dict_value = value

    @selected_key.setter
    def selected_key(self, value: K) -> None:
        self.controller.selected_key = value

    def change_dict_value(self, value: dict[K, V]) -> None:
        self.controller.dict_value = value

    def change_selected_key(self, value: K) -> None:
        self.controller.selected_key = value

    def change_selected_value(self, value: V) -> None:
        self.controller.selected_value = value

    #--------------------------------------------------------------------------
    # Dict-like interface
    #--------------------------------------------------------------------------

    def __getitem__(self, key: K) -> V:
        """Get value by key."""
        return self.controller[key]

    def __setitem__(self, key: K, value: V) -> None:
        """Set value by key."""
        self.controller[key] = value

    def __delitem__(self, key: K) -> None:
        """Delete key-value pair."""
        del self.controller[key]

    def __contains__(self, key: K) -> bool:
        """Check if key exists."""
        return key in self.controller

    def __len__(self) -> int:
        """Get dictionary length."""
        return len(self.controller)

    def keys(self):
        """Get dictionary keys."""
        return self.controller.keys()

    def values(self):
        """Get dictionary values."""
        return self.controller.values()

    def items(self):
        """Get dictionary items."""
        return self.controller.items()

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get value by key with default."""
        return self.controller.get(key, default)

    def pop(self, key: K, default: V | None = None) -> V | None:
        """Pop value by key."""
        return self.controller.pop(key, default)

    def copy(self) -> dict[K, V]:
        """Copy dictionary."""
        return self.controller.copy()

