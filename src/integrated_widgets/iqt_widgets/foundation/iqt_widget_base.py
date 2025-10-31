"""
Flexible container widget that applies layout strategies to organize content dynamically.

This module provides IQtWidgetBase, a container that separates layout logic from
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
The IQtWidgetBase uses the Strategy pattern for layouts:

```
IQtWidgetBase (QWidget)
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
Leverages Qt's automatic cleanup - when the IQtWidgetBase is destroyed,
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
container = IQtWidgetBase(payload, vertical_layout)
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
container = IQtWidgetBase(payload)  # No layout yet
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
container = IQtWidgetBase(payload, strategy)
```

Thread Safety
------------
IQtWidgetBase is not thread-safe. All operations must occur on the
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
- IQtControllerWidgetBase: Adds controller lifecycle management
- LayoutStrategyBase: Protocol defining strategy signature
"""

from typing import Optional, TypeVar, Generic, Any
from logging import Logger

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy

from ...controllers.core.base_controller import BaseController
from .layout_payload_base import LayoutPayloadBase
from .layout_strategy_base import LayoutStrategyBase

P = TypeVar("P", bound=LayoutPayloadBase)  # Payload must be a LayoutPayloadBase

class IQtWidgetBase(QWidget, Generic[P]):
    """
    A container widget that applies a layout strategy to organize content dynamically.

    This widget implements the Strategy design pattern for Qt layouts, allowing you
    to swap layout algorithms at runtime without recreating widgets. It manages a
    payload of widgets and applies different layout strategies to arrange them.

    This is the base class for all integrated Qt widgets in the foundation module.

    **Key Capabilities:**
    - Dynamic layout switching at runtime
    - Safe widget management (widgets are re-parented, never deleted)
    - Separation of layout logic from widget creation
    - Type-safe payload handling via generics
    - Deferred layout creation (optional)
    - Layout refresh without strategy changes
    - Strategy status checking
    - Visual placeholder when no strategy is configured

    **Architecture:**
    The widget maintains a stable host layout (QVBoxLayout) that contains either
    the current content widget returned by the layout strategy, or a placeholder
    label when no strategy is set. When strategies change, the old content widget
    is removed, payload widgets are un-parented to prevent deletion, and a new
    content widget is created and inserted.

    This base class provides the foundation for controller-aware widgets that
    automatically manage the lifecycle of controllers and their associated Qt resources.

    **Lifecycle:**
    1. Creation: Payload and optional strategy provided
    2. Placeholder: If no strategy set, displays "Layout strategy missing!" message
    3. Active: Strategy arranges payload widgets for display
    4. Layout Changes: Old layout removed, widgets re-parented, new layout applied
    5. Refresh: Current strategy reapplied with optional parameters
    6. Destruction: Qt's parent-child system handles cleanup automatically

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
    Basic usage with layout strategy:

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
    >>> container = IQtWidgetBase(payload, my_layout)
    >>> container.show()

    Deferred layout creation (shows placeholder initially):

    >>> container = IQtWidgetBase(payload)  # Shows "Layout strategy missing!" placeholder
    >>> container.has_layout_strategy()  # False
    >>> container.set_layout_strategy(my_layout)  # Placeholder replaced with actual layout
    >>> container.has_layout_strategy()  # True

    Dynamic layout switching:

    >>> def horizontal_layout(parent, payload):
    ...     widget = QWidget()
    ...     layout = QHBoxLayout(widget)
    ...     layout.addWidget(payload.button)
    ...     layout.addWidget(payload.label)
    ...     return widget
    >>>
    >>> container.set_layout_strategy(horizontal_layout)  # Switches layout

    Layout refresh with parameters:

    >>> def responsive_layout(parent, payload, compact=False):
    ...     widget = QWidget()
    ...     layout = QVBoxLayout(widget) if not compact else QHBoxLayout(widget)
    ...     layout.addWidget(payload.button)
    ...     layout.addWidget(payload.label)
    ...     return widget
    >>>
    >>> container.set_layout_strategy(responsive_layout)
    >>> container.refresh_layout(compact=True)  # Reapplies with compact=True
    
    Notes
    -----
    - Payload must be a frozen dataclass (immutability is enforced)
    - Strategies should not modify or store references to payload widgets
    - Layout switching is fast - widgets are re-parented, not recreated
    - When no strategy is set, displays a "Layout strategy missing!" placeholder
    - Use has_layout_strategy() to check if a strategy is configured
    - Use refresh_layout() to reapply the current strategy without changing it
    - All operations must occur on the Qt GUI thread

    See Also
    --------
    LayoutPayloadBase : Base class for creating payloads
    LayoutStrategyBase : Protocol defining the strategy callable signature
    IQtControllerWidgetBase : Class adding controller lifecycle management
    has_layout_strategy : Check if a layout strategy is configured
    refresh_layout : Reapply the current layout strategy
    set_layout_strategy : Set or change the layout strategy
    """

    def __init__(
        self,
        payload: P,
        layout_strategy: Optional[LayoutStrategyBase[P]] = None,
        *,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
        **layout_strategy_kwargs: Any
        ) -> None:

        # Initialize using super() to respect MRO with multiple inheritance
        # IQtWidgetBase inherits from both CanBePayloadQObject and QWidget
        QWidget.__init__(self, parent)

        self._logger = logger
        self._strategy: Optional[LayoutStrategyBase[P]] = layout_strategy
        self._payload: P = payload

        self._host_layout = QVBoxLayout(self) # Stable host; we swap content within it
        self._host_layout.setContentsMargins(0, 0, 0, 0)
        self._host_layout.setSpacing(0)

        self._content_root: QWidget | None = None  # Content widget returned by strategy
        self._placeholder: QWidget | None = None   # Persistent geometry holder during rebuilds

        # Always call _build() - it will show a placeholder if no strategy is set
        self._build(**layout_strategy_kwargs)

    ###########################################################################
    # Internal methods
    ###########################################################################

    def _disable_layout_updates(self) -> None:
        """
        Disable widget updates on this widget and its parent to prevent flicker
        and layout rearrangement during rebuild.
        """
        self.setUpdatesEnabled(False)
        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            parent_widget.setUpdatesEnabled(False)

    def _restore_layout_updates(self) -> None:
        """
        Re-enable widget updates and force layout/repaint to ensure correct display.
        """
        self.setUpdatesEnabled(True)
        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            parent_widget.setUpdatesEnabled(True)
        
        # Force layout update and repaint to ensure correct display
        self.updateGeometry()
        self.update()


    def _rebuild(self, **layout_strategy_kwargs: Any) -> None:
        # Mark all controllers that are affected by the rebuild
        affected_controllers: set[BaseController[Any, Any]] = set()
        for controlled_widget in self._payload.registered_controlled_widgets:
            affected_controllers.add(controlled_widget.controller)
        for controller in self._payload.registered_controllers:
            affected_controllers.add(controller)
        for controller in affected_controllers:
            controller.relayouting_is_starting()

        try:
            # Prevent parent layout from stealing our space mid-rebuild
            self._freeze_geometry()

            # Clear current host and install a geometry-holding placeholder
            self._clear_host()

            # Build new layout or placeholder message in-place
            self._build(**layout_strategy_kwargs)

            # Activate and repaint once at the end
            self._host_layout.activate()
            self.updateGeometry()
            self.update()

        finally:
            # Release size lock and trigger outer layout settle
            self._unfreeze_geometry()

            for controller in affected_controllers:
                controller.relayouting_has_ended()
            affected_controllers.clear()

    # _create_size_placeholder is no longer needed

    def _freeze_geometry(self) -> None:
        """
        Lock this widget's size so its parent layout doesn't try to reclaim space
        while we are rebuilding.
        """
        s = self.size()

        # Hard lock current size
        self.setMinimumSize(s)
        self.setMaximumSize(s)

        # Optional: also disable updates to avoid partial repaint states
        self.setUpdatesEnabled(False)

        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            parent_widget.setUpdatesEnabled(False)


    def _unfreeze_geometry(self) -> None:
        """
        Unlock the widget's size and trigger a final relayout/repaint.
        """
        # Re-enable painting
        self.setUpdatesEnabled(True)
        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            parent_widget.setUpdatesEnabled(True)

        # Release the artificial size lock
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)  # Qt "no max"

        # Restore a sane size policy (tweak if you use something else)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred
        )

        # Tell the parent layout to recompute once, now that we're stable
        self.updateGeometry()
        if parent_widget is not None:
            parent_layout = parent_widget.layout()
            if parent_layout is not None:
                parent_layout.activate()

        # final repaint
        self.update()
        if parent_widget is not None:
            parent_widget.update()

    def _build(self, **layout_strategy_kwargs: Any) -> None:
        # We assume _clear_host() has ensured there is a placeholder in _host_layout.
        placeholder = self._placeholder

        if self._strategy is None:
            # No strategy -> show message in placeholder. We do NOT remove the placeholder.
            # Just restyle it to look like the dashed message box.
            if placeholder is None:
                # Safety fallback (first build during __init__ before _clear_host() ever ran)
                placeholder = QWidget(self)
                self._host_layout.addWidget(placeholder, 1)
                self._placeholder = placeholder

            # Turn placeholder into a label-like appearance.
            # We keep it as QWidget, not QLabel, to avoid replacing the item in layout.
            placeholder.setMinimumSize(placeholder.size())
            placeholder.setMaximumSize(16777215, 16777215)
            placeholder.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
            placeholder.setStyleSheet(
                """
                QWidget {
                    color: #666;
                    font-style: italic;
                    padding: 20px;
                    border: 2px dashed #ccc;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                """
            )
            # Also inject an inner QLabel child to actually show the text.
            # We recreate a tiny layout inside the placeholder so text is visible.
            from PySide6.QtWidgets import QVBoxLayout, QLabel
            # Clear any existing layout/children in placeholder before adding message
            if placeholder.layout() is not None:
                # remove old items from that internal layout
                inner_layout = placeholder.layout()
                while inner_layout.count():
                    item = inner_layout.takeAt(0)
                    w = item.widget()
                    if w is not None:
                        w.deleteLater()
            else:
                inner_layout = QVBoxLayout(placeholder)
                inner_layout.setContentsMargins(0, 0, 0, 0)
                inner_layout.setSpacing(0)
            msg = QLabel("Layout strategy missing!", placeholder)
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("color: #666; font-style: italic;")
            inner_layout.addWidget(msg, 1)

            # No content_root, placeholder stays in layout
            self._content_root = None
            return

        # Strategy is defined -> build actual content widget.
        result = self._strategy(self._payload, **layout_strategy_kwargs)
        if not isinstance(result, QWidget):  # type: ignore
            raise TypeError(f"Strategy must return a QWidget, got {type(result).__name__}")

        # Replace placeholder with the real content.
        if placeholder is not None:
            # Insert the real widget at the same position as placeholder.
            index = self._host_layout.indexOf(placeholder)
            if index < 0:
                # no placeholder found (edge case: first-time init after __init__)
                self._host_layout.addWidget(result, 1)
            else:
                self._host_layout.insertWidget(index, result, 1)
                self._host_layout.removeWidget(placeholder)
                placeholder.setParent(None)
                placeholder.deleteLater()
            self._placeholder = None
        else:
            # No placeholder? (first-ever build in __init__) Just add normally
            self._host_layout.addWidget(result, 1)

        self._content_root = result
        result.show()

    def _clear_host(self) -> None:
        # First, un-parent all payload widgets to prevent them from being deleted
        payload_widgets = self._payload.registered_widgets
        for widget in payload_widgets:
            if widget is not None:
                try:
                    widget.setParent(None)
                except RuntimeError:
                    pass

        # Capture reference size from current content_root (if any) BEFORE we delete it
        ref_size = None
        if self._content_root is not None:
            try:
                ref_size = self._content_root.size()
            except RuntimeError:
                ref_size = None

        # Wipe host_layout completely
        while self._host_layout.count():
            item = self._host_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        # Create / update persistent placeholder to hold geometry during rebuild
        placeholder = QWidget(self)
        if ref_size is None:
            ref_size = self.size()
        placeholder.setMinimumSize(ref_size)
        placeholder.setMaximumSize(ref_size)
        placeholder.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        # We don't style it here. Styling is handled later in _build() if needed.

        self._placeholder = placeholder
        self._host_layout.addWidget(placeholder, 1)
        placeholder.show()

        # content_root is now gone
        self._content_root = None

    ###########################################################################
    # Public API
    ###########################################################################

    def has_layout_strategy(self) -> bool:
        """
        Check if a layout strategy has been set for this widget.

        Returns True if a layout strategy is currently configured, False otherwise.
        This is useful for determining whether refresh_layout() can be called safely.

        Returns
        -------
        bool
            True if a layout strategy is set, False otherwise

        Examples
        --------
        Check before refreshing:

        >>> container = IQtWidgetBase(payload)  # No strategy initially
        >>> container.has_layout_strategy()  # False
        >>> container.set_layout_strategy(my_layout)
        >>> container.has_layout_strategy()  # True
        >>> container.refresh_layout()  # Safe to call

        Conditional operations:

        >>> if container.has_layout_strategy():
        ...     container.refresh_layout()
        ... else:
        ...     container.set_layout_strategy(default_layout)

        Notes
        -----
        - Returns False immediately after construction if no strategy was provided
        - Returns True after calling set_layout_strategy()
        - Thread-safe to call from any thread (read-only operation)

        See Also
        --------
        set_layout_strategy : Set a layout strategy
        refresh_layout : Reapply the current layout strategy
        """
        return self._strategy is not None

    def refresh_layout(self, **layout_strategy_kwargs: Any) -> None:
        """
        Reapply the current layout strategy to refresh the widget arrangement.

        This method rebuilds the current layout using the same strategy that was
        previously set. It's useful when you want to update the layout without
        changing the strategy itself, such as when widget properties change or
        when you need to refresh the arrangement.

        **Process:**
        1. Old content widget is removed from the host layout
        2. All payload widgets are explicitly un-parented (prevents deletion)
        3. Old content widget is scheduled for deletion (deleteLater)
        4. Current strategy is called again to recreate the arrangement
        5. New content widget is added to the host layout

        **Requirements:**
        - A layout strategy must already be set via set_layout_strategy() or __init__
        - Must be called on the Qt GUI thread

        Parameters
        ----------
        **layout_strategy_kwargs : Any
            Optional keyword arguments passed to the layout strategy. These can
            be used to customize the layout behavior on each refresh.

        Raises
        ------
        RuntimeError
            If no layout strategy has been set yet

        Examples
        --------
        Basic refresh:

        >>> container = IQtWidgetBase(payload, my_layout)
        >>> # ... widget properties change ...
        >>> container.refresh_layout()  # Reapply current layout

        Refresh with custom parameters:

        >>> def responsive_layout(parent, payload, compact=False):
        ...     # Layout adjusts based on compact parameter
        ...     pass
        >>>
        >>> container.set_layout_strategy(responsive_layout)
        >>> container.refresh_layout(compact=True)  # Refresh with new params

        Refresh after widget property changes:

        >>> # Change widget properties that affect layout
        >>> payload.button.setText("New Button Text")
        >>> container.refresh_layout()  # Layout adjusts to new text

        Notes
        -----
        - Does nothing if no layout strategy is currently set
        - Safe to call multiple times
        - Payload widgets are never deleted, only re-parented
        - Operation is synchronous on the GUI thread

        See Also
        --------
        set_layout_strategy : Set or change the layout strategy
        """
        if self._strategy is None:
            raise RuntimeError(
                "Cannot refresh layout: no layout strategy has been set. "
                "Call set_layout_strategy() first."
            )
        self._rebuild(**layout_strategy_kwargs)

    def set_layout_strategy(self, layout_strategy: LayoutStrategyBase[P], **layout_strategy_kwargs: Any) -> None:
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
        layout_strategy : LayoutStrategyBase[P]
            A callable taking (parent: QWidget, payload: P) and returning a QWidget
            with the payload's widgets arranged in a layout.
        
        Raises
        ------
        TypeError
            If the strategy doesn't return a QWidget
        
        Examples
        --------
        Switch from vertical to horizontal layout:

        >>> container = IQtWidgetBase(payload, vertical_layout)
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
        self._rebuild(**layout_strategy_kwargs)

    def update_layout_strategy_kwargs(self, **layout_strategy_kwargs: Any) -> None:
        """
        Update the keyword arguments for the current layout strategy.

        This method is useful when you want to update the keyword arguments for the current layout strategy
        without changing the strategy itself. This is useful when you want to update the layout strategy
        with new keyword arguments, such as when widget properties change.

        Parameters
        ----------
        **layout_strategy_kwargs : Any
            Optional keyword arguments passed to the layout strategy. These can
            be used to customize the layout behavior on each refresh.

        Raises
        ------
        RuntimeError
            If no layout strategy has been set yet
        """
        if self._strategy is None:
            raise RuntimeError(
                "Cannot update layout strategy kwargs: no layout strategy has been set. "
                "Call set_layout_strategy() first."
            )
        self._rebuild(**layout_strategy_kwargs)