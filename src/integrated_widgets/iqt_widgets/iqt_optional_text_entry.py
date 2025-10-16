from typing import Optional, Union, Callable, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike

from .iqt_base import IQtBaseWidget, LayoutStrategy
from integrated_widgets.widget_controllers.optional_text_entry_controller import OptionalTextEntryController


class DefaultLayoutStrategy(LayoutStrategy[OptionalTextEntryController]):
    def __call__(self, parent: QWidget, controller: OptionalTextEntryController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_line_edit)
        return layout


class IQtOptionalTextEntry(IQtBaseWidget[Literal["value", "enabled"], Optional[str], OptionalTextEntryController]):
    """
    Available hooks:
        - "value": Optional[str]
        - "enabled": bool
    """

    def __init__(
        self,
        value_or_hook_or_observable: Optional[str] | HookLike[Optional[str]] | ObservableSingleValueLike[Optional[str]],
        *,
        validator: Optional[Callable[[Optional[str]], bool]] = None,
        none_value: str = "",
        strip_whitespace: bool = True,
        layout_strategy: Optional[LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = OptionalTextEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
            none_value=none_value,
            strip_whitespace=strip_whitespace,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
