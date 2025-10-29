from __future__ import annotations

from typing import Optional, Any, Iterable, Sequence
from logging import Logger
from contextlib import contextmanager

from integrated_widgets.controllers.core.base_controller import BaseController

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QAbstractButton, QWidget


from .base_controlled_widget import BaseControlledWidget


class ControlledRadioButtonGroup(BaseControlledWidget, QButtonGroup):
    """Model/controller for a dynamic set of buttons. No layout concerns here."""

    # Emitted before and after a batch of membership changes
    contentAboutToChange = Signal()
    contentChanged = Signal()

    # Emitted with fine-grained diffs; views can choose to listen to these
    buttonsAdded = Signal(list)    # list[QAbstractButton]
    buttonsRemoved = Signal(list)  # list[QAbstractButton]

    def __init__(self, controller: BaseController[Any, Any], parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None, *, exclusive: Optional[bool] = None):
        BaseControlledWidget.__init__(self, controller, logger)
        QButtonGroup.__init__(self, parent_of_widget)
        if exclusive is not None:
            self.setExclusive(exclusive)
        self._in_tx = 0
        self._pending_added: list[QAbstractButton] = []
        self._pending_removed: list[QAbstractButton] = []

    # ---------- batching ----------
    @contextmanager
    def transaction(self):
        """Group multiple add/remove operations into a single change."""
        self._begin()
        try:
            yield
        finally:
            self._end()

    def _begin(self):
        if self._in_tx == 0:
            self.contentAboutToChange.emit()
        self._in_tx += 1

    def _end(self):
        self._in_tx -= 1
        if self._in_tx == 0:
            if self._pending_added:
                self.buttonsAdded.emit(self._pending_added[:])
            if self._pending_removed:
                self.buttonsRemoved.emit(self._pending_removed[:])
            # Reset accumulators
            self._pending_added.clear()
            self._pending_removed.clear()
            self.contentChanged.emit()

    # ---------- API ----------
    def set_buttons(self, buttons: Iterable[QAbstractButton], *, start_id: int = 1) -> None:
        """Replace the entire membership with the given buttons."""
        new_list = list(buttons)
        with self.transaction():
            # remove old
            old = list(self.buttons())
            for b in old:
                self._remove_no_emit(b)
            # add new with deterministic IDs
            next_id = start_id
            for b in new_list:
                self._add_no_emit(b, next_id)
                next_id += 1

    def add_buttons(self, buttons: Iterable[QAbstractButton], *, start_id: Optional[int] = None) -> None:
        """Add buttons, assigning IDs sequentially from start_id or continuing from max existing ID."""
        btns = list(buttons)
        if not btns:
            return
        if start_id is None:
            # continue from current max id; default -1 when none exist
            current_ids = [self.id(b) for b in self.buttons()]
            start_id = (max(current_ids) if current_ids else 0) + 1
        with self.transaction():
            next_id = start_id
            for b in btns:
                self._add_no_emit(b, next_id)
                next_id += 1

    def remove_by_ids(self, ids: Sequence[int]) -> None:
        if not ids:
            return
        with self.transaction():
            for i in ids:
                btn = self.button(i)
                if btn:
                    self._remove_no_emit(btn)

    def clear_buttons(self) -> None:
        with self.transaction():
            for b in list(self.buttons()):
                self._remove_no_emit(b)

    # ---------- helpers without emitting per-op ----------
    def _add_no_emit(self, btn: QAbstractButton, id_value: int) -> None:
        # Caller owns parenting; this class does not set parents or layouts.
        self.addButton(btn, id_value)
        self._pending_added.append(btn)

    def _remove_no_emit(self, btn: QAbstractButton) -> None:
        self.removeButton(btn)
        self._pending_removed.append(btn)