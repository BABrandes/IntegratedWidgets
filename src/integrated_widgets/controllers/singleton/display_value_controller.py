from __future__ import annotations

# Standard library imports
from typing import Optional, Generic, TypeVar, Callable
from logging import Logger

# BAB imports
from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

# Local imports
from ..core.base_singleton_controller import BaseSingletonController
from ..core.formatter_mixin import FormatterMixin
from ...controlled_widgets.controlled_qlabel import ControlledQLabel
from ...auxiliaries.resources import log_msg

T = TypeVar("T")

class DisplayValueController(BaseSingletonController[T], FormatterMixin[T], Generic[T]):
    """
    A controller for managing the widgets for displaying a value with a read-only label widget.
    """

    def __init__(
        self,
        value: T | Hook[T] | XSingleValueProtocol[T],
        *,
        formatter: Callable[[T], str] = lambda x: str(x),
        debounce_ms: int|Callable[[], int],
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        ) -> None:

        FormatterMixin.__init__(self, formatter=formatter, invalidate_widgets=self.invalidate_widgets) # type: ignore
        
        BaseSingletonController.__init__( # type: ignore
            self,
            value=value,
            debounce_ms=debounce_ms,
            logger=logger,
            nexus_manager=nexus_manager
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """
        Initialize the display label widget.
        
        This method is called internally during initialization. It creates a
        read-only label widget that will display the formatted value.
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        self._label = ControlledQLabel(self)

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the label from component values.
        
        This internal method synchronizes the label widget with the current value.
        It applies the formatter function (if set) or uses str() to convert the
        value to display text.
        
        The method is called automatically whenever the controller's value changes,
        whether from programmatic changes or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Updating label with value: {self.value}")

        text = self._formatter(self.value)
        self._label.setText(text)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_label(self) -> ControlledQLabel:
        """
        Get the display label widget.
        
        This is the read-only label that displays the formatted value. It can be
        added to any Qt layout.
        
        Returns
        -------
        ControlledLabel
            The label widget managed by this controller.
        
        Examples
        --------
        >>> label = controller.widget_label
        >>> layout.addWidget(label)
        """
        return self._label