"""
Flexible container widget that applies layout strategies to organize content dynamically.

This module provides IQtLayoutedWidget, a container that separates layout logic from
content. It enables dynamic layout switching at runtime while safely managing widget
lifecycles and preventing accidental widget deletion.

Key Features
-----------
- **Separation of Concerns**: Layout logic is independent of widget creation
- **Dynamic Layout Switching**: Change arrangements at runtime without recreating widgets
- **Safe Widget Management**: Widgets are re-parented, never deleted during layout changes
- **Reusable Strategies**: Same layout functions work with different widget sets
- **Deferred Layout**: Optionally create widget without layout, add it later
- **Type Safety**: Generic types ensure payload and strategy compatibility

Architecture
-----------
The IQtLayoutedWidget uses the Strategy pattern for layouts:

```
IQtLayoutedWidget (QWidget)
│
├─ _payload: BaseLayoutPayload
│  └─ Frozen dataclass with QWidget fields
│  
├─ _strategy: LayoutStrategy[P]
│  └─ Callable: (parent, payload) -> QWidget
│
├─ _host_layout: QVBoxLayout
│  └─ Stable container for swapping content
│
└─ _content_root: QWidget | None
   └─ Widget returned by strategy (current layout)
```

Design Principles
----------------

**1. Immutable Payload**
Payloads must be frozen dataclasses to prevent modification. This ensures
widgets remain stable references that strategies can rely on.

**2. Safe Re-parenting**
When changing layouts, widgets are explicitly un-parented before deleting
the old container, preventing Qt from cascading the deletion.

**3. Strategy Flexibility**
Strategies are simple callables, not classes. This makes them lightweight,
reusable, and easy to test.

**4. Qt Parent-Child Relationships**
Leverages Qt's automatic cleanup - when the IQtLayoutedWidget is destroyed,
Qt handles all child widget cleanup automatically.

Example Usage
------------

Basic vertical layout:

```python
from dataclasses import dataclass
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel

@dataclass(frozen=True)
class MyPayload(BaseLayoutPayload):
    button: QPushButton
    label: QLabel

def vertical_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.button)
    layout.addWidget(payload.label)
    return widget

payload = MyPayload(
    button=QPushButton("Click"),
    label=QLabel("Status")
)
container = IQtLayoutedWidget(payload, vertical_layout)
container.show()
```

Dynamic layout switching:

```python
def horizontal_layout(parent, payload):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(payload.button)
    layout.addWidget(payload.label)
    return widget

# Switch layouts at runtime
container.set_layout_strategy(horizontal_layout)  # Widgets safely re-arranged
```

Grouped layout with styling:

```python
def grouped_layout(parent, payload):
    group = QGroupBox("Controls")
    layout = QVBoxLayout(group)
    layout.addWidget(payload.button)
    layout.addWidget(payload.label)
    group.setStyleSheet("QGroupBox { font-weight: bold; }")
    return group

container.set_layout_strategy(grouped_layout)
```

Deferred layout creation:

```python
# Create widget without layout
container = IQtLayoutedWidget(payload)  # No layout yet
# ... later ...
container.set_layout_strategy(vertical_layout)  # Now apply layout
```

Layout Strategy Guidelines
-------------------------

A layout strategy must:
1. Accept two parameters: (parent: QWidget, payload: P)
2. Return a QWidget containing the arranged payload widgets
3. Not delete or store references to payload widgets
4. Be idempotent - multiple calls with same payload should work

Example strategy:

```python
def my_strategy(parent: QWidget, payload: MyPayload) -> QWidget:
    # 1. Create container
    container = QWidget()
    
    # 2. Create and set layout
    layout = QVBoxLayout(container)
    
    # 3. Add payload widgets
    layout.addWidget(payload.button)
    layout.addWidget(payload.label)
    
    # 4. Optional: customize
    layout.setSpacing(10)
    container.setStyleSheet("background: white;")
    
    # 5. Return container
    return container
```

Common Patterns
--------------

**Conditional layouts based on state:**
```python
def adaptive_layout(parent, payload):
    if parent.width() < 400:
        return mobile_layout(parent, payload)
    else:
        return desktop_layout(parent, payload)
```

**Reusable layout factories:**
```python
def make_form_layout(label_width: int):
    def form_strategy(parent, payload):
        # Use label_width in layout
        ...
    return form_strategy

strategy = make_form_layout(100)
container = IQtLayoutedWidget(payload, strategy)
```

Thread Safety
------------
IQtLayoutedWidget is not thread-safe. All operations must occur on the
Qt GUI thread. Use Qt's signal-slot mechanism or QMetaObject.invokeMethod
for cross-thread communication.

Performance Considerations
-------------------------
- Layout switching is fast (widgets are re-parented, not recreated)
- Complex payloads with many widgets may have noticeable layout times
- Strategies are called synchronously on the GUI thread
- Consider caching strategy results if they're expensive to compute

See Also
--------
- BaseLayoutPayload: Base class for creating payloads
- IQtControlledLayoutedWidget: Adds controller lifecycle management
- LayoutStrategy: Protocol defining strategy signature
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
    A container widget that applies a layout strategy to organize content dynamically.
    
    This widget implements the Strategy design pattern for Qt layouts, allowing you
    to swap layout algorithms at runtime without recreating widgets. It manages a
    payload of widgets and applies different layout strategies to arrange them.
    
    **Key Capabilities:**
    - Dynamic layout switching at runtime
    - Safe widget management (widgets are re-parented, never deleted)
    - Separation of layout logic from widget creation
    - Type-safe payload handling via generics
    - Deferred layout creation (optional)
    
    **Architecture:**
    The widget maintains a stable host layout (QVBoxLayout) that contains the
    current content widget returned by the layout strategy. When strategies
    change, the old content widget is removed, payload widgets are un-parented
    to prevent deletion, and a new content widget is created and inserted.
    
    **Lifecycle:**
    1. Creation: Payload and optional strategy provided
    2. Active: Strategy arranges payload widgets for display
    3. Layout Changes: Old layout removed, widgets re-parented, new layout applied
    4. Destruction: Qt's parent-child system handles cleanup automatically
    
    **Type Safety:**
    The generic type parameter P ensures that the payload type matches the
    strategy's expected type at compile time (when using type checkers).
    
    Type Parameters
    --------------
    P : BaseLayoutPayload
        The type of payload (must be a frozen dataclass extending BaseLayoutPayload)
    
    Parameters
    ----------
    payload : P
        A frozen dataclass containing the widgets to be laid out. All fields must
        be QWidget instances. The payload is immutable to ensure widget references
        remain stable across layout changes.
    
    layout_strategy : Optional[LayoutStrategy[P]]
        A callable taking (parent: QWidget, payload: P) and returning a QWidget
        with the arranged payload widgets. If None, the widget is empty until
        set_layout_strategy() is called.
    
    parent : Optional[QWidget]
        The parent widget for Qt's parent-child hierarchy
    
    Attributes
    ----------
    _payload : P
        The immutable payload containing widgets
    _strategy : Optional[LayoutStrategy[P]]
        The current layout strategy
    _host_layout : QVBoxLayout
        Stable container for swapping content
    _content_root : QWidget | None
        Current widget returned by the strategy
    
    Examples
    --------
    Basic usage:
    
    >>> @dataclass(frozen=True)
    ... class MyPayload(BaseLayoutPayload):
    ...     button: QPushButton
    ...     label: QLabel
    >>> 
    >>> def my_layout(parent, payload):
    ...     widget = QWidget()
    ...     layout = QVBoxLayout(widget)
    ...     layout.addWidget(payload.button)
    ...     layout.addWidget(payload.label)
    ...     return widget
    >>> 
    >>> payload = MyPayload(QPushButton("OK"), QLabel("Status"))
    >>> container = IQtLayoutedWidget(payload, my_layout)
    >>> container.show()
    
    Dynamic layout switching:
    
    >>> def horizontal_layout(parent, payload):
    ...     widget = QWidget()
    ...     layout = QHBoxLayout(widget)
    ...     layout.addWidget(payload.button)
    ...     layout.addWidget(payload.label)
    ...     return widget
    >>> 
    >>> container.set_layout_strategy(horizontal_layout)  # Switches layout
    
    Deferred layout:
    
    >>> container = IQtLayoutedWidget(payload)  # No layout initially
    >>> # ... later ...
    >>> container.set_layout_strategy(my_layout)  # Apply layout now
    
    Notes
    -----
    - Payload must be a frozen dataclass (immutability is enforced)
    - Strategies should not modify or store references to payload widgets
    - Layout switching is fast - widgets are re-parented, not recreated
    - All operations must occur on the Qt GUI thread
    
    See Also
    --------
    BaseLayoutPayload : Base class for creating payloads
    LayoutStrategy : Protocol defining the strategy callable signature
    IQtControlledLayoutedWidget : Adds controller lifecycle management
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

        if not isinstance(result, QWidget): # type: ignore
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
            if widget is not None: # type: ignore
                try:
                    widget.setParent(None)  # Un-parent to prevent deletion
                except RuntimeError:
                    # Widget may already be deleted, ignore
                    pass
        
        # Now safe to delete the container widget
        while self._host_layout.count():
            item = self._host_layout.takeAt(0)
            w = item.widget()
            if w is not None: # type: ignore
                # This deletes the container widget returned by the strategy
                w.deleteLater()

        self._content_root = None

    ###########################################################################
    # Public API
    ###########################################################################

    def set_layout_strategy(self, layout_strategy: LayoutStrategy[P]) -> None:
        """
        Replace the current layout strategy and rebuild the widget.
        
        This method enables dynamic layout switching at runtime. The payload widgets
        are safely re-parented (not deleted) and arranged according to the new strategy.
        This is useful for responsive layouts, user preferences, or state-dependent
        arrangements.
        
        **Process:**
        1. Old content widget is removed from the host layout
        2. All payload widgets are explicitly un-parented (prevents deletion)
        3. Old content widget is scheduled for deletion (deleteLater)
        4. New strategy is called to create new arrangement
        5. New content widget is added to the host layout
        
        **Performance:**
        Layout switching is fast because widgets are re-used, not recreated.
        The strategy is called synchronously on the GUI thread.
        
        **Limitations:**
        - The payload itself cannot be changed; only the layout strategy
        - Strategies must work with the same payload type
        - Must be called on the Qt GUI thread
        
        Parameters
        ----------
        layout_strategy : LayoutStrategy[P]
            A callable taking (parent: QWidget, payload: P) and returning a QWidget
            with the payload's widgets arranged in a layout.
        
        Raises
        ------
        TypeError
            If the strategy doesn't return a QWidget
        
        Examples
        --------
        Switch from vertical to horizontal layout:
        
        >>> container = IQtLayoutedWidget(payload, vertical_layout)
        >>> container.show()
        >>> # ... later, user clicks "horizontal mode" ...
        >>> container.set_layout_strategy(horizontal_layout)
        
        Responsive layout based on window size:
        
        >>> def on_resize(event):
        ...     if container.width() < 600:
        ...         container.set_layout_strategy(mobile_layout)
        ...     else:
        ...         container.set_layout_strategy(desktop_layout)
        
        Apply grouped layout:
        
        >>> def grouped_layout(parent, payload):
        ...     group = QGroupBox("Settings")
        ...     layout = QVBoxLayout(group)
        ...     for widget in payload.registered_widgets:
        ...         layout.addWidget(widget)
        ...     return group
        >>> 
        >>> container.set_layout_strategy(grouped_layout)
        
        Notes
        -----
        - Safe to call multiple times
        - Old content widget is deleted via deleteLater() (deferred deletion)
        - Payload widgets are never deleted, only re-parented
        - Strategy is called immediately (synchronous operation)
        
        See Also
        --------
        _rebuild : Internal method that performs the rebuild
        _clear_host : Internal method that cleans up old layout
        _build : Internal method that applies new layout
        """
        
        self._strategy = layout_strategy
        self._rebuild()