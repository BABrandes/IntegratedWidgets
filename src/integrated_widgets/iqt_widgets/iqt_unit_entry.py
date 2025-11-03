from typing import Optional, Callable, Literal, Any, AbstractSet, Mapping
from dataclasses import dataclass
from logging import Logger

from PySide6.QtWidgets import QWidget, QVBoxLayout

from nexpy import Hook, XDictProtocol, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from united_system import Unit, Dimension

from integrated_widgets.controlled_widgets import ControlledEditableComboBox, ControlledComboBox, ControlledQLabel, ControlledLineEdit

from ..controllers.composite.unit_select_controller import UnitSelectController
from ..auxiliaries.default import default_debounce_ms
from .foundation.iqt_composite_controller_widget_base import IQtCompositeControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a unit combo box widget."""
    unit_label: ControlledQLabel
    unit_line_edit: ControlledLineEdit
    unit_combobox: ControlledComboBox
    unit_editable_combobox: ControlledEditableComboBox


def layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.unit_label)
    layout.addWidget(payload.unit_line_edit)
    layout.addWidget(payload.unit_combobox)
    layout.addWidget(payload.unit_editable_combobox)
    return widget

class IQtUnitEntry(IQtCompositeControllerWidgetBase[Literal["selected_unit", "available_units"], Any, Controller_Payload, UnitSelectController]):
    """
    A dropdown for selecting physical units from united_system.
    
    This widget provides a dropdown for selecting a Unit from a dictionary of
    available units organized by Dimension. Supports dimension filtering to
    show only units of specific dimensions. Validates selected units against
    allowed dimensions. Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "selected_unit": Unit - The currently selected unit
        - "available_units": dict[Dimension, set[Unit]] - Available units by dimension
    
    Properties:
        selected_unit: Unit - Get or set the selected unit (read/write)
        available_units: dict[Dimension, set[Unit]] - Get or set available units (read/write)
    """

    def __init__(
        self,
        selected_unit: Unit | Hook[Unit] | XSingleValueProtocol[Unit],
        available_units: Mapping[Dimension, AbstractSet[Unit]] | Hook[Mapping[Dimension, AbstractSet[Unit]]] | XDictProtocol[Dimension, AbstractSet[Unit]],
        *,
        allowed_dimensions: None | AbstractSet[Dimension] = None,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.unit_label,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the unit combo box widget.
        
        Parameters
        ----------
        selected_unit : Unit | Hook[Unit] | XSingleValueProtocol[Unit]
            The initial selected unit, or a hook/observable to bind to.
        available_units : Mapping[Dimension, AbstractSet[Unit]] | Hook[Mapping[Dimension, AbstractSet[Unit]]] | XDictProtocol[Dimension, AbstractSet[Unit]]
            Dictionary mapping dimensions to sets of available units, or a hook/observable to bind to.
        allowed_dimensions : None | AbstractSet[Dimension] optional
            Set of allowed dimensions for validation. If None, all dimensions are allowed. Default is None.
        formatter : Callable[[Unit], str], optional
            Function to format units for display. Default is u.format_string(as_fraction=True). 
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. Default is default layout.
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = UnitSelectController(
            selected_unit=selected_unit,
            available_units=available_units,
            allowed_dimensions=allowed_dimensions,
            formatter=formatter,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(unit_label=controller.widget_unit_label, unit_line_edit=controller.widget_unit_line_edit, unit_combobox=controller.widget_unit_combobox, unit_editable_combobox=controller.widget_unit_editable_combobox)

        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    def __str__(self) -> str:
        unit = self.selected_unit
        unit_str = str(unit)
        if len(unit_str) > 15:
            unit_str = unit_str[:12] + "..."
        return f"{self.__class__.__name__}(unit={unit_str!r})"

    def __repr__(self) -> str:
        unit = self.selected_unit
        unit_str = str(unit)
        if len(unit_str) > 15:
            unit_str = unit_str[:12] + "..."
        return f"{self.__class__.__name__}(unit={unit_str!r}, id={hex(id(self))})"

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
    def selected_unit(self) -> Unit:
        return self.get_hook_by_key("selected_unit").value # type: ignore

    @property
    def available_units(self) -> dict[Dimension, set[Unit]]:
        return self.get_hook_by_key("available_units").value # type: ignore

    @selected_unit.setter
    def selected_unit(self, value: Unit) -> None:
        self.controller.selected_unit = value

    def change_selected_unit(self, value: Unit) -> None:
        self.controller.selected_unit = value

    @available_units.setter
    def available_units(self, value: dict[Dimension, set[Unit]]) -> None:
        self.controller.submit_values({"available_units": value})

    def change_available_units(self, value: dict[Dimension, set[Unit]]) -> None:
        self.controller.submit_values({"available_units": value})
        
    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------

    def change_selected_unit_and_available_units(self, selected_unit: Unit, available_units: dict[Dimension, set[Unit]]) -> None:
        self.controller.submit_values({"selected_unit": selected_unit, "available_units": available_units})