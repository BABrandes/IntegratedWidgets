"""
Protocol and base class for layout payloads.

A payload is any object that provides widgets to be laid out by a layout strategy.
"""

from dataclasses import dataclass, fields

from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class BaseLayoutPayload():
    """
    Base class for layout payloads. It carries the widgets to be laid out by the layout strategy.
    
    Note: Uses frozen=True for immutability but NOT slots=True, as we need to store
    the _registered_widgets set dynamically in __post_init__.
    """

    def __post_init__(self) -> None:
        """Validate all fields are QWidgets and create widget registry."""
        # Use object.__setattr__ to bypass frozen restriction
        registered_widgets: set[QWidget] = set()
        
        for field_info in fields(self):
            field_value = getattr(self, field_info.name)
            if not isinstance(field_value, QWidget):
                raise ValueError(f"Field {field_info.name} must be a QWidget, got {type(field_value).__name__}")
            registered_widgets.add(field_value)
        
        object.__setattr__(self, "_registered_widgets", registered_widgets)

    @property
    def registered_widgets(self) -> set[QWidget]:
        """
        Return all registered widgets.
        """
        return self._registered_widgets  # type: ignore

        