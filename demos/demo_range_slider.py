#!/usr/bin/env python3
"""Demo application for IQtRangeSlider widget."""

import sys
from typing import Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QHBoxLayout, QGridLayout
)
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit

from integrated_widgets import IQtRangeSlider
from integrated_widgets.iqt_widgets.iqt_range_slider import Controller_Payload


def simple_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Simple layout: slider + span values only."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    layout.addWidget(payload.range_slider)
    
    # Span values in horizontal layout
    span_layout = QHBoxLayout()
    span_layout.addWidget(QLabel("Lower:"))
    span_layout.addWidget(payload.span_lower_value)
    span_layout.addWidget(QLabel("Upper:"))
    span_layout.addWidget(payload.span_upper_value)
    layout.addLayout(span_layout)
    
    return widget


def detailed_grid_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Detailed layout: slider + all displays in a grid."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Slider at top
    layout.addWidget(payload.range_slider)
    
    # Grid for all value displays
    grid = QGridLayout()
    grid.setContentsMargins(5, 5, 5, 5)
    grid.setSpacing(10)
    
    # Row 0: Range bounds
    grid.addWidget(QLabel("<b>Range:</b>"), 0, 0)
    grid.addWidget(QLabel("Min:"), 0, 1)
    grid.addWidget(payload.range_lower_value, 0, 2)
    grid.addWidget(QLabel("Max:"), 0, 3)
    grid.addWidget(payload.range_upper_value, 0, 4)
    
    # Row 1: Span values
    grid.addWidget(QLabel("<b>Span:</b>"), 1, 0)
    grid.addWidget(QLabel("Lower:"), 1, 1)
    grid.addWidget(payload.span_lower_value, 1, 2)
    grid.addWidget(QLabel("Upper:"), 1, 3)
    grid.addWidget(payload.span_upper_value, 1, 4)
    
    # Row 2: Computed values
    grid.addWidget(QLabel("<b>Computed:</b>"), 2, 0)
    grid.addWidget(QLabel("Size:"), 2, 1)
    grid.addWidget(payload.span_size_value, 2, 2)
    grid.addWidget(QLabel("Center:"), 2, 3)
    grid.addWidget(payload.span_center_value, 2, 4)
    
    layout.addLayout(grid)
    
    return widget


def compact_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Compact layout: slider + only essential info."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    layout.addWidget(payload.range_slider)
    
    # Single line with range and span
    info_layout = QHBoxLayout()
    info_layout.addWidget(QLabel("Range:"))
    info_layout.addWidget(payload.span_lower_value)
    info_layout.addWidget(QLabel("to"))
    info_layout.addWidget(payload.span_upper_value)
    info_layout.addWidget(QLabel("(Size:"))
    info_layout.addWidget(payload.span_size_value)
    info_layout.addWidget(QLabel(")"))
    info_layout.addStretch()
    
    layout.addLayout(info_layout)
    
    return widget


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtRangeSlider Demo")
    window.resize(600, 500)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtRangeSlider Demo</h2>"))
    layout.addWidget(QLabel("Demonstrating custom layout strategies with set_layout_strategy()"))
    
    # Simple relative range (0.0 to 1.0) with simple layout
    layout.addWidget(QLabel("<h3>1. Simple Layout (slider + span values):</h3>"))
    lower_relative = ObservableSingleValue(0.2)
    upper_relative = ObservableSingleValue(0.8)
    
    simple_slider = IQtRangeSlider[float](
        number_of_ticks=100,
        span_lower_relative_value=lower_relative,
        span_upper_relative_value=upper_relative,
        minimum_span_size_relative_value=0.1,
        debounce_ms=0
    )
    # Apply custom simple layout
    simple_slider.set_layout_strategy(lambda payload, **_: simple_layout_strategy(payload))
    layout.addWidget(simple_slider)
    
    # Range with physical values (temperature) with detailed grid layout
    layout.addWidget(QLabel("<h3>2. Detailed Grid Layout (all values in grid):</h3>"))
    temp_lower = ObservableSingleValue(0.3)
    temp_upper = ObservableSingleValue(0.7)
    
    temp_slider = IQtRangeSlider[RealUnitedScalar](
        number_of_ticks=100,
        span_lower_relative_value=temp_lower,
        span_upper_relative_value=temp_upper,
        minimum_span_size_relative_value=0.05,
        range_lower_value=RealUnitedScalar(-50.0, Unit("°C")),
        range_upper_value=RealUnitedScalar(150.0, Unit("°C")),
        debounce_ms=0
    )
    # Apply custom detailed grid layout
    temp_slider.set_layout_strategy(lambda payload, **_: detailed_grid_layout_strategy(payload))
    layout.addWidget(temp_slider)
    
    # Price range with compact layout
    layout.addWidget(QLabel("<h3>3. Compact Layout (single line info):</h3>"))
    price_lower = ObservableSingleValue(0.1)
    price_upper = ObservableSingleValue(0.9)
    
    price_slider = IQtRangeSlider[float](
        number_of_ticks=50,
        span_lower_relative_value=price_lower,
        span_upper_relative_value=price_upper,
        minimum_span_size_relative_value=0.1,
        range_lower_value=0.0,
        range_upper_value=1000.0,
        debounce_ms=0
    )
    # Apply custom compact layout
    price_slider.set_layout_strategy(lambda payload, **_: compact_layout_strategy(payload))
    layout.addWidget(price_slider)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

