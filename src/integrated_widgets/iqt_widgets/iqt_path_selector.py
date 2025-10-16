from typing import Optional, Union, Literal
from pathlib import Path
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout, QHBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike

from .iqt_base import IQtBaseWidget, LayoutStrategy
from integrated_widgets.widget_controllers.path_selector_controller import PathSelectorController


class DefaultLayoutStrategy(LayoutStrategy[PathSelectorController]):
    def __call__(self, parent: QWidget, controller: PathSelectorController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        
        # Line edit for path entry
        layout.addWidget(controller.widget_line_edit)
        
        # Buttons on same row
        button_layout = QHBoxLayout()
        button_layout.addWidget(controller.widget_button)
        button_layout.addWidget(controller.widget_clear_button)
        layout.addLayout(button_layout)
        
        return layout


class IQtPathSelector(IQtBaseWidget[Literal["value"], Optional[Path], PathSelectorController]):
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
        layout_strategy: Optional[LayoutStrategy] = None,
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

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
