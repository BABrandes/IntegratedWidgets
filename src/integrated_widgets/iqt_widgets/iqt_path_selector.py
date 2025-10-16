from typing import Optional, Literal
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.path_selector_controller import PathSelectorController
from .layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a path selector widget."""
    line_edit: QWidget
    button: QWidget
    clear_button: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for path selector widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(payload.line_edit)
        layout.addWidget(payload.button)
        layout.addWidget(payload.clear_button)
        return widget


class IQtPathSelector(IQtControlledLayoutedWidget[Literal["value"], Optional[Path], Controller_Payload, PathSelectorController]):
    """
    Available hooks:
        - "value": Optional[Path]
    """

    def __init__(
        self,
        value_or_hook_or_observable: Optional[Path] | HookLike[Optional[Path]] | ObservableSingleValueLike[Optional[Path]],
        *,
        dialog_title: Optional[str] = None,
        mode: Literal["file", "directory"] = "file",
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: None | str | set[str] = None,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = PathSelectorController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            dialog_title=dialog_title,
            mode=mode,
            suggested_file_title_without_extension=suggested_file_title_without_extension,
            suggested_file_extension=suggested_file_extension,
            allowed_file_extensions=allowed_file_extensions,
            logger=logger
        )

        payload = Controller_Payload(
            line_edit=controller.widget_line_edit,
            button=controller.widget_button,
            clear_button=controller.widget_clear_button
        )
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)

    @property
    def value(self) -> Optional[Path]:
        return self.get_value_of_hook("value")
