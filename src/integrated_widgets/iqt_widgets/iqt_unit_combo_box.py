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
    Available hooks:
        - "selected_unit": Optional[Unit]
        - "available_units": dict[Dimension, set[Unit]]
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

    @property
    def selected_unit(self) -> Optional[Unit]:
        return self.get_value_of_hook("selected_unit") # type: ignore

    @property
    def available_units(self) -> dict[Dimension, set[Unit]]:
        return self.get_value_of_hook("available_units") # type: ignore