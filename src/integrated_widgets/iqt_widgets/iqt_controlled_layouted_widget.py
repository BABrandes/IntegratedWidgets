from typing import Optional, TypeVar, Generic, Protocol
from PySide6.QtWidgets import QWidget
from dataclasses import dataclass

from observables import HookLike

from integrated_widgets.util.base_controller import BaseController
from .iqt_layouted_widget import IQtLayoutedWidget, LayoutStrategy
from .layout_payload import BaseLayoutPayload


# ---- Strategy type for controllers ----------------------------------------------

HK = TypeVar("HK", bound=str)
HV = TypeVar("HV")
P = TypeVar("P", bound=BaseLayoutPayload)
C = TypeVar("C", bound=BaseController)  # Invariant since we return it in properties

class IQtControlledLayoutedWidget(IQtLayoutedWidget[P], Generic[HK, HV, P, C]):
    """
    Base widget class for widgets that wrap controllers.
    
    This class inherits from IQtLayoutedWidget, treating the controller as
    the payload. The controller's widgets are extracted and managed by the
    parent class, ensuring they're never accidentally deleted during layout changes.
    
    When this widget is destroyed, the controller is automatically disposed,
    cleaning up all its internal resources (hooks, signals, timers, etc.).
    """

    def __init__(
        self,
        controller: C,
        payload: P,
        layout_strategy: Optional[LayoutStrategy[P]] = None,
        parent: Optional[QWidget] = None
        ) -> None:
        """
        Initialize the base widget with a controller and layout strategy.
        
        Args:
            controller: The controller to wrap (becomes the payload)
            layout_strategy: Strategy for arranging the controller's widgets
            parent: Optional parent widget
        """
        
        self._controller = controller
        super().__init__(payload=payload, layout_strategy=layout_strategy, parent=parent)
    
    def __del__(self) -> None:
        """Cleanup when widget is destroyed - dispose the controller."""
        if hasattr(self, '_controller') and self._controller is not None:
            try:
                self._controller.dispose()
            except Exception:
                # Ignore errors during cleanup - controller may already be disposed
                pass

    ###########################################################################
    # Public API
    ###########################################################################
    
    @property
    def controller(self) -> C:
        """Get the controller (payload) of this widget."""
        return self._controller

    def get_hook(self, key: HK) -> HookLike[HV]:
        """Get a hook from the controller."""
        return self._controller.get_hook(key)

    def get_value_of_hook(self, key: HK) -> HV:
        """Get the current value of a hook from the controller."""
        return self._controller.get_value_of_hook(key)

