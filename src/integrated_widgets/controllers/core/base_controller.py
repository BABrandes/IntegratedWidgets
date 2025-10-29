from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, final, Callable, Mapping, Any, TypeVar, Generic
from logging import Logger

from PySide6.QtCore import QObject, Qt, Signal, QThread
from PySide6.QtCore import QTimer

#BAB imports
from nexpy.core import NexusManager, SubmissionError
from nexpy import XBase

# Local imports
from ...auxiliaries.resources import log_msg

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

HK = TypeVar("HK", bound=str)
HV = TypeVar("HV")
C = TypeVar("C", bound="BaseController[Any, Any]")

class BaseController(XBase[HK, HV], Generic[HK, HV]):

    def __init__(
        self,
        *,
        nexus_manager: NexusManager,
        debounce_ms: int|Callable[[], int],
        logger: Optional[Logger] = None,
        ) -> None:

        # Store callback reference for internal use and debounce ms
        self._nexus_manager = nexus_manager

        # Initialize internal state first (before creating Qt objects)
        self._signals_blocked: bool = False
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        self._debounce_ms: int|Callable[[], int] = debounce_ms
        self._logger: Optional[Logger] = logger
        
        # Create a QObject to handle Qt parent-child relationships
        self._qt_object = QObject()
        # Note: We don't connect to destroyed signal here because it can cause crashes
        # during garbage collection. Controllers should be explicitly disposed, or
        # disposal will happen via parent widget's destroyed signal (see IQtControlledLayoutedWidget)

        # Helper to marshal arbitrary callables onto the GUI thread
        # Created without parent so it lives as long as the controller, not tied to Qt object lifecycle
        self._gui_executor = _GuiExecutor()
        
        # Create signal forwarder for queued widget invalidation
        # This ensures widget updates are processed through the Qt event loop rather than synchronously,
        # preventing re-entrancy issues when the hook system triggers updates
        # Created without parent so it lives as long as the controller, not tied to Qt object lifecycle
        self._widget_invalidation_signal = _WidgetInvalidationSignal()
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
        # Create timer without a parent so it lives as long as the controller, not tied to Qt object lifecycle
        self._submit_timer: QTimer = QTimer() # type: ignore
        self._submit_timer.setSingleShot(True)
        self._submit_timer.timeout.connect(self._commit_staged_widget_value)
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

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")

        # Ensure we're on the GUI thread (Qt signal handlers are guaranteed to be on GUI thread)
        if not QThread.currentThread().isMainThread(): # type: ignore
            # If somehow called from a non-GUI thread, use gui_invoke for safety
            self.gui_invoke(lambda: self._submit_values_debounced(values, debounce_ms))
            return
        
        self._pending_submission_values = values
        self._pending_submission_raise_error_flag = raise_submission_error_flag
        if debounce_ms is not None:
            deb_ms: int = debounce_ms
        else:
            if callable(self._debounce_ms):
                deb_ms = self._debounce_ms()
            else:
                deb_ms = self._debounce_ms
                
        interval = 0 if deb_ms <= 0 else deb_ms

        if interval == 0:
            # Immediate commit - call directly since we're on GUI thread
            self._commit_staged_widget_value()
        else:
            # Set up timer directly since we're already on the GUI thread
            self._submit_timer.setInterval(interval)
            self._submit_timer.start()

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
            success, msg = super()._submit_values(values_to_submit)

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
                self._invalidate_widgets_impl()
            except RuntimeError as e:
                # Catch errors from deleted Qt widgets (can happen during cleanup)
                if "Internal C++ object" in str(e) or "deleted" in str(e):
                    log_msg(self, "_invalidate_widgets_called_by_hook_system", self._logger, f"Widget already deleted, ignoring: {e}")
                    # Don't mark as disposed - widgets might be temporarily deleted during tab switching
                    # Controller will be properly disposed when dispose() is explicitly called
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