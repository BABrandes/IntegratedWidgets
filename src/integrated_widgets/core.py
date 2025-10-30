"""
Advanced/core API for custom layouts and widget composition.

This submodule provides the foundation classes for building custom IQT widgets and advanced layout compositions. It exposes the low-level building blocks that power the high-level widget API.

Use Cases:
----------
- Building custom IQT widgets that integrate with nexpy observables
- Creating complex widget compositions with custom layouts
- Implementing specialized controllers for domain-specific widgets
- Developing reusable widget libraries

Architecture:
-------------
The core API provides three main foundation classes:

1. **IQtWidgetBase**: Base class for layout-managed widgets using the Strategy pattern
2. **IQtControllerWidgetBase**: Combines controllers with layout management and lifecycle handling
3. **IQtSingletonControllerWidgetBase**: Specialized base for single-value controllers
4. **IQtCompositeControllerWidgetBase**: Specialized base for multi-value controllers

Plus supporting protocols:
- **LayoutStrategyBase**: Protocol for layout strategy callables
- **LayoutPayloadBase**: Base class for immutable widget payload dataclasses

Most users should use top-level imports from `integrated_widgets` for standard widgets.
Only import from `integrated_widgets.core` when building custom widgets or advanced compositions.

Common imports:
    from integrated_widgets.core import (
        IQtControllerWidgetBase,      # Base for controller-managed widgets
        IQtWidgetBase,                 # Base for layout-managed widgets
        IQtSingletonControllerWidgetBase,  # For single-value widgets
        IQtCompositeControllerWidgetBase,  # For multi-value widgets
        LayoutStrategyBase,            # Protocol for layout strategies
        LayoutPayloadBase              # Base for payload dataclasses
    )

Example Usage:
-------------
Creating a custom widget with controller lifecycle management:

    from dataclasses import dataclass
    from integrated_widgets.core import IQtControllerWidgetBase, LayoutPayloadBase

    @dataclass(frozen=True)
    class MyPayload(LayoutPayloadBase):
        widget: QWidget

    class MyCustomWidget(IQtControllerWidgetBase[MyPayload]):
        def __init__(self, controller, payload, **kwargs):
            super().__init__(controller, payload, **kwargs)
            # Custom initialization here
"""

from .iqt_widgets.foundation.iqt_widget_base import IQtWidgetBase
from .iqt_widgets.foundation.iqt_controller_widget_base import IQtControllerWidgetBase
from .iqt_widgets.foundation.iqt_composite_controller_widget_base import IQtCompositeControllerWidgetBase
from .iqt_widgets.foundation.iqt_singleton_controller_widget_base import IQtSingletonControllerWidgetBase
from .iqt_widgets.foundation.layout_strategy_base import LayoutStrategyBase
from .iqt_widgets.foundation.layout_payload_base import LayoutPayloadBase

__all__ = [
    "IQtCompositeControllerWidgetBase",
    "IQtSingletonControllerWidgetBase",
    "IQtControllerWidgetBase",
    "IQtWidgetBase",
    "LayoutStrategyBase",
    "LayoutPayloadBase"
]