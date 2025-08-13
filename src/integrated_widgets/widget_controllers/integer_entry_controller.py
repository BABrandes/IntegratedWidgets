from __future__ import annotations

from typing import Callable, Optional, overload

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike, ObservableSingleValue
from integrated_widgets.guarded_widgets import GuardedLineEdit


Model = ObservableSingleValueLike[int] | ObservableSingleValue[int]


class IntegerEntryController(ObservableController[Model]):

    @overload
    def __init__(
        self,
        observable: Model,
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: int,
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        observable_or_value,
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        if isinstance(observable_or_value, (ObservableSingleValueLike, ObservableSingleValue)):
            observable = observable_or_value
        elif isinstance(observable_or_value, int):
            observable = ObservableSingleValue(observable_or_value)
        else:
            raise TypeError(f"Invalid type for observable_or_value: {type(observable_or_value)}")
        self._validator = validator
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._edit = GuardedLineEdit(self.owner_widget)
        self._edit.editingFinished.connect(self._on_edited)

    def update_widgets_from_observable(self) -> None:
        with self._internal_update():
            self._edit.setText(str(int(self._observable.value)))

    def update_observable_from_widgets(self) -> None:
        try:
            value = int(self._edit.text().strip())
            if self._validator is not None and not self._validator(value):
                self.update_widgets_from_observable()
                return
        except Exception:
            self.update_widgets_from_observable()
            return
        self._observable.set_value(value)

    def _on_edited(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    @property
    def line_edit(self) -> GuardedLineEdit:
        return self._edit


