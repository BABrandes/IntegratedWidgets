from __future__ import annotations
from typing import Generic, TypeVar
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLayoutItem, QSpacerItem

T = TypeVar('T', bound=QWidget)

class BlankableWidget(QWidget, Generic[T]):
    """
    Wrap any QWidget so you can toggle it into 'blank space' without
    moving anything else in the parent layout.

    - When blanked, the inner widget is removed from this wrapper's layout,
      signals are blocked, interaction is disabled, and a spacer with
      matching size/policy is inserted in its place.
    - When unblanked, the spacer is removed and the widget reinserted at
      the same index; signals/interaction are restored.

    Usage:
        inner = SomeWidget(...)
        wrapper = BlankableWidget(inner)
        parent_layout.addWidget(wrapper)

        wrapper.blank()   # show as blank space (no signals, no input)
        wrapper.unblank() # bring the real widget back
        wrapper.setBlanked(True/False)  # convenience
    """
    def __init__(self, inner_widget: T):
        # Capture inner's parent and use it as BlankableWidget's parent
        # Note: parent() returns QObject|None, but QWidget.__init__ accepts it
        super().__init__(inner_widget.parent())  # type: ignore[arg-type]
        
        # Reparent inner widget to this wrapper
        inner_widget.setParent(self)

        self._inner_widget = inner_widget
        self._was_enabled = inner_widget.isEnabled()
        self._was_signals_blocked = inner_widget.signalsBlocked()
        self._was_transparent_mouse = inner_widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._blanked = False

        # wrapper layout: keep margins 0 so geometry passes through
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self._inner_widget)

        # create a reusable spacer that mimics size hints & policies
        sp = self._inner_widget.sizePolicy()
        self._spacer = QSpacerItem(
            max(self._inner_widget.sizeHint().width(), 0),
            max(self._inner_widget.sizeHint().height(), 0),
            sp.horizontalPolicy(),
            sp.verticalPolicy()
        )

        # mirror the wrapper's size policy to the inner by default
        self.setSizePolicy(sp)

    def _update_spacer_hint(self) -> None:
        # Refresh spacer dimensions to track current inner sizeHint
        hint = self._inner_widget.sizeHint()
        # QSpacerItem has no setters for policies after construction,
        # but we can safely adjust its cached size via changeSize().
        hp = self._spacer.sizePolicy().horizontalPolicy()
        vp = self._spacer.sizePolicy().verticalPolicy()
        self._spacer.changeSize(hint.width(), hint.height(), hp, vp)

    def isBlanked(self) -> bool:
        return self._blanked

    def setBlanked(self, value: bool) -> None:
        if value:
            self.blank()
        else:
            self.unblank()

    def blank(self) -> None:
        if self._blanked:
            return

        # belt & suspenders: make absolutely non-interactive & silent
        self._was_enabled = self._inner_widget.isEnabled()
        self._was_signals_blocked = self._inner_widget.signalsBlocked()
        self._was_transparent_mouse = self._inner_widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._inner_widget.blockSignals(True)
        self._inner_widget.setEnabled(False)
        self._inner_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # replace widget -> spacer at the same index
        idx = self._layout.indexOf(self._inner_widget)
        if idx == -1:
            # not expected, but ensure we know where to put the spacer
            idx = 0

        self._update_spacer_hint()
        self._layout.removeWidget(self._inner_widget)   # keeps widget alive & parented
        self._inner_widget.setVisible(False)            # no painting
        self._layout.insertItem(idx, self._spacer)

        self._blanked = True

    def unblank(self) -> None:
        if not self._blanked:
            return

        # locate spacer and its index
        # Walk the layout to find the QLayoutItem that *is* our spacer
        spacer_index = -1
        for i in range(self._layout.count()):
            item: QLayoutItem = self._layout.itemAt(i)
            if item is self._spacer:
                spacer_index = i
                break

        if spacer_index != -1:
            # takeAt transfers ownership back to us; don't delete it
            self._layout.takeAt(spacer_index)

        # reinsert the inner widget at the same position
        insert_index = spacer_index if spacer_index != -1 else self._layout.count()
        self._layout.insertWidget(insert_index, self._inner_widget)
        self._inner_widget.setVisible(True)

        # restore previous interaction state
        self._inner_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, self._was_transparent_mouse)
        self._inner_widget.setEnabled(self._was_enabled)
        self._inner_widget.blockSignals(self._was_signals_blocked)

        self._blanked = False

    # Optional: pass-through helpers
    def innerWidget(self) -> T:
        return self._inner_widget