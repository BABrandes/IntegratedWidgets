from __future__ import annotations

from typing import Callable, Optional, TypeVar, overload, Generic, Any

from PySide6.QtWidgets import QWidget, QButtonGroup

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import (
    ObservableSelectionOptionLike,
)
from integrated_widgets.guarded_widgets import GuardedRadioButton

from observables import ObservableSelectionOption

T = TypeVar("T")
Model =  ObservableSelectionOptionLike[T] | ObservableSelectionOption[T]

DEFAULT_FORMATTER: Callable[[Any], str] = lambda e: str(e)

class RadioButtonsController(ObservableController[Model], Generic[T]):
    @overload
    def __init__(
        self,
        observable: Model,
        *,
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        available_values: Optional[list[T]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: T,
        *,
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        available_values: Optional[list[T]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        observable_or_value,
        *,
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        available_values: Optional[list[T]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        if isinstance(observable_or_value, (ObservableSelectionOptionLike, ObservableSelectionOption)):
            observable: Model = observable_or_value
        else:
            raise TypeError("Expected an selection-option-like observable for RadioButtonsController")
        self._formatter: Callable[[T], str] = formatter
        opts = None
        try:
            opts = list(observable.options)
        except Exception:
            opts = None
        self._available_values: list[T] = available_values if available_values is not None else (opts or [])
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._group = QButtonGroup(self.owner_widget)
        self._buttons: list[GuardedRadioButton] = []
        self._rebuild_buttons()
        # connect after build
        for btn in self._buttons:
            btn.toggled.connect(self._on_toggled)

    def update_widgets_from_observable(self) -> None:
        try:
            value = self._observable.selected_option  # type: ignore[attr-defined]
        except Exception:
            try:
                value = self._observable.selected_option  # type: ignore[attr-defined]
            except Exception:
                value = None
        # ensure buttons match available_values
        if len(self._buttons) != len(self._available_values):
            self._rebuild_buttons()
        # set checked
        if value is not None:
            for btn in self._buttons:
                if btn.property("value") == value:
                    btn.setChecked(True)
                    break

    def update_observable_from_widgets(self) -> None:
        for btn in self._buttons:
            if btn.isChecked():
                value = btn.property("value")
                self._observable.selected_option = value  # type: ignore[attr-defined]
                break

    ###########################################################################
    # Internal
    ###########################################################################
    def _rebuild_buttons(self) -> None:
        # disconnect old
        try:
            for btn in self._buttons:
                btn.toggled.disconnect()
                self._group.removeButton(btn)
                btn.setParent(None)
        except Exception:
            pass
        self._buttons = []
        # build new
        for member in sorted(self._available_values, key=lambda m: str(m)):
            btn = GuardedRadioButton(self.owner_widget, self._formatter(member))
            btn.setProperty("value", member)
            self._group.addButton(btn)
            self._buttons.append(btn)

    def _on_toggled(self, checked: bool) -> None:
        if not checked or self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    ###########################################################################
    # Disposal
    ###########################################################################
    def dispose_before_children(self) -> None:
        for btn in self._buttons:
            try:
                btn.toggled.disconnect()
            except Exception:
                pass

    ###########################################################################
    # Public access
    ###########################################################################
    
    @property
    def widgets_radio_buttons(self) -> list[GuardedRadioButton]:
        return list(self._buttons)


