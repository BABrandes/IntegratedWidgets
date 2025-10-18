from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, final, Callable, Mapping, Any, TypeVar, Generic
from logging import Logger
import warnings
from PySide6.QtCore import QObject, Qt, Signal, QThread
from PySide6.QtCore import QTimer

#BAB imports
from observables.core import NexusManager, CarriesHooksBase, SubmissionError

# Local imports
from ..util.resources import log_msg

class _WidgetInvalidationSignal(QObject):
    """Internal QObject used to marshal widget invalidation requests to the Qt event loop.
    
    This ensures that widget updates triggered by the hook system are queued
    rather than executed synchronously, preventing re-entrancy issues and
    ensuring proper event loop processing.
    """
    trigger = Signal()

# Helper QObject to execute callables on the GUI thread via a queued signal
class _GuiExecutor(QObject):
    """Internal QObject to execute callables on the GUI thread via a queued signal."""
    execute = Signal(object)

    def __init__(self, parent: Optional[QObject] = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        # Ensure queued delivery so the slot runs in this object's thread (GUI thread)
        self.execute.connect(self._execute, Qt.ConnectionType.QueuedConnection)

    def _execute(self, func: object) -> None:
        try:
            if callable(func):
                func()  # type: ignore[misc]
        except Exception:
            # Swallow exceptions to avoid breaking the Qt event loop; rely on caller's logging
            pass

# Default debounce time for all controllers (can be overridden by users)
DEFAULT_DEBOUNCE_MS: int = 100

HK = TypeVar("HK", bound=str)
"""Hook Key Type - String literal type for hook identifiers (e.g., Literal["value", "enabled"])"""

HV = TypeVar("HV")
"""Hook Value Type - The type of values stored in hooks (e.g., int, str, bool)"""

C = TypeVar("C", bound="BaseController[Any, Any, Any]")
"""Controller Type - The concrete controller class type for self-referential typing"""

class BaseController(CarriesHooksBase[HK, HV, C], Generic[HK, HV, C]):
    """
    Abstract base class for all widget controllers in the Integrated Widgets framework.
    
    This class provides the foundation for creating Qt widget controllers that integrate
    with the observables hook system, managing bidirectional data binding, widget lifecycle,
    debounced updates, and Qt signal/slot connections.
    
    **Architecture Overview:**
    BaseController sits between Qt widgets and the observables hook system, providing:
    - Automatic widget invalidation when hook values change
    - Debounced submission of user input changes back to hooks
    - Qt event loop integration for thread-safe updates
    - Lifecycle management with proper disposal of Qt resources
    - Internal subscriber mechanism for external notifications (e.g., contentChanged signal)
    
    **Type Parameters:**
    
    HK : str (bound)
        Hook Key type - typically a Literal string union defining all hook names.
        Example: Literal["value", "enabled"] for a controller with value and enabled hooks.
        
    HV : Any
        Hook Value type - the union of all possible value types for this controller's hooks.
        Example: int | bool for a controller with int value and bool enabled hooks.
        
    C : BaseController
        Controller type - the concrete subclass type for proper self-referential typing.
        This enables methods to return the correct subclass type.
        
    **Generic Type Usage Example:**
    ```python
    from typing import Literal
    
    class MyController(
        BaseSingleHookController[int, "MyController"],  # int values, self-referential
        Generic[int, "MyController"]
    ):
        # HK is automatically Literal["value"] from BaseSingleHookController
        # HV is int (the value type)
        # C is "MyController" (self-reference)
        ...
    ```
    
    **Subclass Requirements:**
    
    Controllers MUST implement these abstract methods:
    
    1. `_initialize_widgets_impl()` - Create and configure Qt widgets
       - Called once during initialization
       - Create widgets and connect their signals to controller handlers
       - Do NOT set widget values (handled by invalidate)
       
    2. `_invalidate_widgets_impl()` - Update widgets from hook values
       - Called automatically when hooks change
       - Read values from hooks via get_value_of_hook()
       - Update widget display to match current hook values
       
    3. `dispose_impl()` - Clean up controller-specific resources
       - Disconnect hooks
       - Clean up any custom resources
       - Base class handles Qt object cleanup
    
    **Internal Subscribers Mechanism:**
    
    The `_internal_subscribers` list allows external code (like IQtControlledLayoutedWidget)
    to be notified whenever the widget content is invalidated. This enables features like
    the `contentChanged` Qt signal without coupling the controller to Qt signals.
    
    Example of internal subscriber usage:
    ```python
    # In IQtControlledLayoutedWidget.__init__:
    controller._internal_subscribers.append(self.contentChanged.emit)
    
    # Now contentChanged signal is automatically emitted whenever hooks change
    ```
    
    **Debouncing:**
    
    Controllers use debouncing to smooth user input and reduce update frequency:
    - User types in a text field → values are staged
    - Timer starts (resets on each keystroke)
    - When timer expires → value is submitted to hooks
    - Default debounce time: 100ms (configurable per-controller or globally)
    
    **Thread Safety:**
    
    All widget updates are marshaled to the Qt GUI thread via queued signals,
    ensuring safe updates from background threads or hook system callbacks.
    
    **Lifecycle:**
    
    1. **Initialization**: Hooks created, widgets initialized, bindings established
    2. **Active**: Bidirectional sync between hooks and widgets
    3. **Disposal**: Hooks disconnected, Qt resources cleaned up
    
    **Example Implementation:**
    
    ```python
    from integrated_widgets.util.base_single_hook_controller import BaseSingleHookController
    from PySide6.QtWidgets import QLineEdit
    from typing import Literal
    
    class TextController(BaseSingleHookController[str, "TextController"]):
        def _initialize_widgets_impl(self) -> None:
            # Create widgets
            self._line_edit = QLineEdit()
            
            # Connect Qt signals to controller handlers
            self._line_edit.editingFinished.connect(self._on_text_edited)
        
        def _invalidate_widgets_impl(self) -> None:
            # Update widget from hook value
            current_text = self.get_value_of_hook("value")
            self._line_edit.setText(current_text)
        
        def _on_text_edited(self) -> None:
            # User edited text - submit to hook system with debounce
            new_text = self._line_edit.text()
            self.submit(new_text)
        
        @property
        def widget_line_edit(self) -> QLineEdit:
            return self._line_edit
    ```
    
    See Also
    --------
    BaseSingleHookController : For controllers with a single hook (most common)
    BaseComplexHookController : For controllers with multiple related hooks
    IQtControlledLayoutedWidget : High-level widget that manages controller lifecycle
    """

    def __init__(
        self,
        *,
        nexus_manager: NexusManager,
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
        ) -> None:
        """
        Initialize the base controller with Qt integration and hook system setup.
        
        This constructor sets up the foundational infrastructure for widget controllers:
        - Qt object for parent-child relationships
        - Widget invalidation signaling system
        - Debounced value submission mechanism
        - Internal subscriber notification system
        
        **Parameters:**
        
        nexus_manager : NexusManager
            The nexus manager for coordinating hook connections across observables.
            Usually obtained from DEFAULT_NEXUS_MANAGER or a custom nexus.
            
        debounce_ms : int | None, optional
            Debounce time in milliseconds for user input changes. Controls how long
            the controller waits after user input before submitting to hooks.
            - Default: 100ms (DEFAULT_DEBOUNCE_MS)
            - Lower values: More responsive but more frequent updates
            - Higher values: Smoother for rapid input (typing) but less responsive
            - 0: No debouncing, immediate submission
            
        logger : Logger | None, optional
            Optional logger for debugging controller operations. If provided, the
            controller will log initialization, disposal, and widget updates.
            
        **Internal State Initialized:**
        
        - `_qt_object`: QObject for Qt parent-child relationships and signal handling
        - `_widget_invalidation_signal`: Signal for queued widget updates
        - `_gui_executor`: Helper for thread-safe GUI operations
        - `_submit_timer`: QTimer for debounced value submission
        - `_internal_subscribers`: List of callables notified on widget invalidation
        - `_signals_blocked`: Flag to prevent recursive updates
        - `_internal_widget_update`: Flag indicating programmatic widget updates
        - `_is_disposed`: Flag tracking disposal state
        
        **Example:**
        
        ```python
        from observables.core import DEFAULT_NEXUS_MANAGER
        
        # In subclass __init__:
        super().__init__(
            nexus_manager=DEFAULT_NEXUS_MANAGER,
            debounce_ms=200,  # Longer debounce for smoother typing
            logger=my_logger
        )
        ```
        
        **Note:**
        Do not call this directly - it's called by BaseSingleHookController or
        BaseComplexHookController during their initialization.
        """

        # Store callback reference for internal use and debounce ms
        self._debounce_ms = debounce_ms if debounce_ms is not None else DEFAULT_DEBOUNCE_MS
        self._nexus_manager = nexus_manager

        # Initialize internal state first (before creating Qt objects)
        self._signals_blocked: bool = False
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        self._logger: Optional[Logger] = logger
        
        # Create a QObject to handle Qt parent-child relationships
        self._qt_object = QObject()
        # Note: We don't connect to destroyed signal here because it can cause crashes
        # during garbage collection. Controllers should be explicitly disposed, or
        # disposal will happen via parent widget's destroyed signal (see IQtControlledLayoutedWidget)

        # Helper to marshal arbitrary callables onto the GUI thread
        self._gui_executor = _GuiExecutor(self._qt_object)
        
        # Create signal forwarder for queued widget invalidation
        # This ensures widget updates are processed through the Qt event loop rather than synchronously,
        # preventing re-entrancy issues when the hook system triggers updates
        self._widget_invalidation_signal = _WidgetInvalidationSignal(self._qt_object)
        self._widget_invalidation_signal.trigger.connect(self._invalidate_widgets, Qt.ConnectionType.QueuedConnection)
      
        # Queue initial widget invalidation (will execute after full initialization completes)
        # This ensures widgets reflect initial values once construction finishes
        self._widget_invalidation_signal.trigger.emit()

        ###########################################################################
        # Staging & commit control for widget-originated changes
        ###########################################################################
        self._pending_submission_values: Optional[Mapping[HK, HV]] = None
        self._raise_submission_error_flag: bool = True # The first submission should raise an error if it fails
        self._committing: bool = False
        self._submit_timer: QTimer = QTimer(self._qt_object) # type: ignore
        self._submit_timer.setSingleShot(True)
        self._submit_timer.timeout.connect(self._commit_staged_widget_value)
        ###########################################################################

        ###########################################################################
        # Internal Subscribers - Notification mechanism for external observers
        ###########################################################################
        # List of no-argument callables that are invoked whenever widgets are invalidated.
        # This mechanism allows external code (e.g., IQtControlledLayoutedWidget) to be
        # notified of content changes without coupling the controller to Qt signals.
        # 
        # Example usage:
        #   controller._internal_subscribers.append(lambda: print("Content changed!"))
        #   controller._internal_subscribers.append(self.contentChanged.emit)
        #
        # Subscribers are called after _invalidate_widgets_impl() completes successfully.
        self._internal_subscribers: list[Callable[[], None]] = []
        ###########################################################################
        
        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "BaseController initialized, initial invalidation queued")

    @property
    @final
    def logger(self) -> Optional[Logger]:
        return self._logger

    @logger.setter
    @final
    def logger(self, logger: Optional[Logger]) -> None:
        self._logger = logger
    
    @property
    @final
    def qt_object(self) -> QObject:
        """Get the internal Qt object for this controller.
        
        This can be used to establish Qt parent-child relationships, allowing
        Qt to automatically dispose the controller when the parent is destroyed.
        
        Example:
            ```python
            controller = TextEntryController("initial")
            # Parent to a widget - controller will be disposed when widget is destroyed
            controller.qt_object.setParent(my_widget)
            ```
        
        Returns:
            The internal QObject that manages Qt resources for this controller.
        """
        return self._qt_object

    ###########################################################################
    # Abstract Methods - To be implemented by subclasses
    ###########################################################################

    @abstractmethod
    def _initialize_widgets_impl(self) -> None:
        """Create and set up widget instances.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to create their widgets.
        **DO NOT CALL THIS METHOD DIRECTLY:**

        This is called during initialization before any other operations.
        
        **What to do here:**
        - Create all widget instances (QWidget, QLabel, etc.)
        - Set up widget properties and initial states
        - Connect widget signals to internal handlers
        - Store widgets as instance attributes (e.g., self._label, self._button)
        
        **What NOT to do here:**
        - Don't update widget values from component values (that's handled by invalidate_widgets)
        - Don't set up bindings (base controller handles this)
        - Don't call update methods (base controller calls them automatically)
        - Don't call self._internal_update() (base controller handles this)
        - Don't use block_signals() or unblock_signals() (base controller handles this)
        """
        raise NotImplementedError

    @abstractmethod
    def _invalidate_widgets_impl(self) -> None:
        """
        Invalidate the widgets implementation.

        **REQUIRED OVERRIDE:** Controllers must implement this method to invalidate their widgets.
        **DO NOT CALL THIS METHOD DIRECTLY:** Use invalidate_widgets() instead.

        This is called automatically by the base controller when the component values have been changed.
        """
        raise NotImplementedError

    ###########################################################################
    # (Staged) Value Submission
    ###########################################################################

    #---------------------------------------------------------------------------
    # Public Methods
    #---------------------------------------------------------------------------

    def submit_values(self, values: Mapping[HK, HV], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = False, logger: Optional[Logger] = None) -> tuple[bool, str]:
        """
        Submit values to the controller.

        Args:
            values: The values to submit.
            debounce_ms: The debounce time in milliseconds. If None, the default debounce time is used.
            raise_submission_error_flag: If True, raise a SubmissionError if the submission fails (after the widgets have been invalidated to take on the last valid state)
        """
        self._submit_values_debounced(values, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)
        return True, "Values submitted"

    def submit_value(self, key: HK, value: HV, *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = False, logger: Optional[Logger] = None) -> tuple[bool, str]:
        """
        Submits a value to the controller.

        Args:
            value: The value to submit.
            debounce_ms: The debounce time in milliseconds. If None, the default debounce time is used.
            raise_submission_error_flag: If True, raise a SubmissionError if the submission fails (after the widgets have been invalidated to take on the last valid state)
        """
        self._submit_values_debounced({key: value}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)
        return True, "Value submitted"

    #---------------------------------------------------------------------------
    # Internal Methods
    #---------------------------------------------------------------------------

    def _submit_values_debounced(self, values: Mapping[HK, HV], debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = False) -> None:
        """
        Stage a value coming from widget/user interaction and commit after a debounce.
        Use in onChanged handlers for high-frequency inputs (e.g., typing).

        1. The value is staged
        2. The timer is started (the timer is reset when the value is changed)
        3. The value is committed when the timer expires

        NOTE: This method must be called from the GUI thread (Qt signal handlers).

        Args:
            values: The values to submit.
            debounce_ms: The debounce time in milliseconds. If None, the default debounce time is used.
            raise_submission_error_flag: If True, raise a SubmissionError if the submission fails (after the widgets have been invalidated to take on the last valid state)
        """

        if debounce_ms is None:
            debounce_ms = self._debounce_ms

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")

        # Ensure we're on the GUI thread (Qt signal handlers are guaranteed to be on GUI thread)
        if not QThread.currentThread().isMainThread(): # type: ignore
            # If somehow called from a non-GUI thread, use gui_invoke for safety
            self.gui_invoke(lambda: self._submit_values_debounced(values, debounce_ms))
            return

        self._pending_submission_values = values
        self._pending_submission_raise_error_flag = raise_submission_error_flag
        interval = 0 if debounce_ms <= 0 else int(debounce_ms)

        if interval == 0:
            # Immediate commit - call directly since we're on GUI thread
            self._commit_staged_widget_value()
        else:
            # Set up timer directly since we're already on the GUI thread
            try:
                self._submit_timer.setInterval(interval)
                self._submit_timer.start()
            except RuntimeError:
                # Timer may be deleted during shutdown; ignore
                pass

    def _commit_staged_widget_value(self) -> None:
        """
        Timer slot: commit the last staged value if present.

        Args:
            raise_submission_error_flag: If True, raise a SubmissionError if the submission fails.

        Raises:
            SubmissionError: If the submission fails and raise_submission_error_flag is True (after the widgets have been invalidated to take on the last valid state)
        """
        if self._pending_submission_values is None:
            return

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")

        if self._committing:
            return
        self._committing = True

        try:
            if self._is_disposed:
                raise RuntimeError("Controller has been disposed")
            values_to_submit = dict(self._pending_submission_values)
            self._pending_submission_value_or_values = None
            success, msg = super().submit_values(values_to_submit, raise_submission_error_flag=False)

            if success:
                log_msg(self, "_commit_staged_widget_value", self._logger, f"Successfully committed staged value: {values_to_submit}")
            else:
                log_msg(self, "_commit_staged_widget_value", self._logger, f"Failed to commit staged value '{values_to_submit}': {msg}")
                # Reset the state of the widget (reflect model's last committed value)
                self.invalidate_widgets()

            if not success and self._pending_submission_raise_error_flag:
                raise SubmissionError(msg, values_to_submit)
                 
        finally:
            self._committing = False

    ###########################################################################
    # Signal/Event driven invalidation
    ###########################################################################

    #---------------------------------------------------------------------------
    # Public Methods
    #---------------------------------------------------------------------------

    @final
    @property
    def is_blocking_signals(self) -> bool:
        return self._signals_blocked

    @final
    @is_blocking_signals.setter
    def is_blocking_signals(self, value: bool) -> None:
        self._signals_blocked = value

    def invalidate_widgets(self) -> None:
        """Invalidate the widgets to reflect current hook values.
        
        This is a safe public method that can be called by anyone to refresh
        the widget UI without triggering the hook system or changing any values.
        It's commonly used when formatters are set or other external changes
        require the widgets to be updated to show current values.
        
        This method:
        - Only updates widget display, does not change values
        - Does not trigger the observables/hook system
        - Is thread-safe and can be called from anywhere
        - Is safe to call multiple times
        - Does nothing if the controller is disposed
        """
        if self._is_disposed:
            return
        self._widget_invalidation_signal.trigger.emit()

    #---------------------------------------------------------------------------
    # Internal Methods
    #---------------------------------------------------------------------------

    @final
    @contextmanager
    def _internal_update(self):
        """Context manager for internal widget updates."""
        self._internal_widget_update = True
        try:
            yield
        finally:
            self._internal_widget_update = False

    @final
    def _invalidate_widgets(self) -> None:
        """
        Invalidate the widgets.

        This method is called automatically by the base controller when component values have been changed by the hook system and the widgets should be invalidated.
        It automatically wraps the actual implementation in the internal update context.

        **DO NOT OVERRIDE:** Controllers should implement _invalidate_widgets_impl() instead.
        **DO NOT CALL THIS METHOD DIRECTLY:** Use invalidate_widgets() instead.

        Args:
            calling_nexus_manager: The nexus manager that called this method.

        Raises:
            RuntimeError: If the calling nexus manager is different from the controller's nexus manager.
        """
        if self._is_disposed:
            return  # Silently return if disposed to avoid errors during cleanup
        
        with self._internal_update():
            self.is_blocking_signals = True

            try:
                log_msg(self, "_invalidate_widgets_called_by_hook_system", self._logger, f"Invalidating widgets")
                
                # Invalidate the widgets implementation
                self._invalidate_widgets_impl()

                try:
                    # Notify internal subscribers
                    for subscriber in self._internal_subscribers:
                        subscriber()
                except Exception as e:
                    warnings.warn(f"Error notifying internal subscribers: {e}")
                    log_msg(self, "_invalidate_widgets_called_by_hook_system", self._logger, f"Error notifying internal subscribers: {e}")

            except RuntimeError as e:
                # Catch errors from deleted Qt widgets (can happen during cleanup)
                if "Internal C++ object" in str(e) or "deleted" in str(e):
                    log_msg(self, "_invalidate_widgets_called_by_hook_system", self._logger, f"Widget already deleted, ignoring: {e}")
                    # Mark as disposed to prevent further attempts
                    self._is_disposed = True
                else:
                    raise
            finally:
                self.is_blocking_signals = False

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    @abstractmethod
    def dispose_impl(self) -> None:
        ...

    def dispose(self, *, from_del: bool = False) -> None:
        """Dispose of the controller and clean up resources.
        
        This method should be called explicitly when the controller is no longer needed.
        If the controller's Qt object has a parent widget, Qt's parent-child cleanup
        will automatically trigger disposal when the parent is destroyed.
        
        Args:
            from_del: Internal flag indicating if called from __del__. 
                      Skips potentially dangerous Qt operations during garbage collection.
        
        Example:
            ```python
            controller = TextEntryController("initial")
            # ... use controller ...
            controller.dispose()  # Clean up when done
            ```
        
        Or use Qt's parent-child relationship:
            ```python
            controller = TextEntryController("initial")
            # Parent the controller's Qt object to a widget
            controller._qt_object.setParent(my_widget)
            # Qt will automatically dispose when my_widget is destroyed
            ```
        """

        if self._is_disposed:
            return

        self._is_disposed = True

        # Stop any pending debounced submissions
        if self._submit_timer:
            try:
                self._submit_timer.stop()
            except RuntimeError:
                # QTimer may have been deleted by Qt's parent-child mechanism
                pass

        # Call the implementation dispose method (for hook-specific cleanup)
        self.dispose_impl()
        
        # Common disposal cleanup (shared by all controller types)
        self._dispose_common_cleanup(from_del=from_del)
    
    def close(self) -> None:
        """Qt-friendly alias for dispose().
        
        This provides a more intuitive name for Qt users who are familiar with
        close() methods on Qt widgets.
        """
        self.dispose()

    def _dispose_common_cleanup(self, *, from_del: bool = False) -> None:
        """Common disposal cleanup shared by all controller types.
        
        Args:
            from_del: If True, skip potentially dangerous Qt operations during garbage collection.
        """
        
        # If called from __del__ during garbage collection, skip Qt operations entirely
        # as they may crash due to inconsistent object state
        if from_del:
            return
        
        # Check if Qt application is still running before attempting Qt cleanup
        # This prevents crashes during interpreter shutdown or garbage collection
        try:
            from PySide6.QtWidgets import QApplication
            if QApplication.instance() is None:
                # Qt application has been destroyed, skip Qt cleanup
                return
        except (ImportError, RuntimeError):
            # Qt is shutting down or unavailable
            return
        
        # Disconnect widget invalidation signal
        if hasattr(self, '_widget_invalidation_signal'):
            try:
                # Check if the signal trigger still exists and is valid
                if hasattr(self._widget_invalidation_signal, 'trigger'):
                    # Additional check: try to access a property to see if the object is still valid
                    if hasattr(self._widget_invalidation_signal.trigger, 'blockSignals'):
                        self._widget_invalidation_signal.trigger.disconnect()
            except (RuntimeError, AttributeError) as e:
                # Qt object may have been deleted already during shutdown
                log_msg(self, "dispose", self._logger, f"Error disconnecting widget invalidation signal: {e}")
        
        # Clean up Qt object and all its children
        if hasattr(self, '_qt_object'):
            try:
                # Check if the Qt object is still valid before trying to delete it
                if hasattr(self._qt_object, 'isVisible'):  # Quick check if object is still valid
                    self._qt_object.deleteLater()
            except (RuntimeError, AttributeError) as e:
                # Qt object may have been deleted already during shutdown
                log_msg(self, "dispose", self._logger, f"Error deleting Qt object: {e}")

        log_msg(self, f"{self.__class__.__name__} disposed", self._logger, "Controller disposed")

    def __del__(self) -> None:
        """Mark object as being garbage collected.
        
        Note: We intentionally don't call dispose() here because Qt cleanup
        during garbage collection can crash. Controllers should be explicitly
        disposed before going out of scope, or rely on Qt's parent-child cleanup.
        """
        pass
    ###########################################################################
    # GUI Thread Invocation Helper
    ###########################################################################

    @final
    def gui_invoke(self, func: Callable[[], None]) -> None:
        """Schedule *func* to run on the GUI thread via a queued connection.
        Safe to call from worker threads. No-op if controller is disposed.
        """
        if self._is_disposed:
            return
        self._gui_executor.execute.emit(func)