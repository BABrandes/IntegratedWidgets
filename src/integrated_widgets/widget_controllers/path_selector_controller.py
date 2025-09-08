from __future__ import annotations

# Standard library imports
from typing import Optional, Literal, overload, Any, Mapping
from logging import Logger
from pathlib import Path
from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog, QFrame, QVBoxLayout

# BAB imports
from integrated_widgets.widget_controllers.base_controller_with_disable import BaseWidgetControllerWithDisable
from observables import ObservableSingleValueLike, HookLike, InitialSyncMode

# Local imports
from ..guarded_widgets import GuardedLineEdit, GuardedLabel

class PathSelectorController(BaseWidgetControllerWithDisable[Literal["value"], Any], ObservableSingleValueLike[Optional[Path]]):

    @overload
    def __init__(
        self,
        value: Optional[Path],
        *,
        dialog_title: Optional[str] = None,
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: Optional[set[str]] = None,
        mode: Literal["file", "directory"] = "file",
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: ObservableSingleValueLike[Optional[Path]] | HookLike[Optional[Path]] | Optional[Path],
        *,
        dialog_title: Optional[str] = None,
        mode: Literal["file", "directory"] = "file",
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: Optional[set[str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        value,
        *,
        dialog_title: Optional[str] = None,
        mode: Literal["file", "directory"] = "file",
        suggested_file_title_without_extension: Optional[str] = None,
        suggested_file_extension: Optional[str] = None,
        allowed_file_extensions: Optional[set[str]] = None,
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
        
        # Handle different types of value
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: Optional[Path] = value.value  # type: ignore
            value_hook = value
        elif isinstance(value, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: Optional[Path] = value.value
            value_hook = value.value_hook
        elif isinstance(value, (Path, type(None))):
            # It's a direct value
            initial_value = value
            value_hook: Optional[HookLike[Optional[Path]]] = None
        else:
            raise ValueError(f"Invalid value: {value}")
        
        def verification_method(x: Mapping[Literal["value"], Any]) -> tuple[bool, str]:
            # Verify the value is a Path or None
            current_value = x.get("value", initial_value)
            if current_value is not None and not isinstance(current_value, Path):
                return False, f"Value must be a Path or None, got {type(current_value)}"
            return True, "Verification method passed"

        super().__init__(
            {"value": initial_value},
            verification_method=verification_method,
            parent=parent,
            logger=logger,
        )
        
        # Store hook for later binding
        self._value_hook = value_hook
        
        if value_hook is not None:
            self.connect(value_hook, to_key="value", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)

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

    def _disable_widgets(self) -> None:
        self._edit.setEnabled(False)
        self._button.setEnabled(False)
        self._clear.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["value"], Any]) -> None:
        self._edit.setEnabled(True)
        self._button.setEnabled(True)
        self._clear.setEnabled(True)
        self._set_incomplete_primary_component_values(initial_component_values)

    def _on_edited(self) -> None:
        """Handle line edit editing finished."""
        if self.is_blocking_signals:
            return
        
        raw: str = self._edit.text().strip()
        new_path: Optional[Path] = None if raw == "" else Path(raw)
        self._set_incomplete_primary_component_values({"value": new_path})
        
    def _on_clear(self) -> None:
        """Handle clear button click."""
        self._edit.blockSignals(True)
        try:
            self._edit.setText("")
        finally:
            self._edit.blockSignals(False)
        self._set_incomplete_primary_component_values({"value": None})

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

            current_value: Optional[Path] = self.get_value("value")
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
            self._set_incomplete_primary_component_values({"value": path})

    def _invalidate_widgets_impl(self) -> None:
        path = self.component_values_dict["value"]
        text = "" if path is None else str(path)
        self._edit.setText(text)
        self._label.setText(text)

    ###########################################################################
    # Disposal
    ###########################################################################

    def dispose_before_children(self) -> None:
        """Disconnect signals before children are deleted."""
        try:
            self._button.clicked.disconnect()
        except Exception:
            pass
        try:
            self._edit.editingFinished.disconnect()
        except Exception:
            pass
        try:
            self._clear.clicked.disconnect()
        except Exception:
            pass

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def hook_value(self) -> HookLike[Optional[Path]]:
        return self.get_component_hook("value")

    @property
    def value(self) -> Optional[Path]:
        """Get the current path value."""
        return self.get_value("value")

    @value.setter
    def value(self, value: Optional[Path]) -> None:
        """Set the path value."""
        self._set_incomplete_primary_component_values({"value": value})

    @property
    def path(self) -> Optional[Path]:
        """Get the current path value."""
        return self.get_value("value")
    
    @path.setter
    def path(self, new_value: Optional[Path]) -> None:
        """Set the path value."""
        self._set_incomplete_primary_component_values({"value": new_value})

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
