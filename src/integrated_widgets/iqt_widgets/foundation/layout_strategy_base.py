from typing import Any, Protocol, TypeVar
from PySide6.QtWidgets import QWidget

from .layout_payload_base import LayoutPayloadBase

P = TypeVar("P", bound=LayoutPayloadBase)  # Payload must be a LayoutPayloadBase

class LayoutStrategyBase(Protocol[P]):  # type: ignore
    """
    Protocol defining a layout strategy callable for arranging widget payloads.

    A layout strategy is a simple callable that takes a payload containing widgets and returns
    a QWidget with those widgets arranged in a layout. Strategies are pure functions that
    can be reused across different widget instances.

    The strategy pattern allows widgets to change their visual arrangement at runtime
    without recreating the underlying widgets, enabling dynamic responsive layouts.
    """
    def __call__(self, payload: P, **layout_strategy_kwargs: Any) -> QWidget: # type: ignore
        """
        Build and return a QWidget containing the payload's widgets arranged in a layout.
        
        The strategy should:
        1. Create a container widget (QWidget, QGroupBox, QFrame, etc.)
        2. Create and set a layout on that widget
        3. Add the payload's widgets (accessed via dataclass fields or registered_widgets) to the layout
        4. Return the container widget
        
        Args:
            payload: The payload (frozen dataclass extending BaseLayoutPayload)
            layout_strategy_kwargs: Additional keyword arguments passed to the layout strategy
        
        Returns:
            A QWidget containing the arranged payload widgets
            
        Example:
            ```python
            def my_layout_strategy(payload: MyPayload, **layout_strategy_kwargs: Any) -> QWidget:
                # Create container
                widget = QWidget()
                layout = QVBoxLayout(widget)
                
                # Add payload's widgets to the layout
                layout.addWidget(payload.button1)
                layout.addWidget(payload.button2)
                layout.addWidget(payload.label)
                
                # Optional: customize the layout
                layout.setSpacing(10)
                widget.setStyleSheet("background: white;")
                
                return widget
            ```
        """
        ...