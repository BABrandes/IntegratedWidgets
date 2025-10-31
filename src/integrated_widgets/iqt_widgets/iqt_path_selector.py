from typing import Optional, Literal, Any, Callable
from pathlib import Path
from logging import Logger
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from ..controlled_widgets.controlled_qlabel import ControlledQLabel
from ..controlled_widgets.controlled_line_edit import ControlledLineEdit
from ..controllers.singleton.path_selector_controller import PathSelectorController
from ..auxiliaries.default import default_debounce_ms
from .foundation.iqt_singleton_controller_widget_base import IQtSingletonControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a path selector widget."""
    mode: Literal["file", "directory"]
    path_label: ControlledQLabel
    path_entry: ControlledLineEdit
    browse_button: QPushButton
    clear_button: QPushButton


def layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.path_label)
    layout.addWidget(payload.path_entry)
    layout.addWidget(payload.browse_button)
    layout.addWidget(payload.clear_button)
    return widget

class IQtPathSelector(IQtSingletonControllerWidgetBase[Optional[Path], Controller_Payload, PathSelectorController]):
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
        value: Optional[Path] | Hook[Optional[Path]] | XSingleValueProtocol[Optional[Path]],
        *,
        dialog_title: Optional[str] = None,
        mode: Literal["file", "directory"] = "file",
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: None | str | set[str] = None,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = layout_strategy,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the path selector widget.
        
        Parameters
        ----------
        value : Optional[Path] | Hook[Optional[Path]] | XSingleValueProtocol[Optional[Path]]
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
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. Default is default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = PathSelectorController(
            value=value,
            dialog_title=dialog_title,
            mode=mode,
            suggested_file_title_without_extension=suggested_file_title_without_extension,
            suggested_file_extension=suggested_file_extension,
            allowed_file_extensions=allowed_file_extensions,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(
            mode=mode,
            path_label=controller.widget_path_label,
            path_entry=controller.widget_path_entry,
            browse_button=controller.widget_browse_button,
            clear_button=controller.widget_clear_button
        )
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    def __str__(self) -> str:
        path = self.value
        if path is None:
            return f"{self.__class__.__name__}(path=None)"
        path_str = str(path)
        if len(path_str) > 25:
            path_str = "..." + path_str[-22:]
        return f"{self.__class__.__name__}(path={path_str!r})"

    def __repr__(self) -> str:
        path = self.value
        if path is None:
            return f"{self.__class__.__name__}(path=None, id={hex(id(self))})"
        path_str = str(path)
        if len(path_str) > 25:
            path_str = "..." + path_str[-22:]
        return f"{self.__class__.__name__}(path={path_str!r}, id={hex(id(self))})"

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def path_hook(self) -> Hook[Optional[Path]]:
        """Hook for the path value."""
        hook: Hook[Optional[Path]] = self.hook
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def path(self) -> Optional[Path]:
        return self.value

    @path.setter
    def path(self, path: Optional[Path]) -> None:
        self.controller.value = path

    def change_path(self, path: Optional[Path]) -> None:
        self.controller.value = path