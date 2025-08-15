from __future__ import annotations

from typing import Optional, Literal, overload, Any, Mapping
from pathlib import Path

from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSingleValueLike, Hook, SyncMode, HookLike, CarriesDistinctSingleValueHook
from integrated_widgets.guarded_widgets import GuardedLineEdit, GuardedLabel


class PathSelectorController(BaseObservableController, ObservableSingleValueLike[Optional[Path]]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"value"}

    @overload
    def __init__(
        self,
        value: Optional[Path],
        *,
        dialog_title: str = "Select Path",
        mode: Literal["file", "directory"] = "file",
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: ObservableSingleValueLike[Optional[Path]] | HookLike[Optional[Path]] | CarriesDistinctSingleValueHook[Optional[Path]],
        *,
        dialog_title: str = "Select Path",
        mode: Literal["file", "directory"] = "file",
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        value,
        *,
        dialog_title: str = "Select Path",
        mode: Literal["file", "directory"] = "file",
        parent: Optional[QWidget] = None,
    ) -> None:
        
        self._dialog_title = dialog_title
        self._mode = mode
        
        # Handle different types of value
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: Optional[Path] = value.value  # type: ignore
            value_hook: Optional[HookLike[Optional[Path]]] = value
        elif isinstance(value, CarriesDistinctSingleValueHook):
            # It's a hook - get initial value
            initial_value: Optional[Path] = value._get_single_value()
            value_hook: Optional[HookLike[Optional[Path]]] = value._get_single_value_hook()
        elif isinstance(value, (Path, type(None))):
            # It's a direct value
            initial_value = value
            value_hook: Optional[HookLike[Optional[Path]]] = None
        else:
            raise ValueError(f"Invalid value: {value}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Verify the value is a Path or None
            current_value = x.get("value", initial_value)
            if current_value is not None and not isinstance(current_value, Path):
                return False, f"Value must be a Path or None, got {type(current_value)}"
            return True, "Verification method passed"

        super().__init__(
            {
                "value": initial_value
            },
            {
                "value": Hook(self, self._get_single_value, self._set_single_value)
            },
            verification_method=verification_method,
            parent=parent
        )
        
        # Store hook for later binding
        self._value_hook = value_hook
        
        if value_hook is not None:
            self.bind_to(value_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_to(self, observable_or_hook: ObservableSingleValueLike[Optional[Path]] | HookLike[Optional[Path]] | CarriesDistinctSingleValueHook[Optional[Path]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().establish_binding(observable_or_hook, initial_sync_mode)

    def unbind_from(self, observable_or_hook: ObservableSingleValueLike[Optional[Path]] | HookLike[Optional[Path]] | CarriesDistinctSingleValueHook[Optional[Path]]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().remove_binding(observable_or_hook)

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    def _get_single_value(self) -> Optional[Path]:
        """Get the current path value."""
        return self._get_component_value("value")

    def _get_single_value_hook(self) -> HookLike[Optional[Path]]:
        """Get self as a hook for binding."""
        return self._component_hooks["value"]

    def _set_single_value(self, value: Optional[Path]) -> None:
        """Set the path value."""
        self._set_component_value("value", value)

    def initialize_widgets(self) -> None:
        self._label = GuardedLabel(self)
        self._edit = GuardedLineEdit(self._owner_widget)
        self._button = QPushButton("…", self._owner_widget)
        self._clear = QPushButton("✕", self._owner_widget)
        self._button.clicked.connect(self._browse)
        self._edit.editingFinished.connect(self._on_edited)
        self._clear.clicked.connect(self._on_clear)

    def update_widgets_from_component_values(self) -> None:
        """Update the widgets from the component values."""
        if not hasattr(self, '_edit'):
            return
            
        p = self._get_single_value()
        text = "" if p is None else str(p)
        
        self._edit.blockSignals(True)
        try:
            self._edit.setText(text)
            with self._internal_update():
                self._label.setText(text)
        finally:
            self._edit.blockSignals(False)

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the widgets."""
        raw = self._edit.text().strip()
        self._set_single_value(None if raw == "" else Path(raw))

    def _on_edited(self) -> None:
        """Handle line edit editing finished."""
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    def _browse(self) -> None:
        """Handle browse button click."""
        if self._mode == "directory":
            sel = QFileDialog.getExistingDirectory(self._owner_widget, self._dialog_title)
            path = Path(sel) if sel else None
        else:
            sel, _ = QFileDialog.getOpenFileName(self._owner_widget, self._dialog_title)
            path = Path(sel) if sel else None
        if path is not None:
            self._edit.blockSignals(True)
            try:
                self._edit.setText(str(path))
            finally:
                self._edit.blockSignals(False)
            self.update_component_values_from_widgets()

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
        """Handle clear button click."""
        self._edit.blockSignals(True)
        try:
            self._edit.setText("")
        finally:
            self._edit.blockSignals(False)
        self.update_component_values_from_widgets()

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def value(self) -> Optional[Path]:
        """Get the current path value."""
        return self._get_single_value()

    @value.setter
    def value(self, new_value: Optional[Path]) -> None:
        """Set the path value."""
        self._set_single_value(new_value)


