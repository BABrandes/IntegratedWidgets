from __future__ import annotations

from typing import Generic, Optional, TypeVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QListWidgetItem

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import (
    ObservableMultiSelectionOptionLike,
)
from integrated_widgets.guarded_widgets import GuardedListWidget

from observables import ObservableMultiSelectionOption


T = TypeVar("T")
Model = ObservableMultiSelectionOptionLike[T] | ObservableMultiSelectionOption[T]


class DoubleListSelectionController(ObservableController[Model], Generic[T]):
    """Controller providing two list views and two move buttons to manage a multi-selection.

    Left list shows available (unselected) items.
    Right list shows selected items.
    '>' moves selected items from left to right (adds to selected_options).
    '<' moves selected items from right to left (removes from selected_options).
    """

    def __init__(
        self,
        observable: Model,
        *,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################
    def initialize_widgets(self) -> None:
        self._left = GuardedListWidget(self.owner_widget)
        self._right = GuardedListWidget(self.owner_widget)
        self._left.setSelectionMode(GuardedListWidget.SelectionMode.ExtendedSelection)
        self._right.setSelectionMode(GuardedListWidget.SelectionMode.ExtendedSelection)

        self._to_right = QPushButton(">", self.owner_widget)
        self._to_left = QPushButton("<", self.owner_widget)
        self._to_right.clicked.connect(self._on_move_to_right)
        self._to_left.clicked.connect(self._on_move_to_left)

        # Update move button enabled state on selection change
        self._left.itemSelectionChanged.connect(self._update_button_states)
        self._right.itemSelectionChanged.connect(self._update_button_states)

    def update_widgets_from_observable(self) -> None:
        # Build left = options - selected, right = selected
        try:
            options = set(self._observable.available_options)  # type: ignore[attr-defined]
        except Exception:
            options = set()
        try:
            selected = set(self._observable.selected_options)  # type: ignore[attr-defined]
        except Exception:
            selected = set()
        available = [v for v in options if v not in selected]
        # Rebuild lists
        with self._internal_update():
            self._left.clear()
            self._right.clear()
            for v in sorted(available, key=lambda x: str(x)):
                item = QListWidgetItem(str(v), self._left)
                item.setData(Qt.ItemDataRole.UserRole, v)
            for v in sorted(selected, key=lambda x: str(x)):
                item = QListWidgetItem(str(v), self._right)
                item.setData(Qt.ItemDataRole.UserRole, v)
        self._update_button_states()

    def update_observable_from_widgets(self) -> None:
        # Not used directly; mutations happen in move handlers
        pass

    ###########################################################################
    # Internal
    ###########################################################################
    def _update_button_states(self) -> None:
        self._to_right.setEnabled(len(self._left.selectedItems()) > 0)
        self._to_left.setEnabled(len(self._right.selectedItems()) > 0)

    def _on_move_to_right(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._left, direction=">")

    def _on_move_to_left(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._right, direction="<")

    def _move(self, selected_from: GuardedListWidget, direction: str) -> None:
        # Collect items to move
        items = list(selected_from.selectedItems())
        if not items:
            return
        # Compute new selected set
        try:
            current_selected = set(self._observable.selected_options)  # type: ignore[attr-defined]
        except Exception:
            current_selected = set()
        members = [it.data(Qt.ItemDataRole.UserRole) for it in items]
        if direction == ">":
            new_selected = current_selected.union(members)
        else:
            new_selected = {v for v in current_selected if v not in members}
        # Apply to observable
        self.set_block_signals(self)
        try:
            self._observable.selected_options = new_selected  # type: ignore[attr-defined]
        finally:
            self.set_unblock_signals(self)
        # Rebuild UI from model
        self.update_widgets_from_observable()

    ###########################################################################
    # Public accessors
    ###########################################################################
    @property
    def widget_left_list(self) -> GuardedListWidget:
        return self._left

    @property
    def widget_right_list(self) -> GuardedListWidget:
        return self._right

    @property
    def widget_to_right_button(self) -> QPushButton:
        return self._to_right

    @property
    def widget_to_left_button(self) -> QPushButton:
        return self._to_left

    ###########################################################################
    # Disposal
    ###########################################################################
    def dispose_before_children(self) -> None:
        try:
            self._to_right.clicked.disconnect()
        except Exception:
            pass
        try:
            self._to_left.clicked.disconnect()
        except Exception:
            pass
        try:
            self._left.itemSelectionChanged.disconnect()
        except Exception:
            pass
        try:
            self._right.itemSelectionChanged.disconnect()
        except Exception:
            pass


