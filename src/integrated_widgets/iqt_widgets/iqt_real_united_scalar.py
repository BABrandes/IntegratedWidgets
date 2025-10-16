from typing import Optional, Callable, Literal, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableDictLike
from united_system import RealUnitedScalar, Unit, Dimension
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.real_united_scalar_controller import RealUnitedScalarController
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE
from .layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for real united scalar widget."""
    label: QWidget
    line_edit: QWidget
    combobox: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for real united scalar widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(payload.label)
        layout.addWidget(payload.line_edit)
        layout.addWidget(payload.combobox)
        return widget


class IQtRealUnitedScalar(IQtControlledLayoutedWidget[Literal["value", "unit_options"], Any, Controller_Payload, RealUnitedScalarController]):
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
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
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

        payload = Controller_Payload(
            label=controller.widget_real_united_scalar_label,
            line_edit=controller.widget_real_united_scalar_line_edit,
            combobox=controller.widget_display_unit_combobox
        )
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)

    @property
    def value(self) -> RealUnitedScalar:
        return self.get_value_of_hook("value") # type: ignore

    @property
    def unit_options(self) -> dict[Dimension, set[Unit]]:
        return self.get_value_of_hook("unit_options") # type: ignore