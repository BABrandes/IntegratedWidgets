from typing import Optional, Callable, Literal, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableDictLike
from united_system import RealUnitedScalar, Unit, Dimension
from dataclasses import dataclass

from observables.core import HookWithOwnerLike

from integrated_widgets.widget_controllers.real_united_scalar_controller import RealUnitedScalarController
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from .core.layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for real united scalar widget."""
    label: QWidget
    line_edit: QWidget
    combobox: QWidget
    editable_combobox: QWidget

class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for real united scalar widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(payload.label)
        layout.addWidget(payload.line_edit)
        layout.addWidget(payload.combobox)
        layout.addWidget(payload.editable_combobox)
        return widget


class IQtRealUnitedScalar(IQtControlledLayoutedWidget[Literal["value", "unit_options"], Any, Controller_Payload, RealUnitedScalarController]):
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
        value: RealUnitedScalar | HookLike[RealUnitedScalar] | ObservableSingleValueLike[RealUnitedScalar] = RealUnitedScalar.nan(Dimension.dimensionless_dimension()),
        display_unit_options: Optional[dict[Dimension, set[Unit]]] | HookLike[dict[Dimension, set[Unit]]] | ObservableDictLike[Dimension, set[Unit]] = None,
        *,
        value_formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        unit_formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        unit_options_sorter: Callable[[set[Unit]], list[Unit]] = lambda u: sorted(u, key=lambda x: x.format_string(as_fraction=True)),
        allowed_dimensions: Optional[set[Dimension]] = None,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        debounce_ms: Optional[int] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the real united scalar widget.
        
        Parameters
        ----------
        value : RealUnitedScalar | HookLike[RealUnitedScalar] | ObservableSingleValueLike[RealUnitedScalar]
            The initial united scalar value, or a hook/observable to bind to. Default is NaN with dimensionless dimension.
        display_unit_options : Optional[dict[Dimension, set[Unit]]] | HookLike[...] | ObservableDictLike[...], optional
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
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = RealUnitedScalarController(
            value_or_hook_or_observable=value,
            display_unit_options=display_unit_options,
            value_formatter=value_formatter,
            unit_formatter=unit_formatter,
            unit_options_sorter=unit_options_sorter,
            allowed_dimensions=allowed_dimensions,
            debounce_ms=debounce_ms,
            logger=logger
        )

        payload = Controller_Payload(
            label=controller.widget_real_united_scalar_label,
            line_edit=controller.widget_real_united_scalar_line_edit,
            combobox=controller.widget_display_unit_combobox,
            editable_combobox=controller.widget_unit_editable_combobox,
        )
        
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
    def value_hook(self) -> HookWithOwnerLike[RealUnitedScalar]:
        """
        Hook for the value.
        """
        return self.controller.value_hook
    
    @property
    def unit_options_hook(self) -> HookWithOwnerLike[dict[Dimension, set[Unit]]]:
        """
        Hook for the unit options.
        """
        return self.controller.unit_options_hook
    
    @property
    def unit_hook(self) -> HookWithOwnerLike[Unit]:
        """
        Hook for the unit.
        """
        return self.controller.unit_hook
    
    @property
    def value(self) -> RealUnitedScalar:
        return self.get_value_of_hook("value") # type: ignore

    @property
    def unit_options(self) -> dict[Dimension, set[Unit]]:
        return self.get_value_of_hook("unit_options") # type: ignore

    @value.setter
    def value(self, value: RealUnitedScalar) -> None:
        self.controller.value = value

    def set_value(self, value: RealUnitedScalar) -> None:
        self.controller.value = value