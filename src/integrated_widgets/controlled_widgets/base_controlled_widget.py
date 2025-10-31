from typing import Optional, Any
from logging import Logger

from PySide6.QtCore import Signal

from integrated_widgets.controllers.core.base_controller import BaseController

class BaseControlledWidget:

    userInputFinishedSignal = Signal(object)
    """
    Signal emitted when user input is finished.
    
    It only emits when the controller is not blocking signals, e.g. during an internal widget update.
    
    The signal always emits a single object argument. For Qt signals that emit multiple arguments,
    this will be a tuple containing all arguments. For Qt signals with no arguments, this will be None.
    For Qt signals with a single argument, that argument is passed directly.
    """

    def __init__(self, controller: BaseController[Any, Any], logger: Optional[Logger] = None) -> None:
        # Don't call super().__init__() here - we need to initialize attributes first,
        # then let the Qt widget (QLineEdit, QLabel, etc.) handle QObject initialization
        # in its own __init__() call to avoid double initialization issues.
        # The Signal is defined at class level and will work once QObject is initialized by the widget.
        self._controller = controller
        self._logger = logger
        self._internal_widget_update = False

    @property
    def controller(self) -> BaseController[Any, Any]:
        return self._controller

    @property
    def logger(self) -> Optional[Logger]:
        return self._logger

    def _on_user_input_finished(self, *args: Any, **kwargs: Any) -> None:
        """Handle when user input is finished.
        
        This method is called when user input is finished, such as when the user presses Enter or loses focus.
        It emits the user_input_finished signal.
        
        Signals are suppressed if:
        - The controller is blocking signals (during widget invalidation)
        - The widget is not visible (when actually hidden, not just during relayout)
        """

        # Check if this is triggered during internal widget updates or when signals are blocked
        if self._controller.is_blocking_signals:
            # The controller is blocking signals, so we do nothing
            return

        if self._controller.is_relayouting():
            # The controller is relayouting, so we do nothing
            return
        
        # The controller is not blocking signals and not relayouting, so we can emit the signal
        # Always emit a single object: None for no args, first arg for single arg, tuple for multiple args
        if len(args) == 0:
            signal_arg = None
        elif len(args) == 1:
            signal_arg = args[0]
        else:
            signal_arg = tuple(args) if args else None
        self.userInputFinishedSignal.emit(signal_arg) # type: ignore