from __future__ import annotations

from typing import Optional, Literal, overload
from pathlib import Path

from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike, ObservableSingleValue
from integrated_widgets.guarded_widgets import GuardedLineEdit, GuardedLabel


Model = ObservableSingleValueLike[Optional[Path]] | ObservableSingleValue[Optional[Path]]


class PathSelectorController(ObservableController[Model]):

    @overload
    def __init__(
        self,
        observable: Model,
        *,
        dialog_title: str = "Select Path",
        mode: Literal["file", "directory"] = "file",
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: Optional[Path],
        *,
        dialog_title: str = "Select Path",
        mode: Literal["file", "directory"] = "file",
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        observable_or_value,
        *,
        dialog_title: str = "Select Path",
        mode: Literal["file", "directory"] = "file",
        parent: Optional[QWidget] = None,
    ) -> None:
        
        if isinstance(observable_or_value, (ObservableSingleValueLike, ObservableSingleValue)):
            observable = observable_or_value
        elif isinstance(observable_or_value, Optional[Path]):
            observable = ObservableSingleValue(observable_or_value)
        else:
            raise TypeError(f"Invalid type for observable_or_value: {type(observable_or_value)}")
        self._dialog_title = dialog_title
        self._mode = mode
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._label = GuardedLabel(self.owner_widget)
        # GuardedLabel only allows updates within controller-managed context
        with self._internal_update():
            self._label.setText("")
        self._edit = GuardedLineEdit(self.owner_widget)
        self._button = QPushButton("…", self.owner_widget)
        self._clear = QPushButton("✕", self.owner_widget)
        self._button.clicked.connect(self._browse)
        self._edit.editingFinished.connect(self._on_edited)
        self._clear.clicked.connect(self._on_clear)

    def update_widgets_from_observable(self) -> None:
        with self._internal_update():
            p = self._observable.value
            text = "" if p is None else str(p)
            self._edit.setText(text)
            self._label.setText(text)

    def update_observable_from_widgets(self) -> None:
        raw = self._edit.text().strip()
        self._observable.set_value(None if raw == "" else Path(raw))

    def _on_edited(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    def _browse(self) -> None:
        if self._mode == "directory":
            sel = QFileDialog.getExistingDirectory(self.owner_widget, self._dialog_title)
            path = Path(sel) if sel else None
        else:
            sel, _ = QFileDialog.getOpenFileName(self.owner_widget, self._dialog_title)
            path = Path(sel) if sel else None
        if path is not None:
            with self._internal_update():
                self._edit.setText(str(path))
            self.update_observable_from_widgets()

    def dispose_before_children(self) -> None:
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

    @property
    def line_edit(self) -> GuardedLineEdit:
        return self._edit

    @property
    def button(self) -> QPushButton:
        return self._button

    @property
    def label(self) -> GuardedLabel:
        return self._label

    # Descriptive accessors
    @property
    def path_line_edit(self) -> GuardedLineEdit:
        return self._edit

    @property
    def browse_button(self) -> QPushButton:
        return self._button

    @property
    def path_label(self) -> GuardedLabel:
        return self._label

    @property
    def clear_button(self) -> QPushButton:
        return self._clear

    def _on_clear(self) -> None:
        with self._internal_update():
            self._edit.setText("")
        self.update_observable_from_widgets()


