from __future__ import annotations

from typing import Generic, Optional, TypeVar, overload, Any, Callable
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSelectionOptionLike, ObservableSelectionOption
from integrated_widgets.guarded_widgets import GuardedComboBox


T = TypeVar("T")
Model = ObservableSelectionOptionLike[T] | ObservableSelectionOption[T]

class ComboBoxController(ObservableController[Model], Generic[T]):

    @overload
    def __init__(
            self,
            observable: Model,
            *,
            allow_none: bool = True,
            formatter: Optional[Callable[[T], str]] = None,
            parent: Optional[QWidget] = None,
        ) -> None: ...
    
    @overload
    def __init__(
        self,
        selected_value: Optional[T] = None,
        *,
        options: Optional[set[T]] = None,
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        observable_or_selected_value,
        *,
        options: Optional[set[T]] = None,
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        self._formatter = formatter
        if isinstance(observable_or_selected_value, (ObservableSelectionOptionLike, ObservableSelectionOption)):
            observable = observable_or_selected_value
        else:
            observable = ObservableSelectionOption(selected_option=observable_or_selected_value, options=options or set(), allow_none=allow_none)  # type: ignore
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._combobox = GuardedComboBox(self.owner_widget)
        self._combobox.currentIndexChanged.connect(lambda _i: self._on_changed())

    def update_widgets_from_observable(self) -> None:
        options = self._observable.options
        selected = self._observable.selected_option
        self._combobox.blockSignals(True)
        try:
            with self._internal_update():
                self._combobox.clear()
                # Only show placeholder for None when options include None and allow_none
                if getattr(self._observable, "is_none_selection_allowed", False) and (None in options or selected is None):
                    self._combobox.addItem("", None)
                for opt in sorted(options, key=lambda x: str(x)):
                    label = self._formatter(opt) if self._formatter is not None else str(opt)
                    self._combobox.addItem(label, userData=opt)
            # Select
            if selected is None:
                with self._internal_update():
                    self._combobox.setCurrentIndex(0 if getattr(self._observable, "is_none_selection_allowed", False) else -1)
            else:
                for i in range(self._combobox.count()):
                    if self._combobox.itemData(i) == selected:
                        with self._internal_update():
                            self._combobox.setCurrentIndex(i)
                        break
        finally:
            self._combobox.blockSignals(False)

    def update_observable_from_widgets(self) -> None:
        idx = self._combobox.currentIndex()
        if idx < 0:
            return
        value = self._combobox.itemData(idx)
        # Treat empty string entry as None only when None is allowed
        if value is None and getattr(self._observable, "is_none_selection_allowed", False):
            self._observable.selected_option = None  # type: ignore[assignment]
        else:
            self._observable.selected_option = value

    def _on_changed(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    @property
    def widget_combobox(self) -> GuardedComboBox:
        return self._combobox


