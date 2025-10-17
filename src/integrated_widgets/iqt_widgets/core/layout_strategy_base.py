from typing import Any, Protocol, TypeVar
from PySide6.QtWidgets import QWidget

from .layout_payload_base import LayoutPayloadBase

P = TypeVar("P", bound=LayoutPayloadBase)  # Payload must be a LayoutPayloadBase

class LayoutStrategyBase(Protocol[P]): # type: ignore
    """
    Protocol defining a layout strategy callable.
    
    A layout strategy takes a parent widget and a payload, then returns a QWidget
    containing the arranged content.
    """
    def layout(self, payload: P, *args: Any, **kwargs: Any) -> QWidget:
        """
        Build and return a QWidget containing the payload's widgets arranged in a layout.
        
        The strategy should:
        1. Create a container widget (QWidget, QGroupBox, QFrame, etc.)
        2. Create and set a layout on that widget
        3. Add the payload's widgets (accessed via dataclass fields or registered_widgets) to the layout
        4. Return the container widget
        
        Args:
            payload: The payload (frozen dataclass extending BaseLayoutPayload)
        
        Returns:
            A QWidget containing the arranged payload widgets
            
        Example:
            ```python
            def my_layout_strategy(payload: MyPayload) -> QWidget:
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