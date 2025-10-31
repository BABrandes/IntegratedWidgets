"""
Protocol and base class for layout payloads.

A payload is any object that provides widgets to be laid out by a layout strategy.
"""

from typing import Any, Sequence, Mapping
from types import MappingProxyType
from dataclasses import dataclass, fields

from PySide6.QtWidgets import QWidget

from integrated_widgets.controlled_widgets.base_controlled_widget import BaseControlledWidget
from integrated_widgets.controllers.core.base_controller import BaseController


@dataclass(frozen=True)
class LayoutPayloadBase():
    """
    Base class for layout payloads that carry widgets and metadata to be used by layout strategies.
    
    This class automatically discovers all QWidget and BaseControlledWidget fields in subclasses,
    aggregating them into immutable collections accessible via properties. Non-widget fields 
    (such as strings, numbers, or configuration data) are allowed and will be ignored during discovery.
    
    Usage
    -----
    Subclass this class and define fields containing QWidget or BaseControlledWidget instances,
    sequences of widgets, mappings of widgets, or any other data you need:
    
    >>> @dataclass(frozen=True)
    ... class MyPayload(LayoutPayloadBase):
    ...     label: QLabel
    ...     buttons: list[QPushButton]  # Can use mutable types
    ...     controlled_widget: ControlledLineEdit  # BaseControlledWidget instance
    ...     options: dict[str, QWidget]  # Dictionary for convenience
    ...     title: str  # Non-widget fields are allowed
    ...     max_items: int  # Configuration data
    
    Field Types
    -----------
    - **Widget fields**: Any field containing a QWidget or its subclass - will be registered
    - **Controlled widget fields**: Any field containing a BaseControlledWidget - will be registered in controlled_widgets collection
    - **Sequence fields**: Any Sequence containing items (QWidgets and BaseControlledWidgets are registered) - only ONE sequence field allowed
    - **Mapping fields**: Any Mapping containing items (only QWidget values are registered) - multiple mappings are merged
    - **Other fields**: Any non-widget data (strings, numbers, etc.) - will be ignored during discovery
    
    Immutability
    ------------
    While you can define fields using mutable types (list, dict) for convenience during
    initialization, the aggregated widget collections are stored immutably:
    
    - Sequence fields → aggregated into a single immutable tuple
    - Mapping fields → aggregated into a single immutable MappingProxyType
    
    Note: The original fields remain as-is, but the aggregated properties are immutable.
    
    Properties
    ----------
    registered_controlled_widgets : set[BaseControlledWidget]
        All unique BaseControlledWidget instances found in all fields (used for relayout signal suppression)
    registered_controllers : set[BaseController]
        All unique BaseController instances found in IQtControllerWidgetBase fields (used for relayout signal suppression)
    registered_widgets : set[QWidget]
        All unique QWidget instances found in all fields (for layout operations)
    list_of_widgets : tuple[QWidget, ...]
        All widgets from sequence fields, as an immutable tuple
    mapping_of_widgets : Mapping[Any, QWidget]
        All widgets from mapping fields, as an immutable mapping
    
    Validation
    ----------
    - Only one sequence field is allowed per payload
    - Duplicate keys across mapping fields will raise ValueError
    - Strings and bytes are explicitly excluded from sequence detection
    - Non-QWidget/BaseControlledWidget items in sequences and mappings are silently ignored
    
    Example
    -------
    >>> from PySide6.QtWidgets import QPushButton, QLabel
    >>> from integrated_widgets.controlled_widgets import ControlledLineEdit, ControlledCheckBox
    >>> 
    >>> @dataclass(frozen=True)
    ... class FormPayload(LayoutPayloadBase):
    ...     title: str  # Metadata
    ...     name_entry: ControlledLineEdit  # BaseControlledWidget (also a QWidget)
    ...     enabled_checkbox: ControlledCheckBox  # BaseControlledWidget (also a QWidget)
    ...     other_widgets: list[QPushButton]
    ...     max_items: int = 5  # Configuration
    ...     
    >>> payload = FormPayload(
    ...     title="User Form",
    ...     name_entry=some_controlled_line_edit,
    ...     enabled_checkbox=some_controlled_checkbox,
    ...     other_widgets=[QPushButton("Help"), QPushButton("More")]
    ... )
    >>> 
    >>> # Access controlled widget collection (for relayout signal suppression)
    >>> len(payload.registered_controlled_widgets)  # 2 (name_entry + enabled_checkbox)
    >>> # Access controller collection (for nested controller widgets)
    >>> len(payload.registered_controllers)  # 0 (no IQtControllerWidgetBase in this example)
    >>> # Access widget collection (for layout operations)
    >>> len(payload.registered_widgets)  # 4 (name_entry + enabled_checkbox + 2 buttons)
    >>> len(payload.list_of_widgets)  # 2 (from other_widgets)
    >>> payload.list_of_widgets[0] = None  # TypeError: immutable!
    >>> 
    >>> # Access metadata directly
    >>> payload.title  # "User Form"
    >>> payload.max_items  # 5
    
    Technical Notes
    ---------------
    Uses frozen=True for immutability but NOT slots=True, as we need to store
    internal attributes dynamically in __post_init__.
    """

    def __post_init__(self) -> None:
        """Discover QWidget, BaseControlledWidget, and BaseController fields, create registries, and make collections immutable."""

        registered_controlled_widgets: set[BaseControlledWidget] = set()
        registered_controllers: set[BaseController[Any, Any]] = set()
        registered_widgets: set[QWidget] = set()

        def register_object(obj: Any) -> None:
            """Register object if it's a BaseControlledWidget, QWidget, or IQtControllerWidgetBase (extracts controller)."""
            # Check if it's an IQtControllerWidgetBase and extract its controller
            # Use getattr to safely check for _controller attribute without type errors
            controller = getattr(obj, '_controller', None)
            if isinstance(controller, BaseController):
                registered_controllers.add(controller)  # type: ignore[arg-type]
            
            if isinstance(obj, BaseControlledWidget):
                registered_controlled_widgets.add(obj)
            if isinstance(obj, QWidget):
                registered_widgets.add(obj)

        list_of_widgets: list[QWidget] = []
        dict_of_widgets: dict[Any, QWidget] = {}

        one_list_found = False

        # Discover objects from fields
        for field_info in fields(self):

            field_value = getattr(self, field_info.name)

            # Check Mapping first (before Sequence, since some mappings might also match Sequence)
            if isinstance(field_value, Mapping):
                for key, value in field_value.items(): # type: ignore
                    if isinstance(value, BaseControlledWidget):
                        register_object(value)
                        # For widget-specific collections, only add QWidgets
                    if isinstance(value, QWidget):
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
                    if isinstance(item, BaseControlledWidget):
                        register_object(item)
                        # For widget-specific collections, only add QWidgets
                    if isinstance(item, QWidget):
                        list_of_widgets.append(item) # type: ignore

            # Single field - register if it's a QWidget or BaseControlledWidget
            elif isinstance(field_value, (BaseControlledWidget, QWidget)):
                register_object(field_value)

        object.__setattr__(self, "_registered_controlled_widgets", registered_controlled_widgets)
        object.__setattr__(self, "_registered_controllers", registered_controllers)
        object.__setattr__(self, "_registered_widgets", registered_widgets)
        object.__setattr__(self, "_list_of_widgets", tuple(list_of_widgets))
        object.__setattr__(self, "_mapping_of_widgets", MappingProxyType(dict_of_widgets))

    @property
    def registered_controlled_widgets(self) -> set[BaseControlledWidget]:
        """
        Return all registered BaseControlledWidget instances.
        
        These are used during layout rebuilds to suppress userInputFinishedSignal
        emissions when widgets lose focus during the relayout process.
        """
        return self._registered_controlled_widgets  # type: ignore

    @property
    def registered_controllers(self) -> set[BaseController[Any, Any]]:
        """
        Return all registered BaseController instances found in IQtControllerWidgetBase fields.
        
        These are used during layout rebuilds to suppress signal emissions from the
        controller's controlled widgets when the controller widget is being relayouted.
        
        Controllers are automatically discovered when IQtControllerWidgetBase instances
        are present in payload fields.
        """
        return self._registered_controllers  # type: ignore

    @property
    def registered_widgets(self) -> set[QWidget]:
        """
        Return all registered QWidget instances.
        
        Used for safe un-parenting during layout rebuilds to prevent accidental deletion.
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
