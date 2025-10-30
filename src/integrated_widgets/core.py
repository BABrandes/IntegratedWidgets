"""
Advanced/core API for custom layouts and extension.

This submodule exposes low-level building blocks for advanced users:
- Layout composition base classes (IQtControlledLayoutedWidget, IQtLayoutedWidget)
- Custom layout strategy classes (LayoutStrategyBase, LayoutPayloadBase)

Most users should use top-level imports from `integrated_widgets` for day-to-day widgets.
Only use `integrated_widgets.core` if you are building custom containers, widgets, or layouts.

Common imports:
    from integrated_widgets.core import (
        IQtControlledLayoutedWidget,
        IQtLayoutedWidget,
        LayoutStrategyBase,
        LayoutPayloadBase
    )
"""

from .iqt_widgets.core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .iqt_widgets.core.iqt_layouted_widget import IQtLayoutedWidget
from .iqt_widgets.core.layout_strategy_base import LayoutStrategyBase
from .iqt_widgets.core.layout_payload_base import LayoutPayloadBase

__all__ = [
    "IQtControlledLayoutedWidget",
    "IQtLayoutedWidget",
    "LayoutStrategyBase",
    "LayoutPayloadBase"
]