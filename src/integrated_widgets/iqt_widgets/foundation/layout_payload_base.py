"""
Protocol and base class for layout payloads.

A payload is any object that provides widgets to be laid out by a layout strategy.
"""

from typing import Any, Sequence, Mapping
from types import MappingProxyType
from dataclasses import dataclass, fields

from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class LayoutPayloadBase():
    """
    Base class for layout payloads that carry widgets and metadata to be used by layout strategies.
    
    This class automatically discovers all QWidget fields in subclasses, aggregating them 
    into immutable collections accessible via properties. Non-widget fields (such as strings, 
    numbers, or configuration data) are allowed and will be ignored during widget discovery.
    
    Usage
    -----
    Subclass this class and define fields containing QWidget instances, sequences of widgets,
    mappings of widgets, or any other data you need:
    
    >>> @dataclass(frozen=True)
    ... class MyPayload(LayoutPayloadBase):
    ...     label: QLabel
    ...     buttons: list[QPushButton]  # Can use mutable types
    ...     options: dict[str, QWidget]  # Dictionary for convenience
    ...     title: str  # Non-widget fields are allowed
    ...     max_items: int  # Configuration data
    
    Field Types
    -----------
    - **Widget fields**: Any field containing a QWidget or its subclass - will be registered
    - **Sequence fields**: Any Sequence containing items (only QWidgets are registered) - only ONE sequence field allowed
    - **Mapping fields**: Any Mapping containing items (only QWidget values are registered) - multiple mappings are merged
    - **Other fields**: Any non-widget data (strings, numbers, etc.) - will be ignored during widget discovery
    
    Immutability
    ------------
    While you can define fields using mutable types (list, dict) for convenience during
    initialization, the aggregated widget collections are stored immutably:
    
    - Sequence fields → aggregated into a single immutable tuple
    - Mapping fields → aggregated into a single immutable MappingProxyType
    
    Note: The original fields remain as-is, but the aggregated properties are immutable.
    
    Properties
    ----------
    registered_widgets : set[QWidget]
        All unique QWidget instances found in all fields
    list_of_widgets : tuple[QWidget, ...]
        All widgets from sequence fields, as an immutable tuple
    mapping_of_widgets : Mapping[Any, QWidget]
        All widgets from mapping fields, as an immutable mapping
    
    Validation
    ----------
    - Only one sequence field is allowed per payload
    - Duplicate keys across mapping fields will raise ValueError
    - Strings and bytes are explicitly excluded from sequence detection
    - Non-QWidget items in sequences and mappings are silently ignored
    
    Example
    -------
    >>> @dataclass(frozen=True)
    ... class ButtonGroupPayload(LayoutPayloadBase):
    ...     title: str  # Metadata
    ...     ok_button: QPushButton
    ...     cancel_button: QPushButton
    ...     other_buttons: list[QPushButton]
    ...     max_buttons: int = 5  # Configuration
    ...     
    >>> payload = ButtonGroupPayload(
    ...     title="Actions",
    ...     ok_button=QPushButton("OK"),
    ...     cancel_button=QPushButton("Cancel"),
    ...     other_buttons=[QPushButton("Help"), QPushButton("More")]
    ... )
    >>> 
    >>> # Access widget collections (immutable)
    >>> len(payload.registered_widgets)  # 4 unique widgets
    >>> len(payload.list_of_widgets)  # 2 (from other_buttons)
    >>> payload.list_of_widgets[0] = None  # TypeError: immutable!
    >>> 
    >>> # Access metadata directly
    >>> payload.title  # "Actions"
    >>> payload.max_buttons  # 5
    
    Technical Notes
    ---------------
    Uses frozen=True for immutability but NOT slots=True, as we need to store
    internal attributes dynamically in __post_init__.
    """

    def __post_init__(self) -> None:
        """Discover QWidget fields, create widget registry, and make collections immutable."""

        registered_widgets: set[QWidget] = set()

        def register_widget(obj: Any) -> None:
            """Register object only if it's a QWidget."""
            if isinstance(obj, QWidget):
                registered_widgets.add(obj)

        list_of_widgets: list[QWidget] = []
        dict_of_widgets: dict[Any, QWidget] = {}

        one_list_found = False

        # Discover widgets from fields
        for field_info in fields(self):

            field_value = getattr(self, field_info.name)

            # Check Mapping first (before Sequence, since some mappings might also match Sequence)
            if isinstance(field_value, Mapping):
                for key, value in field_value.items(): # type: ignore
                    if isinstance(value, QWidget):
                        register_widget(value)
                        if key not in dict_of_widgets:
                            dict_of_widgets[key] = value
                        else:
                            raise ValueError(f"Duplicate key {key} in mapping of widgets")

            # Check Sequence but exclude strings (strings are sequences too!)
            elif isinstance(field_value, Sequence) and not isinstance(field_value, (str, bytes)):
                if one_list_found:
                    raise ValueError("Only one sequence field is allowed")
                one_list_found = True
                for item in field_value: # type: ignore
                    if isinstance(item, QWidget):
                        register_widget(item)
                        list_of_widgets.append(item) # type: ignore

            # Single field - register only if it's a QWidget
            elif isinstance(field_value, QWidget):
                register_widget(field_value)

        object.__setattr__(self, "_registered_widgets", registered_widgets)
        object.__setattr__(self, "_list_of_widgets", tuple(list_of_widgets))
        object.__setattr__(self, "_mapping_of_widgets", MappingProxyType(dict_of_widgets))

    @property
    def registered_widgets(self) -> set[QWidget]:
        """
        Return all registered widgets.
        """
        return self._registered_widgets  # type: ignore

    @property
    def list_of_widgets(self) -> tuple[QWidget, ...]:
        """
        Return all list of widgets as an immutable tuple.
        """
        return self._list_of_widgets  # type: ignore

    @property
    def mapping_of_widgets(self) -> Mapping[Any, QWidget]:
        """
        Return all mapping of widgets as an immutable mapping.
        """
        return self._mapping_of_widgets  # type: ignore
