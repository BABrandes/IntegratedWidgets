from __future__ import annotations

from typing import Generic, Optional, TypeVar, overload, Any
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
            parent: Optional[QWidget] = None,
        ) -> None: ...
    
    @overload
    def __init__(
        self,
        selected_value: Optional[T] = None,
        *,
        options: Optional[set[T]] = None,
        allow_none: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        observable_or_selected_value,
        *,
        options: Optional[set[T]] = None,
        allow_none: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        if isinstance(observable_or_selected_value, (ObservableSelectionOptionLike, ObservableSelectionOption)):
            observable = observable_or_selected_value
        else:
            observable = ObservableSelectionOption(selected_option=observable_or_selected_value, options=options or set(), allow_none=allow_none)  # type: ignore
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._combo = GuardedComboBox(self.owner_widget)
        self._combo.currentIndexChanged.connect(lambda _i: self._on_changed())

    def update_widgets_from_observable(self) -> None:
        options = self._observable.options
        selected = self._observable.selected_option
        self._combo.blockSignals(True)
        try:
            with self._internal_update():
                self._combo.clear()
                # Only show placeholder for None when options include None and allow_none
                if getattr(self._observable, "is_none_selection_allowed", False) and (None in options or selected is None):
                    self._combo.addItem("", None)
                for opt in sorted(options, key=lambda x: str(x)):
                    label = opt.name if isinstance(opt, Enum) else str(opt)
                    self._combo.addItem(label, userData=opt)
            # Select
            if selected is None:
                with self._internal_update():
                    self._combo.setCurrentIndex(0 if getattr(self._observable, "is_none_selection_allowed", False) else -1)
            else:
                for i in range(self._combo.count()):
                    if self._combo.itemData(i) == selected:
                        with self._internal_update():
                            self._combo.setCurrentIndex(i)
                        break
        finally:
            self._combo.blockSignals(False)

    def update_observable_from_widgets(self) -> None:
        idx = self._combo.currentIndex()
        if idx < 0:
            return
        value = self._combo.itemData(idx)
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
    def combo(self) -> GuardedComboBox:
        return self._combo


