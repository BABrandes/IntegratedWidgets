from typing import Optional, Union, Callable, Literal, Any
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableDictLike, ObservableSetLike
from united_system import Unit, Dimension

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.unit_combo_box_controller import UnitComboBoxController


class DefaultLayoutStrategy(LayoutStrategyForControllers[UnitComboBoxController]):
    def __call__(self, parent: QWidget, controller: UnitComboBoxController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_combobox)
        return layout


class IQtUnitComboBox(IQtBaseWidget[Literal["selected_unit", "available_units"], Any, UnitComboBoxController]):
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
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
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

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
