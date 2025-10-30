"""
Advanced/core API for custom layouts and extension.

This submodule exposes low-level building blocks for advanced users:
- Layout composition base classes (IQtControllerWidgetBase, IQtWidgetBase)
- Custom layout strategy classes (LayoutStrategyBase, LayoutPayloadBase)

Most users should use top-level imports from `integrated_widgets` for day-to-day widgets.
Only use `integrated_widgets.core` if you are building custom containers, widgets, or layouts.

Common imports:
    from integrated_widgets.core import (
        IQtControllerWidgetBase,
        IQtSingletonControllerWidgetBase,
        IQtCompositeControllerWidgetBase,
        IQtWidgetBase,
        LayoutStrategyBase,
        LayoutPayloadBase
    )
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