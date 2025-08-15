from __future__ import annotations

from typing import Optional, overload

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike
from observables import ObservableSingleValue
from integrated_widgets.guarded_widgets import GuardedCheckBox

Observable = ObservableSingleValueLike[bool] | ObservableSingleValue[bool]

class CheckBoxController(ObservableController[Observable]):

    @overload
    def __init__(
            self,
            observable: Observable,
            *,
            text: str = "",
            parent: Optional[QWidget] = None,
        ) -> None: ...
    
    @overload
    def __init__(  # type: ignore
        self,
        observable_or_value,
        *,
        text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None: ...
        
    def __init__(  # type: ignore
            self,
            observable_or_value,
            *,
            text: str = "",
            parent: Optional[QWidget] = None,
        ) -> None:

        if isinstance(observable_or_value, (ObservableSingleValueLike, ObservableSingleValue)):
            observable = observable_or_value
        elif isinstance(observable_or_value, bool):
            observable = ObservableSingleValue(observable_or_value)
        else:
            raise TypeError(f"Invalid type for observable_or_value: {type(observable_or_value)}")

        self._text = text
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._check = GuardedCheckBox(self.owner_widget, self._text)
        self._check.stateChanged.connect(lambda _s: self._on_changed())

    def update_widgets_from_observable(self) -> None:
        with self._internal_update():
            self._check.setChecked(bool(self._observable.single_value))

    def update_observable_from_widgets(self) -> None:
        self._observable.single_value = self._check.isChecked()

    def _on_changed(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    @property
    def widget_check_box(self) -> GuardedCheckBox:
        return self._check


