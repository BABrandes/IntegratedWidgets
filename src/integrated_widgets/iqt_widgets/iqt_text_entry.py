from typing import Optional, Union, Callable, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike

from .iqt_base import IQtBaseWidget, LayoutStrategy
from integrated_widgets.widget_controllers.text_entry_controller import TextEntryController


class DefaultLayoutStrategy(LayoutStrategy[TextEntryController]):
    def __call__(self, parent: QWidget, controller: TextEntryController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_line_edit)
        return layout


class IQtTextEntry(IQtBaseWidget[Literal["value", "enabled"], str, TextEntryController]):
    """
    Available hooks:
        - "value": str
        - "enabled": bool
    """

    def __init__(
        self,
        value_or_hook_or_observable: str | HookLike[str] | ObservableSingleValueLike[str],
        *,
        validator: Optional[Callable[[str], bool]] = None,
        strip_whitespace: bool = True,
        layout_strategy: Optional[LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = TextEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
            strip_whitespace=strip_whitespace,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
