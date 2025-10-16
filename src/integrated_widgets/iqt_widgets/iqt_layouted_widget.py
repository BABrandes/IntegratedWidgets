"""
A flexible container widget that applies a user-defined layout strategy to organize content.

The IQtLayoutedWidget separates the layout logic from the content, allowing you to:
- Dynamically change how widgets are arranged at runtime
- Reuse layout strategies across different widget compositions
- Keep your layout code modular and testable

Example Usage
-------------
```python
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLabel

# Define a simple horizontal layout strategy
def horizontal_layout(parent, widgets):
    layout = QHBoxLayout()
    for widget in widgets:
        layout.addWidget(widget)
    return layout

# Create widgets to layout
buttons = [QPushButton("Button 1"), QPushButton("Button 2"), QLabel("Status")]

# Create the layouted widget
container = IQtLayoutedWidget(horizontal_layout, buttons)

# Later, switch to a different layout strategy
def vertical_layout(parent, widgets):
    layout = QVBoxLayout()
    for widget in widgets:
        layout.addWidget(widget)
    return layout

container.set_strategy(vertical_layout)
```
"""

from typing import Optional, Protocol, Union, TypeVar, Generic
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout

P = TypeVar("P", contravariant=True)

class LayoutStrategy(Protocol[P]):
    """
    Protocol defining a layout strategy callable.
    
    A layout strategy takes a parent widget and a payload, then returns either
    a QLayout or QWidget containing the arranged content.
    """
    def __call__(
        self,
        parent: QWidget,
        payload: P,
    ) -> Union[QLayout, QWidget]:
        """
        Build and return either:
          - a QLayout whose parent is `parent`, or
          - a QWidget (e.g., QGroupBox/QFrame) whose parent is `parent`.
        
        Args:
            parent: The parent widget that will contain the layout/widget
            payload: The data/widgets to arrange (type determined by your strategy)
        
        Returns:
            Either a QLayout or QWidget containing the arranged content
        """
        ...

class IQtLayoutedWidget(QWidget, Generic[P]):
    """
    A container widget that applies a layout strategy to organize content.
    
    This widget acts as a host that can dynamically switch between different
    layout strategies without recreating the entire widget tree.
    
    Type Parameters:
        P: The type of payload your layout strategy expects (e.g., list of widgets,
           dict of named widgets, custom data structure)
    
    Args:
        layout_strategy: A callable that creates the layout from the payload
        payload: The data/widgets to be laid out
        parent: Optional parent widget
    """

    def __init__(
        self,
        layout_strategy: LayoutStrategy[P],
        payload: P,
        parent: Optional[QWidget] = None,
        ) -> None:

        super().__init__(parent)

        self._strategy: LayoutStrategy[P] = layout_strategy
        self._payload: P = payload

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

        result = self._strategy(self, self._payload)

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

    def set_strategy(self, strategy: LayoutStrategy[P]) -> None:
        """
        Replace the layout strategy and rebuild the widget.
        
        This allows you to dynamically change how the payload is laid out
        without recreating the payload widgets themselves.
        
        Args:
            strategy: The new layout strategy to apply
        """

        self._strategy = strategy
        self._rebuild()