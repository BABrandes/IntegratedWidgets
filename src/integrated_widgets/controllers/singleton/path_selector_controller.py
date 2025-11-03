from __future__ import annotations

# Standard library imports
from typing import Optional, Literal, Callable
from logging import Logger
from pathlib import Path
from PySide6.QtWidgets import QPushButton, QFileDialog, QMessageBox

# BAB imports
from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

# Local imports
from ..core.base_singleton_controller import BaseSingletonController
from ...controlled_widgets.controlled_line_edit import ControlledLineEdit
from ...controlled_widgets.controlled_qlabel import ControlledQLabel
from ...controlled_widgets.controlled_push_button import ControlledPushButton
from ...auxiliaries.resources import log_msg

class PathSelectorController(BaseSingletonController[Optional[Path]]):
    """
    A controller for selecting file or directory paths using a file dialog.
    
    This controller provides widgets for selecting and displaying file system paths. It
    includes a line edit for manual entry, a browse button to open a file/directory dialog,
    a clear button, and a label for display. The controller supports file extension filtering
    and can synchronize with observable values.
    
    Parameters
    ----------
    value_or_hook_or_observable : Optional[Path] | Hook[Optional[Path]] | XSingleValueProtocol[Optional[Path]]
        The initial path or an observable/hook to sync with. Can be:
        - A Path object or None
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for synchronization with reactive data
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
    
    >>> from nexpy import XValue
    >>> from pathlib import Path
    >>> observable = XValue(Path("/tmp/data.csv"))
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
        value: Optional[Path] | Hook[Optional[Path]] | XSingleValueProtocol[Optional[Path]],
        *,
        dialog_title: Optional[str] = None,
        mode: Literal["file", "directory"] = "file",
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: None|str|set[str] = None,
        debounce_ms: int|Callable[[], int],
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
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

        BaseSingletonController.__init__( # type: ignore
            self,
            value=value,
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            logger=logger,
            nexus_manager=nexus_manager
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        log_msg(self, "_initialize_widgets", self._logger, "Creating widgets for PathSelectorController")
        
        self._path_label = ControlledQLabel(self)
        self._path_entry = ControlledLineEdit(self)
        self._browse_button = ControlledPushButton(self, "Select path")
        self._clear_button = ControlledPushButton(self, "Clear path")

        self._browse_button.userInputFinishedSignal.connect(self._on_browse)
        self._path_entry.userInputFinishedSignal.connect(self.evaluate)
        self._clear_button.userInputFinishedSignal.connect(self._on_clear)
        
        log_msg(self, "_initialize_widgets", self._logger, "Widgets created and signals connected")

    def _read_widget_single_value_impl(self) -> tuple[bool, Optional[Path]]:
        """
        Read the value from the path entry widget.
        
        This method reads the current text from the path entry widget, parses it as a Path,
        and returns it as a boolean and the value.
        
        Returns:
            A tuple containing a boolean indicating if the value is valid and the value.
            If the value is invalid, the boolean will be False and the value will be the last valid value.
        """
        raw: str = self._path_entry.text().strip()
        try:
            new_path: Optional[Path] = None if raw == "" else Path(raw)
        except ValueError:
            return False, self.value
        
        return True, new_path
        
    def _on_clear(self) -> None:
        """Handle clear button click."""
        log_msg(self, "_on_clear", self._logger, "Clear button clicked - clearing path")
        self._path_entry.blockSignals(True)
        try:
            self._path_entry.setText("")
        finally:
            self._path_entry.blockSignals(False)
        self.submit(None)
        # Reflect cleared state immediately in label
        self._path_label.setText(f"No {self._mode} selected")
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
            self._path_entry.blockSignals(True)
            try:
                self._path_entry.setText(str(path))
            finally:
                self._path_entry.blockSignals(False)

            # Update label immediately to match selection
            self._path_label.setText(str(path))

            log_msg(self, "_on_browse", self._logger, f"Submitting validated path: {path}")
            success, _ = self._validate_value("value", path)
            if success:
                self.submit(path)
            else:
                # Show a warning message to the user
                QMessageBox.warning(None, "Invalid Path", "The path is not valid!")
                self.invalidate_widgets()
                return
                
        else:
            log_msg(self, "_on_browse", self._logger, "No path selected or dialog cancelled")

    def _invalidate_widgets_impl(self) -> None:
        path = self.value
        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Updating widgets with path: {path}")
        
        edit_text = "" if path is None else str(path)
        self._path_entry.setText(edit_text)
        
        if path is None:
            label_text = f"No {self._mode} selected"
        else:
            label_text = str(path)
        self._path_label.setText(label_text)
        
        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Widgets updated - label: '{label_text}'")

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_path_entry(self) -> ControlledLineEdit:
        return self._path_entry

    @property
    def widget_browse_button(self) -> QPushButton:
        return self._browse_button

    @property
    def widget_path_label(self) -> ControlledQLabel:
        return self._path_label

    @property
    def widget_clear_button(self) -> QPushButton:
        return self._clear_button