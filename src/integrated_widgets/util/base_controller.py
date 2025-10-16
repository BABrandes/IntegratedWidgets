from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, final, Callable, Mapping, Any, TypeVar, Generic
from logging import Logger

from PySide6.QtCore import QObject, Qt, Signal, QThread
from PySide6.QtCore import QTimer

#BAB imports
from observables.core import NexusManager, BaseCarriesHooks

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
HV = TypeVar("HV")
C = TypeVar("C", bound="BaseController")

class BaseController(BaseCarriesHooks[HK, HV, C], Generic[HK, HV, C]):

    def __init__(
        self,
        submit_values_callback: Callable[[Mapping[str, Any]], tuple[bool, str]],
        *,
        nexus_manager: NexusManager,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
        ) -> None:

        # Store callback reference for internal use and debounce ms
        self._submit_values_callback = submit_values_callback
        self._debounce_ms = debounce_ms
        self._nexus_manager = nexus_manager

        # Create a QObject to handle Qt parent-child relationships
        self._qt_object = QObject()

        # Helper to marshal arbitrary callables onto the GUI thread
        self._gui_executor = _GuiExecutor(self._qt_object)
        
        # Create signal forwarder for queued widget invalidation
        # This ensures widget updates are processed through the Qt event loop rather than synchronously,
        # preventing re-entrancy issues when the hook system triggers updates
        self._widget_invalidation_signal = _WidgetInvalidationSignal(self._qt_object)
        self._widget_invalidation_signal.trigger.connect(self._invalidate_widgets_called_by_hook_system, Qt.ConnectionType.QueuedConnection)
        
        # Initialize internal state
        self._signals_blocked: bool = False
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        self._logger: Optional[Logger] = logger
      
        # Queue initial widget invalidation (will execute after full initialization completes)
        # This ensures widgets reflect initial values once construction finishes
        self._widget_invalidation_signal.trigger.emit()

        ###########################################################################
        # Staging & commit control for widget-originated changes
        ###########################################################################
        self._pending_widget_value: Optional[Any|Mapping[str, Any]] = None
        self._committing: bool = False
        self._submit_timer: QTimer = QTimer(self._qt_object) # type: ignore
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

    ###########################################################################
    # Abstract Methods - To be implemented by subclasses
    ###########################################################################

    @abstractmethod
    def _initialize_widgets(self) -> None:
        """Create and set up widget instances.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to create their widgets.
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
        This is called automatically by the base controller when the component values have been changed.
        """
        raise NotImplementedError

    ###########################################################################
    # Signal Management and Blocking
    ###########################################################################

    ### NEW

    def _submit_values_debounced(self, value: Any|Mapping[str, Any], debounce_ms: Optional[int] = None) -> None:
        """
        Stage a value coming from widget/user interaction and commit after a debounce.
        Use in onChanged handlers for high-frequency inputs (e.g., typing).

        1. The value is staged
        2. The timer is started (the timer is reset when the value is changed)
        3. The value is committed when the timer expires

        NOTE: This method must be called from the GUI thread (Qt signal handlers).

        Args:
            value: The value to submit.
            debounce_ms: The debounce time in milliseconds. If None, the default debounce time is used.
        """

        if debounce_ms is None:
            debounce_ms = self._debounce_ms

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")

        # Ensure we're on the GUI thread (Qt signal handlers are guaranteed to be on GUI thread)
        if not QThread.currentThread().isMainThread(): # type: ignore
            # If somehow called from a non-GUI thread, use gui_invoke for safety
            self.gui_invoke(lambda: self._submit_values_debounced(value, debounce_ms))
            return

        self._pending_widget_value = value
        interval = 0 if debounce_ms is None or debounce_ms <= 0 else int(debounce_ms)

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
        """
        if self._pending_widget_value is None:
            return

        if self._is_disposed:
            raise RuntimeError("Controller has been disposed")

        if self._committing:
            return
        self._committing = True

        try:
            if self._is_disposed:
                raise RuntimeError("Controller has been disposed")
            value: Any|Mapping[str, Any] = self._pending_widget_value
            self._pending_widget_value = None
            success, msg = self._submit_values_callback(value)

            if success:
                log_msg(self, "_commit_staged_widget_value", self._logger, f"Successfully committed staged value: {value}")
            else:
                log_msg(self, "_commit_staged_widget_value", self._logger, f"Failed to commit staged value '{value}': {msg}")
                # Reset the state of the widget (reflect model's last committed value)
                self._invalidate_widgets_called_by_hook_system()
        finally:
            self._committing = False


    @final
    @property
    def is_blocking_signals(self) -> bool:
        return self._signals_blocked

    @final
    @is_blocking_signals.setter
    def is_blocking_signals(self, value: bool) -> None:
        self._signals_blocked = value

    @final
    @contextmanager
    def _internal_update(self):
        """Context manager for internal widget updates."""
        self._internal_widget_update = True
        try:
            yield
        finally:
            self._internal_widget_update = False

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

    ###########################################################################
    # Widget Update and Synchronization
    ###########################################################################

    @final
    def _invalidate_widgets_called_by_hook_system(self) -> None:
        """
        Invalidate the widgets.

        This method is called automatically by the base controller when component values have been changed by the hook system and the widgets should be invalidated.
        It automatically wraps the actual implementation in the internal update context.

        **DO NOT OVERRIDE:** Controllers should implement _invalidate_widgets_impl() instead.
        """
        if self._is_disposed:
            return  # Silently return if disposed to avoid errors during cleanup
        
        with self._internal_update():
            self.is_blocking_signals = True
            try:
                log_msg(self, "_invalidate_widgets_called_by_hook_system", self._logger, f"Invalidating widgets")
                self._invalidate_widgets_impl()
            finally:
                self.is_blocking_signals = False

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    @abstractmethod
    def dispose_impl(self) -> None:
        ...

    def dispose(self) -> None:
        """Dispose of the controller and clean up resources."""

        if self._is_disposed:
            return

        self._is_disposed = True

        # Stop any pending debounced submissions
        if self._submit_timer is not None:
            try:
                self._submit_timer.stop()
            except RuntimeError:
                # QTimer may have been deleted by Qt's parent-child mechanism
                pass

        # Call the implementation dispose method (for hook-specific cleanup)
        self.dispose_impl()
        
        # Common disposal cleanup (shared by all controller types)
        self._dispose_common_cleanup()

    def _dispose_common_cleanup(self) -> None:
        """Common disposal cleanup shared by all controller types."""
        
        # Disconnect widget invalidation signal
        if hasattr(self, '_widget_invalidation_signal') and self._widget_invalidation_signal is not None:
            try:
                # Check if the signal trigger still exists and is valid
                if hasattr(self._widget_invalidation_signal, 'trigger') and self._widget_invalidation_signal.trigger is not None:
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
        """Ensure proper cleanup when the object is garbage collected."""
        if not self._is_disposed:
            self.dispose()
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