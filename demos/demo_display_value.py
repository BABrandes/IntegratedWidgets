#!/usr/bin/env python3
"""Demo application for IQtDisplayValue widget."""

import sys
from typing import Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QPushButton, QHBoxLayout, QGridLayout
)
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit

from integrated_widgets import IQtDisplayValue
from integrated_widgets.iqt_widgets.iqt_display_value import Controller_Payload
from integrated_widgets.iqt_widgets.iqt_range_slider import IQtRangeSlider


def simple_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Simple layout: just the label."""
    return payload.label


def labeled_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Layout with a prefix label."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    layout.addWidget(QLabel("Current Value:"))
    layout.addWidget(payload.label)
    
    return widget


def grid_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Grid layout with label."""
    widget = QWidget()
    layout = QGridLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    layout.addWidget(QLabel("<b>Status:</b>"), 0, 0)
    layout.addWidget(payload.label, 0, 1)
    
    return widget


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtDisplayValue Demo")
    window.resize(600, 500)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtDisplayValue Demo</h2>"))
    layout.addWidget(QLabel("Demonstrating read-only value display with custom formatters"))
    
    # Counter with simple layout
    layout.addWidget(QLabel("<h3>1. Simple Number Display:</h3>"))
    counter = ObservableSingleValue(0)
    
    counter_display = IQtDisplayValue(
        value_or_hook_or_observable=counter,
        formatter=lambda x: f"Count: {x}",
        layout_strategy=simple_layout_strategy # type: ignore
    )
    layout.addWidget(counter_display)
    
    counter_button = QPushButton("Increment Counter")
    counter_button.clicked.connect(lambda: setattr(counter, 'value', counter.value + 1))
    layout.addWidget(counter_button)
    
    # Temperature with labeled layout
    layout.addWidget(QLabel("<h3>2. Temperature Display (RealUnitedScalar):</h3>"))
    temperature = ObservableSingleValue(RealUnitedScalar(20.0, Unit("°C")))
    
    temp_display = IQtDisplayValue(
        value_or_hook_or_observable=temperature,
        formatter=lambda x: f"{x.value():.1f} {x.unit}",
        layout_strategy=labeled_layout_strategy # type: ignore
    )
    layout.addWidget(temp_display)
    
    temp_up_button = QPushButton("Increase Temperature (+5°C)")
    temp_up_button.clicked.connect(
        lambda: setattr(temperature, 'value', 
                       RealUnitedScalar(temperature.value.value() + 5, Unit("°C")))
    )
    layout.addWidget(temp_up_button)
    
    temp_down_button = QPushButton("Decrease Temperature (-5°C)")
    temp_down_button.clicked.connect(
        lambda: setattr(temperature, 'value', 
                       RealUnitedScalar(temperature.value.value() - 5, Unit("°C")))
    )
    layout.addWidget(temp_down_button)
    
    # Status message with grid layout
    layout.addWidget(QLabel("<h3>3. Status Message Display:</h3>"))
    status = ObservableSingleValue("Ready")
    
    status_display = IQtDisplayValue(
        value_or_hook_or_observable=status,
        formatter=lambda x: f"✓ {x}" if x == "Ready" else f"⚠ {x}",
        layout_strategy=grid_layout_strategy # type: ignore
    )
    layout.addWidget(status_display)
    
    status_buttons_layout = QHBoxLayout()
    ready_button = QPushButton("Set Ready")
    ready_button.clicked.connect(lambda: setattr(status, 'value', "Ready"))
    status_buttons_layout.addWidget(ready_button)
    
    busy_button = QPushButton("Set Busy")
    busy_button.clicked.connect(lambda: setattr(status, 'value', "Busy"))
    status_buttons_layout.addWidget(busy_button)
    
    error_button = QPushButton("Set Error")
    error_button.clicked.connect(lambda: setattr(status, 'value', "Error"))
    status_buttons_layout.addWidget(error_button)
    
    layout.addLayout(status_buttons_layout)
    
    # Percentage with custom formatter
    layout.addWidget(QLabel("<h3>4. Percentage Display:</h3>"))
    percentage = ObservableSingleValue(0.75)
    
    percentage_display = IQtDisplayValue(
        value_or_hook_or_observable=percentage,
        formatter=lambda x: f"{x*100:.1f}%"
    )
    layout.addWidget(percentage_display)

    percentage_slider_layout = QHBoxLayout()
    for value, label in [(0.0, "0%"), (0.25, "25%"), (0.5, "50%"), (0.75, "75%")]:
        btn = QPushButton(label)
        btn.clicked.connect(lambda checked, v=value: percentage.change_value(v)) # type: ignore
        percentage_slider_layout.addWidget(btn)
    layout.addLayout(percentage_slider_layout)
    
    percentage_slider = IQtRangeSlider[RealUnitedScalar](
        number_of_ticks=100,
        span_lower_relative_value=0.0,
        span_upper_relative_value=1.0,
        range_lower_value=RealUnitedScalar(0.5, Unit("V")),
        range_upper_value=RealUnitedScalar(1.5, Unit("V"))
    )
    layout.addWidget(percentage_slider.controller.widget_range_slider)
    percentage_slider.controller.span_lower_relative_value_hook.connect_hook(percentage, initial_sync_mode="use_target_value")
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

