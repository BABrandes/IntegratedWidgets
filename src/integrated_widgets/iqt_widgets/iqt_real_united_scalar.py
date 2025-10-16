from typing import Optional, Union, Callable, Literal, Any
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout, QHBoxLayout, QLabel
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableDictLike
from united_system import RealUnitedScalar, Unit, Dimension

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.real_united_scalar_controller import RealUnitedScalarController
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE


class DefaultLayoutStrategy(LayoutStrategyForControllers[RealUnitedScalarController]):
    def __call__(self, parent: QWidget, controller: RealUnitedScalarController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        
        # Display section
        display_layout = QHBoxLayout()
        display_layout.addWidget(QLabel("Value:"))
        display_layout.addWidget(controller.widget_real_united_scalar_label)
        layout.addLayout(display_layout)
        
        # Edit section
        edit_layout = QHBoxLayout()
        edit_layout.addWidget(controller.widget_real_united_scalar_line_edit)
        edit_layout.addWidget(controller.widget_display_unit_combobox)
        layout.addLayout(edit_layout)
        
        return layout


class IQtRealUnitedScalar(IQtBaseWidget[Literal["value", "unit_options"], Any, RealUnitedScalarController]):
    """
    Available hooks:
        - "value": RealUnitedScalar
        - "unit_options": dict[Dimension, set[Unit]]
    """

    def __init__(
        self,
        value: Optional[RealUnitedScalar | HookLike[RealUnitedScalar] | ObservableSingleValueLike[RealUnitedScalar]] = None,
        display_unit_options: Optional[dict[Dimension, set[Unit]]] | HookLike[dict[Dimension, set[Unit]]] | ObservableDictLike[Dimension, set[Unit]] = None,
        *,
        value_formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        unit_formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        unit_options_sorter: Callable[[set[Unit]], list[Unit]] = lambda u: sorted(u, key=lambda x: x.format_string(as_fraction=True)),
        allowed_dimensions: Optional[set[Dimension]] = None,
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = RealUnitedScalarController(
            value=value,
            display_unit_options=display_unit_options,
            value_formatter=value_formatter,
            unit_formatter=unit_formatter,
            unit_options_sorter=unit_options_sorter,
            allowed_dimensions=allowed_dimensions,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
