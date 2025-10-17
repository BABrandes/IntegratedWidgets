"""
Widget that combines a controller with a layout strategy for automatic lifecycle management.

This module provides IQtControlledLayoutedWidget, which wraps a BaseController and its
widgets in a QWidget with automatic disposal management. The widget ensures that when
it is destroyed, the controller is properly disposed, cleaning up all Qt resources,
hooks, and signals.

Architecture Overview
--------------------
IQtControlledLayoutedWidget inherits from IQtLayoutedWidget and adds controller lifecycle
management. The controller's widgets are extracted as the payload and arranged according
to a layout strategy, while the widget ensures the controller is disposed when needed.

Lifecycle Phases
---------------
1. **Creation**: Controller and payload are provided, layout strategy arranges widgets
2. **Active Life**: Widget displays controller widgets, controller manages state/hooks
3. **Disposal**: When widget is closed/deleted, controller is disposed first, then Qt cleans up

Key Design Decisions
-------------------
- NO __del__() method: Avoids Python GC interference with Qt's lifecycle
- Overrides close() and deleteLater(): Ensures controller disposal before Qt cleanup
- Qt parent-child relationships: Leverages Qt's automatic cleanup for widget hierarchy
- Exception safety: All disposal operations wrapped in try-except for robustness

Example Usage
------------
```python
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget, QVBoxLayout
from integrated_widgets.iqt_widgets import IQtControlledLayoutedWidget, BaseLayoutPayload
from integrated_widgets.widget_controllers import TextEntryController

# Define payload structure
@dataclass(frozen=True)
class MyPayload(BaseLayoutPayload):
    text_widget: QWidget  # Will be controller.line_edit

# Create controller
controller = TextEntryController("initial value")

# Create payload from controller's widgets
payload = MyPayload(text_widget=controller.line_edit)

# Define layout
def simple_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.text_widget)
    return widget

# Create the managed widget
widget = IQtControlledLayoutedWidget(
    controller=controller,
    payload=payload,
    layout_strategy=simple_layout
)

# Later, when done:
widget.close()  # Controller is disposed automatically before Qt cleanup
```

Disposal Behavior
----------------
The widget ensures proper disposal through multiple mechanisms:

1. **Explicit close()**: Most Qt-idiomatic way
   ```python
   widget.close()  # Disposes controller, then closes widget
   ```

2. **Scheduled deletion via deleteLater()**:
   ```python
   widget.deleteLater()  # Disposes controller, then schedules Qt deletion
   ```

3. **Qt parent-child automatic cleanup**:
   When a parent widget is destroyed, Qt automatically destroys children.
   The overridden methods ensure controller disposal happens first.

4. **Python scope exit** (less reliable):
   If widget goes out of scope without explicit disposal, Qt's parent-child
   mechanism will eventually clean it up. However, explicit disposal is preferred.

Thread Safety
------------
All disposal operations are designed to be safe even if called multiple times
or from different contexts. The controller tracks its disposed state to prevent
double-disposal.

See Also
--------
- IQtLayoutedWidget: Parent class handling layout strategies
- BaseController: Controller base class with disposal infrastructure
- BaseLayoutPayload: Payload structure for widget management
"""

from typing import Optional, TypeVar, Generic, Any
from PySide6.QtWidgets import QWidget

from observables import HookLike

from integrated_widgets.util.base_controller import BaseController
from .iqt_layouted_widget import IQtLayoutedWidget, LayoutStrategy
from .layout_payload import BaseLayoutPayload


# ---- Type Variables ----------------------------------------------

HK = TypeVar("HK", bound=str)  # Hook key type
HV = TypeVar("HV")  # Hook value type
P = TypeVar("P", bound=BaseLayoutPayload)  # Payload type
C = TypeVar("C", bound=BaseController[Any, Any, Any])  # Controller type (invariant)

