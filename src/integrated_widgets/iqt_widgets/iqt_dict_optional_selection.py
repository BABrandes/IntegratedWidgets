from typing import Optional, TypeVar, Generic, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import Hook, ObservableSingleValueProtocol, ObservableOptionalSelectionDict
from dataclasses import dataclass

from integrated_widgets.widget_controllers.dict_optional_selection_controller import DictOptionalSelectionController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase

K = TypeVar("K")
V = TypeVar("V")


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a dict optional selection widget."""
    combobox: QWidget
    label: QWidget


class IQtDictOptionalSelection(IQtControlledLayoutedWidget[Literal["dict", "selected_key", "selected_value"], dict[K, V] | Optional[K] | Optional[V], Controller_Payload, DictOptionalSelectionController[K, V]], Generic[K, V]):
    """
    A dropdown (combo box) widget for selecting one key from a dictionary with optional selection.
    
    This widget provides a dropdown for selecting a single key from a dictionary,
    with support for "None" selection. The None option appears at the top of the
    list with customizable text. Keys are dynamically updated when the dictionary
    changes. The widget also displays the selected value in a label. 
    Bidirectionally synchronizes with observables and provides dict-like interface.
    
    Available hooks:
        - "dict": dict[K, V] - The dictionary of key-value pairs
        - "selected_key": Optional[K] - The currently selected key (can be None)
        - "selected_value": Optional[V] - The value corresponding to the selected key (can be None)
    
    Properties:
        dict_value: dict[K, V] - Get or set the dictionary (read/write)
        selected_key: Optional[K] - Get or set the selected key (read/write, can be None)
        selected_value: Optional[V] - Get the selected value (read-only, synchronized with selected_key)
    """

    def __init__(
        self,
        dict_value: dict[K, V] | Hook[dict[K, V]] | ObservableOptionalSelectionDict[K, V],
        selected_key: Optional[K] | Hook[Optional[K]] | ObservableSingleValueProtocol[Optional[K]] | None = None,
        selected_value: Optional[V] | Hook[Optional[V]] | ObservableSingleValueProtocol[Optional[V]] | None = None,
        *,
        formatter: Callable[[K], str] = lambda key: str(key),
        none_option_text: str = "-",
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.combobox,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the dict optional selection widget.
        
        Parameters
        ----------
        dict_value : dict[K, V] | Hook[dict[K, V]] | ObservableDictProtocol[K, V] | ObservableOptionalSelectionDict[K, V]
            The initial dictionary, or a hook/observable to bind to.
        selected_key : Optional[K] | Hook[Optional[K]] | ObservableSingleValueProtocol[Optional[K]] | None
            The initial selected key (can be None), or a hook/observable to bind to. Can be None.
        selected_value : Optional[V] | Hook[Optional[V]] | ObservableSingleValueProtocol[Optional[V]] | None
            The initial selected value, or a hook/observable to bind to. Can be None.
        formatter : Callable[[K], str], optional
            Function to format keys for display. Default is str(key).
        none_option_text : str, optional
            Text to display for the None option. Default is "-".
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = DictOptionalSelectionController(
            dict_value=dict_value,
            selected_key=selected_key,
            selected_value=selected_value,
            formatter=formatter,
            none_option_text=none_option_text,
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
    def selected_key(self) -> Optional[K]:
        return self.get_value_of_hook("selected_key") # type: ignore

    @property
    def selected_value(self) -> Optional[V]:
        return self.get_value_of_hook("selected_value") # type: ignore

    @dict_value.setter
    def dict_value(self, value: dict[K, V]) -> None:
        self.controller.dict_value = value

    @selected_key.setter
    def selected_key(self, value: Optional[K]) -> None:
        self.controller.selected_key = value

    def change_dict_value(self, value: dict[K, V]) -> None:
        self.controller.dict_value = value

    def change_selected_key(self, value: Optional[K]) -> None:
        self.controller.selected_key = value

    def change_selected_value(self, value: Optional[V]) -> None:
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

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Get value by key with default."""
        return self.controller.get(key, default)

    def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Pop value by key."""
        return self.controller.pop(key, default)

    def clear(self) -> None:
        """Clear dictionary."""
        self.controller.clear()

    def copy(self) -> dict[K, V]:
        """Copy dictionary."""
        return self.controller.copy()
