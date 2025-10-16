from typing import Any, Optional, Protocol, Mapping, Union, TypeVar, Generic, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout

from observables import HookLike, ObservableSingleValueLike

from integrated_widgets.widget_controllers.display_value_controller import DisplayValueController
from integrated_widgets.util.base_controller import BaseController


# ---- Strategy type ----------------------------------------------

HK = TypeVar("HK", bound=str)
HV = TypeVar("HV")
C = TypeVar("C", bound=BaseController, contravariant=True)

class LayoutStrategyForControllers(Protocol, Generic[C]):
    def __call__(
        self,
        parent: QWidget,
        controller: C) -> Union[QLayout, QWidget]:
        """
        Build and return either:
          - a QLayout whose parent is `parent`, or
          - a QWidget (e.g., QGroupBox/QFrame) whose parent is `parent`.
        You must place the provided `widgets` into that layout/widget.
        """
        ...

class IQtBaseWidget(QWidget, Generic[HK, HV, C]):

    def __init__(
        self,
        controller: C,
        layout_strategy: LayoutStrategyForControllers,
        parent: Optional[QWidget] = None
        ) -> None:

        super().__init__(parent)

        # Store references (the container owns/parents the widgets once laid out)
        self._controller: C = controller
        self._strategy: LayoutStrategyForControllers = layout_strategy

        self._host_layout = QVBoxLayout(self) # Stable host; we swap content within it
        self._host_layout.setContentsMargins(0, 0, 0, 0)
        self._host_layout.setSpacing(0)

        self._content_root: QWidget | None = None # If strategy returns a QWidget
        self._content_layout: QLayout | None = None # If strategy returns a QLayout

        self._build()

    ###########################################################################
    # Internal methods
    ###########################################################################

    def _rebuild(self) -> None:
        self._clear_host()
        self._build()

    def _build(self) -> None:
        """
        Apply the strategy to arrange widgets.
        """

        # Ensure none of the widgets are accidentally deleted: do not call deleteLater() on them.
        # Layouting them will set their parent appropriately.

        result = self._strategy(self, self._controller)

        if isinstance(result, QLayout):
            # Strategy gave us a layout for 'self'
            self._content_layout = result
            # If the strategy created result with parent=self, Qt owns it. Attach in host:
            wrapper = QWidget(self)
            wrapper.setLayout(result)
            self._content_root = wrapper
            self._host_layout.addWidget(wrapper, 1)

        elif isinstance(result, QWidget):
            # Strategy gave us a child widget (e.g., QGroupBox/QFrame) parented to self
            self._content_root = result
            self._host_layout.addWidget(result, 1)

        else:
            raise TypeError("Strategy must return a QLayout or QWidget")

    def _clear_host(self) -> None:
        """
        Remove previous content from the stable host without deleting our managed child widgets.
        Created wrapper/group boxes are owned by this container and are safe to deleteLater().
        """

        # Remove any single hosted widget
        while self._host_layout.count():
            item = self._host_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                # This deletes wrapper/group containers, not your supplied leaf widgets.
                w.deleteLater()

        self._content_layout = None
        self._content_root = None

    ###########################################################################
    # Public API
    ###########################################################################

    def set_strategy(self, strategy: LayoutStrategyForControllers) -> None:
        """
        Replace the layout strategy and rebuild.
        """

        self._strategy = strategy
        self._rebuild()

    def set_controller(self, controller: C) -> None:
        """
        Replace the widget set and rebuild.
        If any incoming widget already has a parent, it will be reparented automatically
        when added to the new layout.
        """

        self._controller = controller
        self._rebuild()

    def get_hook(self, key: HK) -> HookLike[HV]:
        return self._controller.get_hook(key) # type: ignore

    def get_value_of_hook(self, key: HK) -> HV:
        return self._controller.get_value_of_hook(key) # type: ignore

