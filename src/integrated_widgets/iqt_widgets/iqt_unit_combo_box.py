from typing import Optional, Callable, Literal, Any
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableDictLike, ObservableSetLike
from united_system import Unit, Dimension
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.unit_combo_box_controller import UnitComboBoxController
from .layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a unit combo box widget."""
    combobox: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for unit combo box widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.combobox


class IQtUnitComboBox(IQtControlledLayoutedWidget[Literal["selected_unit", "available_units"], Any, Controller_Payload, UnitComboBoxController]):
    """
    A dropdown for selecting physical units from united_system.
    
    This widget provides a dropdown for selecting a Unit from a dictionary of
    available units organized by Dimension. Supports dimension filtering to
    show only units of specific dimensions. Validates selected units against
    allowed dimensions. Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "selected_unit": Optional[Unit] - The currently selected unit (can be None)
        - "available_units": dict[Dimension, set[Unit]] - Available units by dimension
    
    Properties:
        selected_unit: Optional[Unit] - Get or set the selected unit (read/write, can be None)
        available_units: dict[Dimension, set[Unit]] - Get or set available units (read/write)
    """

    def __init__(
        self,
        selected_unit: Optional[Unit] | HookLike[Optional[Unit]] | ObservableSingleValueLike[Optional[Unit]],
        available_units: dict[Dimension, set[Unit]] | HookLike[dict[Dimension, set[Unit]]] | ObservableDictLike[Dimension, set[Unit]],
        *,
        allowed_dimensions: None | set[Dimension] | HookLike[set[Dimension]] | ObservableSetLike[Dimension] = None,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        blank_if_none: bool = True,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the unit combo box widget.
        
        Parameters
        ----------
        selected_unit : Optional[Unit] | HookLike[Optional[Unit]] | ObservableSingleValueLike[Optional[Unit]]
            The initial selected unit (can be None), or a hook/observable to bind to.
        available_units : dict[Dimension, set[Unit]] | HookLike[...] | ObservableDictLike[Dimension, set[Unit]]
            Dictionary mapping dimensions to sets of available units, or a hook/observable to bind to.
        allowed_dimensions : None | set[Dimension] | HookLike[set[Dimension]] | ObservableSetLike[Dimension], optional
            Set of allowed dimensions for validation. If None, all dimensions are allowed. Default is None.
        formatter : Callable[[Unit], str], optional
            Function to format units for display. Default is u.format_string(as_fraction=True).
        blank_if_none : bool, optional
            If True, widget appears blank when unit is None. Default is True.
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = UnitComboBoxController(
            selected_unit=selected_unit,
            available_units=available_units,
            allowed_dimensions=allowed_dimensions,
            formatter=formatter,
            blank_if_none=blank_if_none,
            logger=logger
        )

        payload = Controller_Payload(combobox=controller.widget_combobox)
        
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
    def selected_unit_hook(self):
        """Hook for the selected unit."""
        return self.controller.selected_unit_hook
    
    @property
    def available_units_hook(self):
        """Hook for the available units."""
        return self.controller.available_units_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def selected_unit(self) -> Optional[Unit]:
        return self.get_value_of_hook("selected_unit") # type: ignore

    @property
    def available_units(self) -> dict[Dimension, set[Unit]]:
        return self.get_value_of_hook("available_units") # type: ignore

    @selected_unit.setter
    def selected_unit(self, value: Optional[Unit]) -> None:
        self.controller.selected_unit = value

    def change_selected_unit(self, value: Optional[Unit]) -> None:
        self.controller.selected_unit = value

    @available_units.setter
    def available_units(self, value: dict[Dimension, set[Unit]]) -> None:
        self.controller.submit_values({"available_units": value})

    def change_available_units(self, value: dict[Dimension, set[Unit]]) -> None:
        self.controller.submit_values({"available_units": value})
        
    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------

    def change_selected_unit_and_available_units(self, selected_unit: Optional[Unit], available_units: dict[Dimension, set[Unit]]) -> None:
        self.controller.submit_values({"selected_unit": selected_unit, "available_units": available_units})