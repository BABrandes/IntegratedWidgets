from __future__ import annotations

# Standard library imports
from typing import Optional, Literal
from logging import Logger
from pathlib import Path
from PySide6.QtWidgets import QPushButton, QFileDialog, QMessageBox

# BAB imports
from observables import ObservableSingleValueProtocol, Hook

# Local imports
from ..util.base_single_hook_controller import BaseSingleHookController
from ..util.resources import log_msg

# Local imports
from ..controlled_widgets.controlled_line_edit import ControlledLineEdit
from ..controlled_widgets.controlled_qlabel import ControlledQLabel

class PathSelectorController(BaseSingleHookController[Optional[Path], "PathSelectorController"]):
    """
    A controller for selecting file or directory paths using a file dialog.
    
    This controller provides widgets for selecting and displaying file system paths. It
    includes a line edit for manual entry, a browse button to open a file/directory dialog,
    a clear button, and a label for display. The controller supports file extension filtering
    and can synchronize with observable values.
    
    Parameters
    ----------
    value_or_hook_or_observable : Optional[Path] | Hook[Optional[Path]] | ObservableSingleValueProtocol[Optional[Path]]
        The initial path or an observable/hook to sync with. Can be:
        - A Path object or None
        - A Hook object for bidirectional synchronization
        - An ObservableSingleValueProtocol for synchronization with reactive data
    dialog_title : Optional[str], optional
        Title for the file/directory selection dialog. If None, uses "Select File" or
        "Select Directory" based on mode. Defaults to None.
    mode : Literal["file", "directory"], optional
        Selection mode: "file" for file selection, "directory" for directory selection.
        Defaults to "file".
    suggested_file_title_without_extension : Optional[str], optional
        Suggested filename (without extension) when saving. Only used in file mode.
        Defaults to None.
    suggested_file_extension : Optional[str], optional
        Default file extension (e.g., "txt", ".json"). Defaults to None.
    allowed_file_extensions : None|str|set[str], optional
        Allowed file extensions for filtering. Can be a single extension string or a set.
        Only used in file mode. Defaults to None (all files allowed).
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : Optional[Path]
        Property to get/set the current path (inherited from base class).
    widget_label : ControlledLabel
        Label displaying the current path.
    widget_line_edit : ControlledLineEdit
        Line edit for manual path entry.
    widget_browse_button : QPushButton
        Button that opens the file/directory selection dialog.
    widget_clear_button : QPushButton
        Button that clears the current path.
    
    Examples
    --------
    Basic file selection:
    
    >>> controller = PathSelectorController(None, mode="file")
    >>> # User clicks browse button to select a file
    >>> print(controller.value)  # Path('/path/to/selected/file.txt')
    
    Directory selection:
    
    >>> controller = PathSelectorController(
    ...     value=Path.home(),
    ...     mode="directory"
    ... )
    
    With file extension filtering:
    
    >>> controller = PathSelectorController(
    ...     value=None,
    ...     mode="file",
    ...     allowed_file_extensions={"json", "txt"},
    ...     suggested_file_extension="json"
    ... )
    >>> # Only .json and .txt files will be shown in dialog
    
    With observables:
    
    >>> from observables import ObservableSingleValue
    >>> from pathlib import Path
    >>> observable = ObservableSingleValue(Path("/tmp/data.csv"))
    >>> controller = PathSelectorController(observable, mode="file")
    
    Accessing widgets:
    
    >>> layout.addWidget(controller.widget_line_edit)
    >>> layout.addWidget(controller.widget_browse_button)
    >>> layout.addWidget(controller.widget_clear_button)
    
    Notes
    -----
    - The path can be None (no selection)
    - Manual text entry in the line edit is supported
    - Leading/trailing whitespace is automatically stripped
    - Empty text is converted to None
    """

    def __init__(
        self,
        value_or_hook_or_observable: Optional[Path] | Hook[Optional[Path]] | ObservableSingleValueProtocol[Optional[Path]],
        *,
        dialog_title: Optional[str] = None,
        mode: Literal["file", "directory"] = "file",
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: None|str|set[str] = None,
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        
        log_msg(self, "__init__", logger, f"Initializing PathSelectorController with mode={mode}")
        
        if dialog_title is None:
            if mode == "file":
                dialog_title = "Select File"
            else:
                dialog_title = "Select Directory"
        self._dialog_title = dialog_title
        self._mode = mode
        self._suggested_file_title_without_extension = suggested_file_title_without_extension
        self._suggested_file_extension = suggested_file_extension
        self._allowed_file_extensions = allowed_file_extensions
        
        log_msg(self, "__init__", logger, f"Dialog title: {dialog_title}, allowed extensions: {allowed_file_extensions}")
        
        def verification_method(x: Optional[Path]) -> tuple[bool, str]:
            # Verify the value is a Path or None
            if x is not None and not isinstance(x, Path): # type: ignore
                return False, f"Value must be a Path or None, got {type(x)}"
            return True, "Verification method passed"

        BaseSingleHookController.__init__( # type: ignore
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=verification_method,
            logger=logger,
            debounce_ms=debounce_ms
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        log_msg(self, "_initialize_widgets", self._logger, "Creating widgets for PathSelectorController")
        
        self._label = ControlledQLabel(self)
        self._edit = ControlledLineEdit(self)
        self._button = QPushButton("Select path")
        self._clear = QPushButton("Clear path")

        self._button.clicked.connect(self._on_browse)
        self._edit.editingFinished.connect(self._on_edited)
        self._clear.clicked.connect(self._on_clear)
        
        log_msg(self, "_initialize_widgets", self._logger, "Widgets created and signals connected")

    def _on_edited(self) -> None:
        """Handle line edit editing finished."""
        if self.is_blocking_signals:
            log_msg(self, "_on_edited", self._logger, "Ignoring edit - signals are blocked")
            return
        
        raw: str = self._edit.text().strip()
        new_path: Optional[Path] = None if raw == "" else Path(raw)
        log_msg(self, "_on_edited", self._logger, f"Line edit finished - raw text: '{raw}', parsed path: {new_path}")
        self.submit(new_path)
        
    def _on_clear(self) -> None:
        """Handle clear button click."""
        log_msg(self, "_on_clear", self._logger, "Clear button clicked - clearing path")
        self._edit.blockSignals(True)
        try:
            self._edit.setText("")
        finally:
            self._edit.blockSignals(False)
        self.submit(None)
        log_msg(self, "_on_clear", self._logger, "Path cleared successfully")

    def _on_browse(self) -> None:
        """Handle browse button click."""
        log_msg(self, "_on_browse", self._logger, f"Browse button clicked - mode: {self._mode}")
        
        if self._mode == "directory":
            log_msg(self, "_on_browse", self._logger, "Opening directory selection dialog")
            sel = QFileDialog.getExistingDirectory(None, self._dialog_title)
            path = Path(sel) if sel else None
            log_msg(self, "_on_browse", self._logger, f"Directory dialog result: {path}")
        else:
            log_msg(self, "_on_browse", self._logger, "Opening file selection dialog")
            dialog = QFileDialog(None, self._dialog_title)
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

            name_filters: list[str] = []
            patterns: list[str] = []

            if isinstance(self._allowed_file_extensions, str):
                self._allowed_file_extensions = {self._allowed_file_extensions}
            if self._allowed_file_extensions is not None and len(self._allowed_file_extensions) > 0:
                normalized_exts = sorted({ext.lower().lstrip('.') for ext in self._allowed_file_extensions})
                patterns = [f"*.{ext}" for ext in normalized_exts]
                name_filters.append(f"Allowed Files ({' '.join(patterns)})")
                log_msg(self, "_on_browse", self._logger, f"Configured file filters: {patterns}")

            if self._suggested_file_extension:
                default_ext = self._suggested_file_extension.lstrip('.')
                dialog.setDefaultSuffix(default_ext)
                if not patterns:
                    name_filters.append(f"*.{default_ext}")
                log_msg(self, "_on_browse", self._logger, f"Set default extension: {default_ext}")

            name_filters.append("All Files (*)")
            dialog.setNameFilters(name_filters)
            log_msg(self, "_on_browse", self._logger, f"Total name filters: {name_filters}")

            current_value: Optional[Path] = self.value
            if current_value is not None:
                log_msg(self, "_on_browse", self._logger, f"Setting dialog to current path: {current_value}")
                dialog.setDirectory(str(current_value.parent))
                dialog.selectFile(str(current_value))
            else:
                start_dir = str(Path.home())
                dialog.setDirectory(start_dir)
                if self._suggested_file_title_without_extension and self._suggested_file_extension:
                    suggested = f"{self._suggested_file_title_without_extension}.{self._suggested_file_extension.lstrip('.')}"
                    dialog.selectFile(str(Path(start_dir) / suggested))
                    log_msg(self, "_on_browse", self._logger, f"Using suggested filename: {suggested}")
                else:
                    log_msg(self, "_on_browse", self._logger, f"Starting in home directory: {start_dir}")

            selected_path: Optional[Path] = None
            if dialog.exec():
                files = dialog.selectedFiles()
                if files:
                    selected_path = Path(files[0])
                log_msg(self, "_on_browse", self._logger, f"File dialog accepted - selected: {selected_path}")
            else:
                log_msg(self, "_on_browse", self._logger, "File dialog cancelled by user")

            path = selected_path

        if path is not None:
            log_msg(self, "_on_browse", self._logger, f"Processing selected path: {path}")
            self._edit.blockSignals(True)
            try:
                self._edit.setText(str(path))
            finally:
                self._edit.blockSignals(False)

            success, message = self.validate_value("value", path)
            log_msg(self, "_on_browse_validate", self._logger, f"Path validation: {success}, message: {message}")
            if not success:
                log_msg(self, "_on_browse", self._logger, f"Path validation failed: {message}")
                QMessageBox.warning(None, "Invalid Path", "The path is not valid!")
                self.invalidate_widgets()
                return

            log_msg(self, "_on_browse", self._logger, f"Submitting validated path: {path}")
            self.submit(path)
        else:
            log_msg(self, "_on_browse", self._logger, "No path selected or dialog cancelled")

    def _invalidate_widgets_impl(self) -> None:
        path = self.value
        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Updating widgets with path: {path}")
        
        edit_text = "" if path is None else str(path)
        self._edit.setText(edit_text)
        
        if path is None:
            label_text = f"No {self._mode} selected"
        else:
            label_text = str(path)
        self._label.setText(label_text)
        
        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Widgets updated - label: '{label_text}'")

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def path_hook(self) -> Hook[Optional[Path]]:
        hook = self.get_hook("value") # type: ignore
        return hook

    @property
    def path(self) -> Optional[Path]:
        """Get the current path value."""
        return self.value

    @path.setter
    def path(self, path: Optional[Path]) -> None:
        log_msg(self, "path.setter", self._logger, f"Setting path to: {path}")
        self.submit(path)

    def change_path(self, path: Optional[Path], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        log_msg(self, "change_path", self._logger, f"Changing path to: {path}")
        self.submit(path, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)

    @property
    def widget_line_edit(self) -> ControlledLineEdit:
        return self._edit

    @property
    def widget_button(self) -> QPushButton:
        return self._button

    @property
    def widget_label(self) -> ControlledQLabel:
        return self._label

    @property
    def widget_clear_button(self) -> QPushButton:
        return self._clear