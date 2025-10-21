#!/usr/bin/env python3
"""Demo application for IQtUnitComboBox widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from nexpy import XValue, XDict
from united_system import Unit, Dimension

from integrated_widgets import IQtUnitComboBox, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtUnitComboBox Demo")
    window.resize(500, 400)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtUnitComboBox Demo</h2>"))
    
    # Length units
    layout.addWidget(QLabel("<b>Length Unit:</b>"))
    length_dimension = Unit("m").dimension
    length_units = {
        length_dimension: {Unit("m"), Unit("cm"), Unit("mm"), Unit("km"), Unit("in")}
    }
    selected_length_unit = XValue[Unit | None](Unit("m"))
    
    length_unit_widget = IQtUnitComboBox(
        selected_length_unit,
        length_units
    )
    layout.addWidget(length_unit_widget)
    length_display = IQtDisplayValue(
        selected_length_unit,
        formatter=lambda u: f"Selected: {u.format_string() if u else 'None'}"
    )
    layout.addWidget(length_display)
    
    # Temperature units
    layout.addWidget(QLabel("<b>Temperature Unit:</b>"))
    temperature_dimension = Unit("°C").dimension
    temp_units = {
        temperature_dimension: {Unit("°C"), Unit("K"), Unit("°F")}
    }
    selected_temp_unit = XValue[Unit | None](Unit("°C"))
    
    temp_unit_widget = IQtUnitComboBox(
        selected_temp_unit,
        temp_units
    )
    layout.addWidget(temp_unit_widget)
    temp_display = IQtDisplayValue(
        selected_temp_unit,
        formatter=lambda u: f"Selected: {u.format_string() if u else 'None'}"
    )
    layout.addWidget(temp_display)
    
    # Mass units with dynamic options
    layout.addWidget(QLabel("<b>Mass Unit (editable):</b>"))
    mass_dimension = Unit("kg").dimension
    mass_units_dict = XDict[Dimension, set[Unit]]({
        mass_dimension: {Unit("kg"), Unit("g"), Unit("mg"), Unit("t")}
    })
    selected_mass_unit = XValue[Unit | None](Unit("kg"))
    
    mass_unit_widget = IQtUnitComboBox(
        selected_mass_unit,
        mass_units_dict,
        blank_if_none=True
    )
    layout.addWidget(mass_unit_widget)
    mass_display = IQtDisplayValue(
        selected_mass_unit,
        formatter=lambda u: f"Selected: {u.format_string() if u else 'None'}"
    )
    layout.addWidget(mass_display)
    
    layout.addWidget(QLabel("<i>Tip: You can type custom units that get added to the list</i>"))
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

