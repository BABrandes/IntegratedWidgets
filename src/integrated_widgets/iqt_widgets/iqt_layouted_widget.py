"""
A flexible container widget that applies a user-defined layout strategy to organize content.

The IQtLayoutedWidget separates the layout logic from the content, allowing you to:
- Dynamically change how widgets are arranged at runtime
- Reuse layout strategies across different widget compositions
- Keep your layout code modular and testable
- Defer layout creation until needed

The widget safely manages payload widgets - they are never deleted, only re-parented
when the layout strategy changes.

Example Usage
-------------
```python
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from integrated_widgets.iqt_widgets.layout_payload import BaseLayoutPayload

# Create a payload with widgets - use dataclass!
@dataclass(frozen=True)
class ButtonPayload(BaseLayoutPayload):
    button1: QPushButton
    button2: QPushButton
    label: QLabel

# Define layout strategies
def horizontal_layout(parent, payload):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(payload.button1)
    layout.addWidget(payload.button2)
    layout.addWidget(payload.label)
    return widget

def vertical_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.button1)
    layout.addWidget(payload.button2)
    layout.addWidget(payload.label)
    return widget

# Create and use - frozen dataclass ensures immutability
payload = ButtonPayload(
    button1=QPushButton("Button 1"),
    button2=QPushButton("Button 2"),
    label=QLabel("Status")
)
container = IQtLayoutedWidget(payload, horizontal_layout)

# Switch to vertical layout - widgets are safely re-parented
container.set_strategy(vertical_layout)
```
"""

from typing import Optional, Protocol, TypeVar, Generic
from PySide6.QtWidgets import QWidget, QVBoxLayout

from .layout_payload import BaseLayoutPayload

P = TypeVar("P", bound=BaseLayoutPayload)  # Payload must be a BaseLayoutPayload

class LayoutStrategy(Protocol[P]): # type: ignore
    """
    Protocol defining a layout strategy callable.
    
    A layout strategy takes a parent widget and a payload, then returns a QWidget
    containing the arranged content.
    """
    def __call__(
        self,
        parent: QWidget,
        payload: P,
    ) -> QWidget:
        """
        Build and return a QWidget containing the payload's widgets arranged in a layout.
        
        The strategy should:
        1. Create a container widget (QWidget, QGroupBox, QFrame, etc.)
        2. Create and set a layout on that widget
        3. Add the payload's widgets (accessed via dataclass fields or registered_widgets) to the layout
        4. Return the container widget
        
        Args:
            parent: The parent IQtLayoutedWidget (for context; don't manually parent the return value)
            payload: The payload (frozen dataclass extending BaseLayoutPayload)
        
        Returns:
            A QWidget containing the arranged payload widgets
            
        Example:
            ```python
            def my_layout_strategy(parent, payload):
                # Create container
                widget = QWidget()
                layout = QVBoxLayout(widget)
                
                # Access payload's widgets directly by field name
                layout.addWidget(payload.button1)
                layout.addWidget(payload.button2)
                
                # Or iterate over all registered widgets
                for w in payload.registered_widgets:
                    layout.addWidget(w)
                
                return widget
            ```
        """
        ...

class IQtLayoutedWidget(QWidget, Generic[P]):
    """
    A container widget that applies a layout strategy to organize content.
    
    This widget acts as a host that can dynamically switch between different
    layout strategies without recreating the payload. Payload widgets are safely
    managed and never deleted - they're just re-parented when layouts change.
    
    The payload must be a frozen dataclass extending BaseLayoutPayload, with all
    fields being QWidget instances. This ensures type safety and immutability.
    
    Type Parameters:
        P: The type of payload (frozen dataclass extending BaseLayoutPayload)
    
    Args:
        payload: The payload containing widgets (frozen dataclass with QWidget fields)
        layout_strategy: A callable that creates a QWidget with the payload's widgets arranged.
                        If None, the widget remains empty until set_strategy() is called.
                        Can be changed dynamically via set_strategy().
        parent: Optional parent widget
    """

    def __init__(
        self,
        payload: P,
        layout_strategy: Optional[LayoutStrategy[P]] = None,
        parent: Optional[QWidget] = None,
        ) -> None:

        super().__init__(parent)

        self._strategy: Optional[LayoutStrategy[P]] = layout_strategy
        self._payload: P = payload

        self._host_layout = QVBoxLayout(self) # Stable host; we swap content within it
        self._host_layout.setContentsMargins(0, 0, 0, 0)
        self._host_layout.setSpacing(0)

        self._content_root: QWidget | None = None # Content widget returned by strategy

        if self._strategy is not None:
            self._build()

    ###########################################################################
    # Internal methods
    ###########################################################################

    def _rebuild(self) -> None:
        """Rebuild the layout with the current strategy."""
        self._clear_host()
        self._build()

    def _build(self) -> None:
        """
        Apply the strategy to arrange widgets.
        
        The strategy must return a QWidget containing the payload's widgets.
        """
        
        # Skip if no strategy set yet
        if self._strategy is None:
            return

        # Call strategy to get the arranged widget
        result = self._strategy(self, self._payload)

        if not isinstance(result, QWidget):
            raise TypeError(f"Strategy must return a QWidget, got {type(result).__name__}")

        # Add the widget to our host layout
        self._content_root = result
        self._host_layout.addWidget(result, 1)

    def _clear_host(self) -> None:
        """
        Remove previous content from the stable host without deleting payload widgets.
        
        This method safely un-parents all payload widgets before deleting the
        container widget, ensuring the payload's widgets are never accidentally destroyed.
        """
        
        # First, un-parent all payload widgets to prevent them from being deleted
        # when we delete the container
        payload_widgets = self._payload.registered_widgets
        for widget in payload_widgets:
            if widget is not None:
                try:
                    widget.setParent(None)  # Un-parent to prevent deletion
                except RuntimeError:
                    # Widget may already be deleted, ignore
                    pass
        
        # Now safe to delete the container widget
        while self._host_layout.count():
            item = self._host_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                # This deletes the container widget returned by the strategy
                w.deleteLater()

        self._content_root = None

    ###########################################################################
    # Public API
    ###########################################################################

    def set_layout_strategy(self, layout_strategy: LayoutStrategy[P]) -> None:
        """
        Replace the layout strategy and rebuild the widget.
        
        This allows you to dynamically change how the payload is laid out
        without recreating the payload widgets themselves. Payload widgets
        are safely un-parented before the old layout is destroyed, then
        re-parented by the new strategy.
        
        **Important:** The payload cannot be changed - only the layout strategy.
        This ensures proper lifecycle management and prevents orphaned widgets.
        
        Args:
            strategy: The new layout strategy to apply
            
        Example:
            ```python
            # Create widget with horizontal layout
            container = IQtLayoutedWidget(my_payload, horizontal_layout)
            
            # Later, switch to vertical layout
            container.set_layout_strategy(vertical_layout)  # Widgets are safely re-arranged
            ```
        """
        
        self._strategy = layout_strategy
        self._rebuild()