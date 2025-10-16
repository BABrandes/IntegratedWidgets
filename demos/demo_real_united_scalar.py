#!/usr/bin/env python3
"""Demo application for IQtRealUnitedScalar widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit, NamedQuantity

from integrated_widgets import IQtRealUnitedScalar, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtRealUnitedScalar Demo")
    window.resize(600, 500)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtRealUnitedScalar Demo</h2>"))
    layout.addWidget(QLabel("Edit values with units - conversions happen automatically!"))
    
    # Distance measurement
    layout.addWidget(QLabel("<h3>Distance:</h3>"))
    distance_units = {
        NamedQuantity.LENGTH.dimension: {Unit("m"), Unit("cm"), Unit("mm"), Unit("km"), Unit("inch"), Unit("ft")}
        }
    distance = ObservableSingleValue(RealUnitedScalar(100.0, Unit("m")))
    
    distance_widget = IQtRealUnitedScalar(
        distance,
        distance_units
    )
    layout.addWidget(distance_widget)
    distance_display = IQtDisplayValue(
        distance,
        formatter=lambda x: f"Value: {x.value:.2f} {x.unit.format_string()}"
    )
    layout.addWidget(distance_display)
    
    # Temperature
    layout.addWidget(QLabel("<h3>Temperature:</h3>"))
    temp_units = {
        NamedQuantity.TEMPERATURE.dimension: {Unit("°C"), Unit("K"), Unit("°F")}
    }
    temperature = ObservableSingleValue(RealUnitedScalar(25.0, Unit("°C")))
    
    temp_widget = IQtRealUnitedScalar(
        temperature,
        temp_units
    )
    layout.addWidget(temp_widget)
    temp_display = IQtDisplayValue(
        temperature,
        formatter=lambda x: f"Temperature: {x.value:.1f} {x.unit.format_string()}"
    )
    layout.addWidget(temp_display)
    
    # Mass (with dynamic unit options)
    layout.addWidget(QLabel("<h3>Mass:</h3>"))
    mass_units_obs = {
        NamedQuantity.MASS.dimension: {Unit("kg"), Unit("g"), Unit("mg"), Unit("t"), Unit("lb")}
    }
    mass = ObservableSingleValue(RealUnitedScalar(5.5, Unit("kg")))
    
    mass_widget = IQtRealUnitedScalar(
        mass,
        mass_units_obs
    )
    layout.addWidget(mass_widget)
    mass_display = IQtDisplayValue(
        mass,
        formatter=lambda x: f"Mass: {x.value:.3f} {x.unit.format_string()}"
    )
    layout.addWidget(mass_display)
    
    # Buttons to change values programmatically
    def double_distance():
        current: RealUnitedScalar = distance.value
        distance.value = RealUnitedScalar(current.value() * 2, current.unit)
    
    def convert_temp_to_kelvin():
        current = temperature.value
        # Convert to Kelvin
        kelvin_value = current.scalar_in_unit(Unit("K"))
        temperature.value = kelvin_value
    
    double_button = QPushButton("Double Distance")
    double_button.clicked.connect(double_distance)
    layout.addWidget(double_button)
    
    convert_button = QPushButton("Convert Temp to Kelvin")
    convert_button.clicked.connect(convert_temp_to_kelvin)
    layout.addWidget(convert_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

