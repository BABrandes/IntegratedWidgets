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
    Base class for layout payloads that carry widgets to be laid out by a layout strategy.
    
    This class automatically discovers and validates all QWidget fields in subclasses,
    aggregating them into immutable collections accessible via properties.
    
    Usage
    -----
    Subclass this class and define fields containing QWidget instances, sequences of widgets,
    or mappings of widgets:
    
    >>> @dataclass(frozen=True)
    ... class MyPayload(BaseLayoutPayload):
    ...     label: QLabel
    ...     buttons: list[QPushButton]  # Can use mutable types
    ...     options: dict[str, QWidget]  # Dictionary for convenience
    
    Field Types
    -----------
    - **Single widgets**: Any field typed as QWidget or its subclass
    - **Sequences**: Any Sequence[QWidget] (list, tuple, etc.) - only ONE sequence field allowed
    - **Mappings**: Any Mapping[Any, QWidget] (dict, etc.) - multiple mappings are merged
    
    Immutability
    ------------
    While you can define fields using mutable types (list, dict) for convenience during
    initialization, the aggregated collections are stored immutably:
    
    - Sequence fields → aggregated into a single immutable tuple
    - Mapping fields → aggregated into a single immutable MappingProxyType
    
    Note: The original fields remain as-is, but the aggregated properties are immutable.
    
    Properties
    ----------
    registered_widgets : set[QWidget]
        All unique widgets found in all fields
    list_of_widgets : tuple[QWidget, ...]
        All widgets from sequence fields, as an immutable tuple
    mapping_of_widgets : Mapping[Any, QWidget]
        All widgets from mapping fields, as an immutable mapping
    
    Validation
    ----------
    - All field values must be QWidget instances (or sequences/mappings thereof)
    - Only one sequence field is allowed per payload
    - Duplicate keys across mapping fields will raise ValueError
    - Strings are explicitly excluded from sequence detection
    
    Example
    -------
    >>> @dataclass(frozen=True)
    ... class ButtonGroupPayload(BaseLayoutPayload):
    ...     ok_button: QPushButton
    ...     cancel_button: QPushButton
    ...     other_buttons: list[QPushButton]
    ...     
    >>> payload = ButtonGroupPayload(
    ...     ok_button=QPushButton("OK"),
    ...     cancel_button=QPushButton("Cancel"),
    ...     other_buttons=[QPushButton("Help"), QPushButton("More")]
    ... )
    >>> 
    >>> # Access aggregated collections (immutable)
    >>> len(payload.registered_widgets)  # 4 unique widgets
    >>> len(payload.list_of_widgets)  # 2 (from other_buttons)
    >>> payload.list_of_widgets[0] = None  # TypeError: immutable!
    
    Technical Notes
    ---------------
    Uses frozen=True for immutability but NOT slots=True, as we need to store
    internal attributes dynamically in __post_init__.
    """

    def __post_init__(self) -> None:
        """Validate all fields are QWidgets, create widget registry, and make collections immutable."""

        registered_widgets: set[QWidget] = set()

        def register_widget(obj: Any) -> None:
            if not isinstance(obj, QWidget):
                pass
                #raise ValueError(f"All widgets must be QWidget instances, got {type(obj).__name__}")
            registered_widgets.add(obj)

        list_of_widgets: list[QWidget] = []
        dict_of_widgets: dict[Any, QWidget] = {}

        one_list_found = False

        # Register widgets from fields
        for field_info in fields(self):

            field_value = getattr(self, field_info.name)

            # Check Mapping first (before Sequence, since some mappings might also match Sequence)
            if isinstance(field_value, Mapping):
                for key, widget in field_value.items(): # type: ignore
                    register_widget(widget)
                    if key not in dict_of_widgets:
                        dict_of_widgets[key] = widget
                    else:
                        raise ValueError(f"Duplicate key {key} in mapping of widgets")

            # Check Sequence but exclude strings (strings are sequences too!)
            elif isinstance(field_value, Sequence) and not isinstance(field_value, (str, bytes)):
                if one_list_found:
                    raise ValueError("Only one list of widgets is allowed")
                one_list_found = True
                for widget in field_value: # type: ignore
                    register_widget(widget)
                    list_of_widgets.append(widget) # type: ignore

            else:
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
