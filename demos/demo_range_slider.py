#!/usr/bin/env python3
"""Demo application for IQtRangeSlider widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit

from integrated_widgets import IQtRangeSlider, IQtDisplayValue


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
    
    # Simple relative range (0.0 to 1.0)
    layout.addWidget(QLabel("<h3>Simple Relative Range:</h3>"))
    lower_relative = ObservableSingleValue(0.2)
    upper_relative = ObservableSingleValue(0.8)
    
    simple_slider = IQtRangeSlider(
        number_of_ticks=100,
        span_lower_relative_value=lower_relative,
        span_upper_relative_value=upper_relative,
        minimum_span_size_relative_value=0.1,
        debounce_of_range_slider_changes_ms=0
    )
    layout.addWidget(simple_slider)
    
    lower_display = IQtDisplayValue(lower_relative, formatter=lambda x: f"Lower: {x:.2f}")
    upper_display = IQtDisplayValue(upper_relative, formatter=lambda x: f"Upper: {x:.2f}")
    layout.addWidget(lower_display)
    layout.addWidget(upper_display)
    
    # Range with physical values (temperature)
    layout.addWidget(QLabel("<h3>Temperature Range (°C):</h3>"))
    temp_lower = ObservableSingleValue(0.3)
    temp_upper = ObservableSingleValue(0.7)
    
    temp_slider = IQtRangeSlider(
        number_of_ticks=100,
        span_lower_relative_value=temp_lower,
        span_upper_relative_value=temp_upper,
        minimum_span_size_relative_value=0.05,
        range_lower_value=RealUnitedScalar(-50.0, Unit("°C")),
        range_upper_value=RealUnitedScalar(150.0, Unit("°C")),
        debounce_of_range_slider_changes_ms=0
    )
    layout.addWidget(temp_slider)
    
    # Display computed temperature values
    def format_temp(rel_val: float) -> str:
        temp_c = -50.0 + rel_val * 200.0
        return f"{temp_c:.1f}°C"
    
    temp_lower_display = IQtDisplayValue(temp_lower, formatter=format_temp)
    temp_upper_display = IQtDisplayValue(temp_upper, formatter=format_temp)
    layout.addWidget(QLabel("Temperature range:"))
    layout.addWidget(temp_lower_display)
    layout.addWidget(temp_upper_display)
    
    # Price range
    layout.addWidget(QLabel("<h3>Price Range:</h3>"))
    price_lower = ObservableSingleValue(0.1)
    price_upper = ObservableSingleValue(0.9)
    
    price_slider = IQtRangeSlider(
        number_of_ticks=50,
        span_lower_relative_value=price_lower,
        span_upper_relative_value=price_upper,
        minimum_span_size_relative_value=0.1,
        range_lower_value=0.0,
        range_upper_value=1000.0,
        debounce_of_range_slider_changes_ms=0
    )
    layout.addWidget(price_slider)
    
    def format_price(rel_val: float) -> str:
        price = rel_val * 1000.0
        return f"${price:.2f}"
    
    price_lower_display = IQtDisplayValue(price_lower, formatter=format_price)
    price_upper_display = IQtDisplayValue(price_upper, formatter=format_price)
    layout.addWidget(QLabel("Price range:"))
    layout.addWidget(price_lower_display)
    layout.addWidget(price_upper_display)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

