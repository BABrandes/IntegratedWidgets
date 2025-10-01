from __future__ import annotations

# Standard library imports
from typing import Optional, Literal, overload
from logging import Logger
from pathlib import Path
from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog, QFrame, QVBoxLayout, QMessageBox

# BAB imports
from observables import ObservableSingleValueLike, HookLike

# Local imports
from ..util.base_single_hook_controller import BaseSingleHookController

# Local imports
from ..guarded_widgets import GuardedLineEdit, GuardedLabel

class PathSelectorController(BaseSingleHookController[Optional[Path]]):

    def __init__(
        self,
        value_or_hook_or_observable: Optional[Path] | HookLike[Optional[Path]] | ObservableSingleValueLike[Optional[Path]],
        *,
        dialog_title: Optional[str] = None,
        mode: Literal["file", "directory"] = "file",
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: None|str|set[str] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        
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
        
        def verification_method(x: Optional[Path]) -> tuple[bool, str]:
            # Verify the value is a Path or None
            if x is not None and not isinstance(x, Path):
                return False, f"Value must be a Path or None, got {type(x)}"
            return True, "Verification method passed"

        BaseSingleHookController.__init__(
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=verification_method,
            parent=parent,
            logger=logger
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:

        self._label = GuardedLabel(self)
        self._edit = GuardedLineEdit(self)
        self._button = QPushButton("…", self._owner_widget)
        self._clear = QPushButton("✕", self._owner_widget)

        self._button.clicked.connect(self._on_browse)
        self._edit.editingFinished.connect(self._on_edited)
        self._clear.clicked.connect(self._on_clear)

    def _on_edited(self) -> None:
        """Handle line edit editing finished."""
        if self.is_blocking_signals:
            return
        
        raw: str = self._edit.text().strip()
        new_path: Optional[Path] = None if raw == "" else Path(raw)
        self._submit_values_on_widget_changed(new_path)
        
    def _on_clear(self) -> None:
        """Handle clear button click."""
        self._edit.blockSignals(True)
        try:
            self._edit.setText("")
        finally:
            self._edit.blockSignals(False)
        self._submit_values_on_widget_changed(None)

    def _on_browse(self) -> None:
        """Handle browse button click."""
        if self._mode == "directory":
            sel = QFileDialog.getExistingDirectory(self._owner_widget, self._dialog_title)
            path = Path(sel) if sel else None
        else:
            dialog = QFileDialog(self._owner_widget, self._dialog_title)
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

            if self._suggested_file_extension:
                default_ext = self._suggested_file_extension.lstrip('.')
                dialog.setDefaultSuffix(default_ext)
                if not patterns:
                    name_filters.append(f"*.{default_ext}")

            name_filters.append("All Files (*)")
            dialog.setNameFilters(name_filters)

            current_value: Optional[Path] = self.value
            if current_value is not None:
                dialog.setDirectory(str(current_value.parent))
                dialog.selectFile(str(current_value))
            else:
                start_dir = str(Path.home())
                dialog.setDirectory(start_dir)
                if self._suggested_file_title_without_extension and self._suggested_file_extension:
                    suggested = f"{self._suggested_file_title_without_extension}.{self._suggested_file_extension.lstrip('.')}"
                    dialog.selectFile(str(Path(start_dir) / suggested))

            selected_path: Optional[Path] = None
            if dialog.exec():
                files = dialog.selectedFiles()
                if files:
                    selected_path = Path(files[0])

            path = selected_path

        if path is not None:
            self._edit.blockSignals(True)
            try:
                self._edit.setText(str(path))
            finally:
                self._edit.blockSignals(False)

            success, _ = self.validate_value("value", path)
            if not success:
                QMessageBox.warning(self._owner_widget, "Invalid Path", "The path is not valid!")
                self.invalidate_widgets()
                return

            self._submit_values_on_widget_changed(path)

    def _invalidate_widgets_impl(self) -> None:
        path = self.value
        text = "" if path is None else str(path)
        self._edit.setText(text)
        self._label.setText(text)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def path_hook(self) -> HookLike[Optional[Path]]:
        return self.value_hook

    @property
    def path(self) -> Optional[Path]:
        """Get the current path value."""
        return self.value

    @property
    def widget_line_edit(self) -> GuardedLineEdit:
        return self._edit

    @property
    def widget_button(self) -> QPushButton:
        return self._button

    @property
    def widget_label(self) -> GuardedLabel:
        return self._label

    @property
    def widget_clear_button(self) -> QPushButton:
        return self._clear

    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(self._label)
        layout.addWidget(self._edit)
        layout.addWidget(self._button)
        layout.addWidget(self._clear)
        return frame
