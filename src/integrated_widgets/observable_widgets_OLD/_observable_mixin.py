from __future__ import annotations

from typing import Callable, Generic, Optional, TypeVar, final
from abc import ABC, abstractmethod

from observables import Observable

O = TypeVar("O", bound=Observable)

class ObservableWithObservableMixin(Generic[O], ABC):
    """
    Mixin that encapsulates the logic for binding a Qt widget/frame to an observable.

    Requirements for subclasses:
    - Must be a QObject subclass (e.g., QWidget or QFrame) and define a Qt signal named `widget_changed`.
    - Must implement `update_widget` and `update_observable`.
    """

    def __init__(self, observable: O) -> None:
        self._observable: O = observable
        self._internal_update_observable_callback: Callable[[], None] = self.update_observable
        self._observable.add_listeners(self._internal_update_observable_callback)
        self._blocking_objects: set[object] = set()

    def construction_finished(self):
        self._internal_update_widget_and_emit_signal()

    @final
    def _internal_update_widget_and_emit_signal(self):
        if self._blocking_objects:
            return
        self.set_block_signals(self)
        self.update_widget()
        # Subclass must define this signal
        self.widget_changed.emit()  # type: ignore[attr-defined]
        self.set_unblock_signals(self)

    @final
    def _internal_update_observable(self):
        if self._blocking_objects:
            return
        self.set_block_signals(self)
        self.update_observable()
        self.set_unblock_signals(self)

    @final
    def force_update_widget_from_observable(self):
        self.set_unblock_signals(self)
        self._internal_update_widget_and_emit_signal()

    @property
    def observable(self) -> O:
        return self._observable

    @property
    def is_blocking_signals(self) -> bool:
        return bool(self._blocking_objects)
    
    def set_block_signals(self, obj: object) -> None:
        self._blocking_objects.add(obj)

    def set_unblock_signals(self, obj: object) -> None:
        if obj in self._blocking_objects:
            self._blocking_objects.remove(obj)
        else:
            raise ValueError(f"Object {obj} is not blocking signals")
        
    def force_unblock_signals(self) -> None:
        self._blocking_objects.clear()

    def set_or_replace_observable(self, observable: O) -> None:
        """
        This method is used to set or replace the observable.
        If the observable is the same as the current observable, it will not be replaced.
        If the observable is different, the current observable will be removed and the new observable will be added.
        The widget will be updated to reflect the new observable.
        """
        
        if self._observable == observable:
            return
        
        # Detach from previous observable
        self._observable.remove_listeners(self._internal_update_observable_callback)

        # Attach to new observable
        self._observable = observable
        self._observable.add_listeners(self._internal_update_observable_callback)

        self._internal_update_widget_and_emit_signal()

    #########################################################################################
    # Abstract methods
    #########################################################################################

    @abstractmethod
    def update_widget(self) -> None:  # pragma: no cover - abstract
        """
        This method is called when the widget must be updated to reflect the current value of the observable.

        It must be implemented by the subclass.

        The widget must be updated to reflect the current value of the observable.
        """
        ...

    @abstractmethod
    def update_observable(self) -> None:  # pragma: no cover - abstract
        """
        This method is called when the widget has changed and the observable must be updated to reflect the current value of the widget.

        It must be implemented by the subclass.

        The observable must be updated to reflect the current value of the widget.
        """
        ...
