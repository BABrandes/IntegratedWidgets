from typing import AbstractSet, Optional, Callable, Literal, Any, Mapping
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from dataclasses import dataclass

from nexpy import Hook, XDictProtocol, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from united_system import RealUnitedScalar, Unit, Dimension

from ..controllers.composite.real_united_scalar_controller import RealUnitedScalarController
from ..auxiliaries.default import default_debounce_ms
from ..auxiliaries.resources import DEFAULT_FLOAT_FORMAT_VALUE
from .foundation.iqt_composite_controller_widget_base import IQtCompositeControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for real united scalar widget."""
    real_united_scalar_label: QWidget
    real_united_scalar_line_edit: QWidget
    float_value_label: QWidget
    float_value_line_edit: QWidget
    unit_label: QWidget
    unit_line_edit: QWidget
    unit_combobox: QWidget
    unit_editable_combobox: QWidget
    
def layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.real_united_scalar_label)
    layout.addWidget(payload.real_united_scalar_line_edit)
    layout.addWidget(payload.float_value_label)
    layout.addWidget(payload.float_value_line_edit)
    layout.addWidget(payload.unit_label)
    layout.addWidget(payload.unit_line_edit)
    layout.addWidget(payload.unit_combobox)
    layout.addWidget(payload.unit_editable_combobox)
    return widget


class IQtRealUnitedScalarEntry(IQtCompositeControllerWidgetBase[Literal["value", "unit_options"], Any, Controller_Payload, RealUnitedScalarController]):
    """
    A comprehensive unit-aware numeric entry widget from united_system.
    
    This widget provides a complete interface for entering and displaying
    RealUnitedScalar values with automatic unit conversion and validation.
    Includes a label, line edit for value entry, and unit combo box. Users
    can type values with units (e.g., "5.2 km") and the widget handles
    parsing, validation, and conversion. Bidirectionally synchronizes with
    observables.
    
    Available hooks:
        - "value": RealUnitedScalar - The value with its unit
        - "unit_options": dict[Dimension, set[Unit]] - Available units by dimension
    
    Properties:
        value: RealUnitedScalar - Get or set the united scalar value (read/write)
        unit_options: dict[Dimension, set[Unit]] - Get or set unit options (read/write)
    """

    def __init__(
        self,
        value: RealUnitedScalar | Hook[RealUnitedScalar] | XSingleValueProtocol[RealUnitedScalar] = RealUnitedScalar.nan(Dimension.dimensionless_dimension()),
        display_unit_options: Optional[Mapping[Dimension, AbstractSet[Unit]]] | Hook[Mapping[Dimension, AbstractSet[Unit]]] | XDictProtocol[Dimension, AbstractSet[Unit]] = None,
        *,
        value_formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        unit_formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        unit_options_sorter: Callable[[AbstractSet[Unit]], list[Unit]] = lambda u: sorted(u, key=lambda x: x.format_string(as_fraction=True)),
        allowed_dimensions: Optional[AbstractSet[Dimension]] = None,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.real_united_scalar_label,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the real united scalar widget.
        
        Parameters
        ----------
        value : RealUnitedScalar | Hook[RealUnitedScalar] | XSingleValueProtocol[RealUnitedScalar, Hook[RealUnitedScalar]]
            The initial united scalar value, or a hook/observable to bind to. Default is NaN with dimensionless dimension.
        display_unit_options : Optional[dict[Dimension, set[Unit]]] | Hook[...] | XDictProtocol[...], optional
            Dictionary mapping dimensions to sets of display units, or a hook/observable to bind to. Default is None.
        value_formatter : Callable[[RealUnitedScalar], str], optional
            Function to format the value for display. Default is DEFAULT_FLOAT_FORMAT_VALUE.
        unit_formatter : Callable[[Unit], str], optional
            Function to format units for display. Default is u.format_string(as_fraction=True).
        unit_options_sorter : Callable[[set[Unit]], list[Unit]], optional
            Function to sort unit options for display. Default sorts alphabetically.
        allowed_dimensions : Optional[set[Dimension]], optional
            Set of allowed dimensions for validation. If None, all dimensions are allowed. Default is None.
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default vertical layout.
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = RealUnitedScalarController(
            value=value,
            display_unit_options=display_unit_options,
            value_formatter=value_formatter,
            unit_formatter=unit_formatter,
            unit_options_sorter=unit_options_sorter,
            allowed_dimensions=allowed_dimensions,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(
            real_united_scalar_label=controller.widget_real_united_scalar_label,
            real_united_scalar_line_edit=controller.widget_real_united_scalar_line_edit,
            float_value_label=controller.widget_float_value_label,
            float_value_line_edit=controller.widget_float_value_line_edit,
            unit_label=controller.widget_unit_label,
            unit_line_edit=controller.widget_unit_line_edit,
            unit_combobox=controller.widget_unit_combobox,
            unit_editable_combobox=controller.widget_unit_editable_combobox,
        )
        
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------

    @property
    def value_hook(self) -> Hook[RealUnitedScalar]:
        """
        Hook for the value.
        """
        return self.controller.value_hook
    
    @property
    def unit_options_hook(self) -> Hook[Mapping[Dimension, AbstractSet[Unit]]]:
        """
        Hook for the unit options.
        """
        return self.controller.unit_options_hook
    
    @property
    def unit_hook(self) -> Hook[Unit]:
        """
        Hook for the unit.
        """
        return self.controller.unit_hook
    
    @property
    def value(self) -> RealUnitedScalar:
        return self.get_hook_by_key("value").value # type: ignore

    @property
    def unit_options(self) -> dict[Dimension, set[Unit]]:
        return self.get_hook_by_key("unit_options").value # type: ignore

    @value.setter
    def value(self, value: RealUnitedScalar) -> None:
        self.controller.value = value

    def set_value(self, value: RealUnitedScalar) -> None:
        self.controller.value = value