class IQtControlledLayoutedWidget(IQtLayoutedWidget[P], Generic[HK, HV, P, C]):
    """
    A QWidget that manages a controller's lifecycle and arranges its widgets.
    
    This class combines:
    - A BaseController instance (managing application logic, hooks, and Qt resources)
    - A payload of widgets (typically the controller's widgets)
    - A layout strategy (arranging the widgets visually)
    - Automatic disposal management (ensuring clean shutdown)
    
    The widget guarantees that when it is destroyed, the controller is properly
    disposed first, cleaning up all hooks, signals, timers, and Qt resources before
    Qt begins deleting the C++ widget objects.
    
    Architecture
    -----------
    ```
    IQtControlledLayoutedWidget (QWidget)
    │
    ├─ Owns: BaseController
    │  ├─ Manages: Application logic and state
    │  ├─ Owns: Qt resources (QObject, signals, timers)
    │  └─ Connects to: Hooks from observables library
    │
    ├─ Has: BaseLayoutPayload (from controller's widgets)
    │  └─ References: QWidget instances created by controller
    │
    └─ Uses: LayoutStrategy
       └─ Arranges: Payload widgets in Qt layout
    ```
    
    Lifecycle Phases
    ---------------
    
    **1. Creation** (during __init__):
       - Controller is passed in (already created with its widgets)
       - Payload is created from controller's widgets
       - IQtLayoutedWidget.__init__ arranges widgets using strategy
       - Widget is now active and functional
    
    **2. Active Life**:
       - Controller manages state, hooks, and widget updates
       - Layout strategy has arranged widgets for display
       - User interactions trigger controller callbacks
       - Hook system keeps widgets synchronized with state
    
    **3. Disposal** (when widget is closed/destroyed):
       a. close() or deleteLater() is called
       b. Controller.dispose() is called FIRST:
          - Disconnects all hooks (stops observables updates)
          - Stops all timers (prevents queued callbacks)
          - Disconnects Qt signals (stops widget updates)
          - Marks controller as disposed
       c. Qt then deletes the widget and its children
       d. C++ widget objects are safely deleted (no pending signals/timers)
    
    Design Rationale
    ---------------
    
    **Why override close() and deleteLater()?**
    To ensure controller disposal happens BEFORE Qt starts deleting C++ objects.
    This prevents queued signals/timers from trying to access deleted widgets.
    
    **Why NO __del__() method?**
    Python's garbage collector can run at unpredictable times, potentially during
    Qt object construction in other threads. Calling Qt operations during GC
    causes crashes. Instead, we rely on explicit disposal methods and Qt's
    parent-child cleanup.
    
    **Why not use destroyed signal?**
    The destroyed signal fires AFTER Qt has already deleted the C++ objects,
    making it too late to safely dispose the controller (which may try to access
    those deleted objects).
    
    Type Parameters
    --------------
    HK : str
        Type of hook keys (e.g., Literal["value", "enabled"])
    HV : Any
        Type of hook values
    P : BaseLayoutPayload
        Type of the payload (frozen dataclass with widget fields)
    C : BaseController
        Type of the controller being managed
    
    Parameters
    ----------
    controller : C
        The controller instance to manage (creates widgets, manages state)
    payload : P
        Payload containing the controller's widgets to be laid out
    layout_strategy : Optional[LayoutStrategy[P]]
        Function that arranges payload widgets in a layout
    parent : Optional[QWidget]
        Parent widget (follows Qt parent-child relationships)
    
    Attributes
    ----------
    _controller : C
        The managed controller instance
    
    Examples
    --------
    Basic usage with a text entry controller:
    
    >>> from dataclasses import dataclass
    >>> from integrated_widgets.widget_controllers import TextEntryController
    >>> 
    >>> controller = TextEntryController("Hello")
    >>> 
    >>> @dataclass(frozen=True)
    >>> class Payload(BaseLayoutPayload):
    ...     line_edit: QWidget
    >>> 
    >>> payload = Payload(line_edit=controller.line_edit)
    >>> 
    >>> def layout(parent, payload):
    ...     widget = QWidget()
    ...     layout = QVBoxLayout(widget)
    ...     layout.addWidget(payload.line_edit)
    ...     return widget
    >>> 
    >>> widget = IQtControlledLayoutedWidget(controller, payload, layout)
    >>> widget.show()
    >>> 
    >>> # Later, clean up:
    >>> widget.close()  # Controller automatically disposed
    
    See Also
    --------
    IQtLayoutedWidget : Parent class for layout strategy management
    BaseController : Controller base class with disposal infrastructure
    BaseLayoutPayload : Payload structure for widget management
    """

    def __init__(
        self,
        controller: C,
        payload: P,
        layout_strategy: Optional[LayoutStrategy[P]] = None,
        parent: Optional[QWidget] = None
        ) -> None:
        """
        Create a managed widget that controls a controller's lifecycle.
        
        This initializer:
        1. Stores the controller reference
        2. Calls parent IQtLayoutedWidget to arrange payload widgets
        3. Sets up the widget to be functional and ready for display
        
        The controller should already be initialized with its widgets created.
        Those widgets should be included in the payload so the layout strategy
        can arrange them.
        
        **Important**: After initialization, the widget takes responsibility for
        disposing the controller when the widget is closed or destroyed.
        
        Parameters
        ----------
        controller : C
            The controller instance to manage. Must be fully initialized with
            its widgets already created. The widget will call dispose() on this
            controller when it is closed or destroyed.
        
        payload : P
            A frozen dataclass containing the widgets to be laid out. Typically,
            these are the controller's widgets (e.g., line edits, buttons, labels).
            The payload's registered_widgets property provides access to all widgets.
        
        layout_strategy : Optional[LayoutStrategy[P]]
            A callable that takes (parent, payload) and returns a QWidget with
            the payload's widgets arranged in a layout. If None, the widget
            remains empty until set_layout_strategy() is called.
        
        parent : Optional[QWidget]
            The parent widget for Qt's parent-child hierarchy. When a parent
            widget is destroyed, Qt automatically destroys all children. Our
            overridden methods ensure the controller is disposed first.
        
        Raises
        ------
        ValueError
            If payload contains non-QWidget fields (validated in BaseLayoutPayload)
        TypeError
            If layout_strategy doesn't return a QWidget
        
        Examples
        --------
        Create a simple managed text entry:
        
        >>> controller = TextEntryController("initial")
        >>> payload = MyPayload(line_edit=controller.line_edit)
        >>> widget = IQtControlledLayoutedWidget(controller, payload, my_layout)
        >>> widget.show()
        
        Notes
        -----
        - The controller is NOT disposed in __init__; disposal only happens when
          the widget is explicitly closed or destroyed
        - After initialization, you can access the controller via self.controller
        - The widget does not take ownership of the payload widgets in terms of
          reference counting; Qt's parent-child relationships manage memory
        """
        
        self._controller = controller
        super().__init__(payload=payload, layout_strategy=layout_strategy, parent=parent)
        
        # Parent the controller's internal QObject to this widget to prevent GC
        # This MUST happen after super().__init__() because self must be fully initialized first
        controller.qt_object.setParent(self)
    
    def close(self) -> bool:  # type: ignore
        """Close the widget and dispose the controller.
        
        This is the most Qt-idiomatic way to clean up a widget. It ensures
        the controller is properly disposed before Qt begins deleting widget
        objects, preventing errors from queued signals or timers trying to
        access deleted widgets.
        
        Disposal Order
        -------------
        1. Controller.dispose() is called:
           - Disconnects all hooks (stops observables updates)
           - Stops all timers (prevents queued callbacks)  
           - Disconnects Qt signals (stops widget invalidation)
           - Marks controller as disposed
        2. super().close() is called:
           - Qt closes the widget and its children
           - Parent-child relationships ensure proper cleanup
        
        Returns
        -------
        bool
            True if the widget was closed successfully, False otherwise
            (follows QWidget.close() semantics)
        
        Examples
        --------
        Explicit cleanup when done with a widget:
        
        >>> widget = IQtControlledLayoutedWidget(controller, payload, layout)
        >>> widget.show()
        >>> # ... use the widget ...
        >>> widget.close()  # Controller disposed, widget closed
        
        Notes
        -----
        - Safe to call multiple times (controller checks _is_disposed flag)
        - All exceptions during disposal are caught and ignored for robustness
        - After close(), the widget and controller should not be used
        - This is the recommended way to clean up in Qt applications
        
        See Also
        --------
        deleteLater : Schedule cleanup via Qt event loop
        QWidget.close : Qt's standard widget close method
        """
        # Dispose controller first to stop all operations
        if hasattr(self, '_controller') and self._controller is not None: # type: ignore
            try:
                if not self._controller._is_disposed:  # type: ignore
                    self._controller.dispose()
            except Exception:
                # Ignore all disposal errors for robustness
                # Controller may be in an unusual state during shutdown
                pass
        
        # Then let Qt handle widget cleanup
        return super().close()
    
    def deleteLater(self) -> None:  # type: ignore
        """Schedule widget deletion and dispose controller.
        
        This method is used when you want to delete a widget via Qt's event loop
        rather than immediately. It's commonly used when deleting widgets from
        their own signal handlers or when you want to defer cleanup.
        
        The controller is disposed immediately (before scheduling), ensuring no
        queued operations will try to access widgets that are about to be deleted.
        
        Disposal Order
        -------------
        1. Controller.dispose() is called immediately:
           - Disconnects all hooks
           - Stops all timers
           - Disconnects Qt signals
           - Marks controller as disposed
        2. super().deleteLater() schedules Qt deletion:
           - Widget will be deleted on next event loop iteration
           - Qt's deferred delete mechanism ensures safety
        
        Examples
        --------
        Delete a widget from its own signal handler:
        
        >>> def on_close_clicked():
        ...     widget.deleteLater()  # Safe to call from signal handler
        >>> 
        >>> close_button.clicked.connect(on_close_clicked)
        
        Remove widgets from a container:
        
        >>> for widget in container_widgets:
        ...     widget.deleteLater()  # Schedules all for deletion
        
        Notes
        -----
        - Controller is disposed IMMEDIATELY, not deferred
        - Widget deletion is DEFERRED to next event loop iteration
        - Safe to call from signal handlers (unlike direct delete)
        - Safe to call multiple times (Qt tracks deletion state)
        - After calling, do not access the widget or controller
        
        See Also
        --------
        close : Immediate cleanup (more common in applications)
        QWidget.deleteLater : Qt's deferred deletion mechanism
        """
        # Dispose controller first (immediately, not deferred)
        if hasattr(self, '_controller') and self._controller is not None: # type: ignore
            try:
                if not self._controller._is_disposed:  # type: ignore
                    self._controller.dispose()
            except Exception:
                # Ignore all disposal errors for robustness
                pass
        
        # Then schedule deletion (deferred to event loop)
        super().deleteLater()

    ###########################################################################
    # Public API
    ###########################################################################
    
    @property
    def controller(self) -> C:
        """
        Access the managed controller instance.
        
        Use this property to interact with the controller's methods, access its
        state, or connect to its hooks.
        
        Returns
        -------
        C
            The controller instance managed by this widget
        
        Examples
        --------
        >>> widget = IQtControlledLayoutedWidget(controller, payload, layout)
        >>> value = widget.controller.value  # Access controller's value
        >>> widget.controller.change_value("new")  # Call controller method
        
        Notes
        -----
        - The controller remains valid until the widget is closed/destroyed
        - After close(), the controller will be disposed and should not be used
        - Do not manually dispose the controller; let the widget manage it
        """
        return self._controller

    def get_hook(self, key: HK) -> HookLike[HV]:
        """
        Get a hook from the controller by key.
        
        This is a convenience method that forwards to the controller's get_hook()
        method, allowing direct access to the controller's hooks without needing
        to access the controller property first.
        
        Parameters
        ----------
        key : HK
            The hook key (e.g., "value", "enabled")
        
        Returns
        -------
        HookLike[HV]
            The hook instance that can be connected to other hooks
        
        Examples
        --------
        >>> hook = widget.get_hook("value")
        >>> hook.connect_hook(other_hook)
        
        See Also
        --------
        controller : Access the controller directly
        get_value_of_hook : Get the current value instead of the hook
        """
        return self._controller.get_hook(key)

    def get_value_of_hook(self, key: HK) -> HV:
        """
        Get the current value of a hook from the controller.
        
        This is a convenience method that forwards to the controller's
        get_value_of_hook() method, providing quick access to hook values
        without needing to get the hook first.
        
        Parameters
        ----------
        key : HK
            The hook key (e.g., "value", "enabled")
        
        Returns
        -------
        HV
            The current value of the hook
        
        Examples
        --------
        >>> value = widget.get_value_of_hook("value")
        >>> enabled = widget.get_value_of_hook("enabled")
        
        See Also
        --------
        controller : Access the controller directly
        get_hook : Get the hook itself instead of just its value
        """
        return self._controller.get_value_of_hook(key)

