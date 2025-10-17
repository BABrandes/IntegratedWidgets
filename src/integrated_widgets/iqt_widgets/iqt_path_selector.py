from typing import Optional, Literal
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton
from logging import Logger
from integrated_widgets.controlled_widgets.controlled_qlabel import ControlledQLabel
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from integrated_widgets.widget_controllers.path_selector_controller import PathSelectorController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from .core.layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a path selector widget."""
    label: ControlledQLabel
    line_edit: QLineEdit
    button: QPushButton
    clear_button: QPushButton


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
    A file/directory path selector widget with browse dialog.
    
    This widget provides a line edit for entering paths manually, along with
    browse and clear buttons. The browse button opens a native file/directory
    dialog. Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "value": Optional[Path] - The selected file or directory path (can be None)
    
    Properties:
        value: Optional[Path] - Get or set the path (read/write, can be None)
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
        """
        Initialize the path selector widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : Optional[Path] | HookLike[Optional[Path]] | ObservableSingleValueLike[Optional[Path]]
            The initial path (can be None), or a hook/observable to bind to.
        dialog_title : str, optional
            Title for the file/directory dialog. Default is None (uses system default).
        mode : Literal["file", "directory"], optional
            Whether to select files or directories. Default is "file".
        suggested_file_title_without_extension : str, optional
            Suggested filename (without extension) when saving. Default is None.
        suggested_file_extension : str, optional
            Suggested file extension when saving. Default is None.
        allowed_file_extensions : None | str | set[str], optional
            File extensions to filter in dialog (e.g., "txt" or {"txt", "md"}). Default is None (all files).
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

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
            label=controller.widget_label,
            line_edit=controller.widget_line_edit,
            button=controller.widget_button,
            clear_button=controller.widget_clear_button
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
    def path_hook(self):
        """Hook for the path value."""
        return self.controller.value_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def path(self) -> Optional[Path]:
        return self.get_value_of_hook("value")

    @path.setter
    def path(self, path: Optional[Path]) -> None:
        self.controller.value = path

    def change_path(self, path: Optional[Path]) -> None:
        self.controller.value = path