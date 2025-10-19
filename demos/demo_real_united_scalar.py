#!/usr/bin/env python3
"""Demo application for IQtRealUnitedScalar widget."""

import sys
from typing import Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QPushButton, QHBoxLayout, QGridLayout
)
from observables import ObservableSingleValue, ObservableDict
from united_system import RealUnitedScalar, Unit, NamedQuantity, Dimension

from integrated_widgets import IQtRealUnitedScalar
from integrated_widgets.iqt_widgets.iqt_real_united_scalar import Controller_Payload

DEBOUNCE_MS = None

def simple_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Simple horizontal layout: label + line edit + combobox."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    layout.addWidget(payload.label)
    layout.addWidget(payload.line_edit)
    layout.addWidget(payload.combobox)
    layout.addWidget(payload.editable_combobox)
    
    return widget


def detailed_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Detailed layout: all widgets in a grid."""
    widget = QWidget()
    layout = QGridLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Row 0: Label
    layout.addWidget(QLabel("<b>Current Value:</b>"), 0, 0)
    layout.addWidget(payload.label, 0, 1, 1, 2)
    
    # Row 1: Line Edit
    layout.addWidget(QLabel("Edit Value:"), 1, 0)
    layout.addWidget(payload.line_edit, 1, 1, 1, 2)
    
    # Row 2: Unit Selector
    layout.addWidget(QLabel("Change Unit:"), 2, 0)
    layout.addWidget(payload.combobox, 2, 1, 1, 2)
    
    return widget


def compact_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Compact layout: just line edit and combobox."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    layout.addWidget(payload.line_edit, 2)
    layout.addWidget(payload.combobox, 1)
    
    return widget


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
    layout.addWidget(QLabel("Demonstrating custom layout strategies with set_layout_strategy()"))

    # Shared available units for all widgets
    available_units = {
        NamedQuantity.LENGTH.dimension: frozenset({Unit("m"), Unit("cm"), Unit("mm"), Unit("km"), Unit("in")}),
        NamedQuantity.TEMPERATURE.dimension: frozenset({Unit("°C"), Unit("K"), Unit("°F")}),
        NamedQuantity.MASS.dimension: frozenset({Unit("kg"), Unit("g"), Unit("mg"), Unit("t"), Unit("lb")})
    }
    obs_available_units = ObservableDict[Dimension, frozenset[Unit]](available_units)

    # Distance measurement with simple horizontal layout
    layout.addWidget(QLabel("<h3>1. Simple Layout (label + edit + unit):</h3>"))
    distance = ObservableSingleValue(RealUnitedScalar(100.0, Unit("m")))
    
    distance_widget = IQtRealUnitedScalar(
        distance,
        obs_available_units,
        debounce_ms=DEBOUNCE_MS
    )
    # Apply simple layout strategy
    distance_widget.set_layout_strategy(lambda payload, **_: simple_layout_strategy(payload))
    layout.addWidget(distance_widget)
    
    # Temperature with detailed grid layout
    layout.addWidget(QLabel("<h3>2. Detailed Layout (labeled grid):</h3>"))
    temperature = ObservableSingleValue(RealUnitedScalar(25.0, Unit("°C")))
    
    temp_widget = IQtRealUnitedScalar(
        temperature,
        obs_available_units,
        debounce_ms=DEBOUNCE_MS
    )
    # Apply detailed grid layout strategy
    temp_widget.set_layout_strategy(lambda payload, **_: detailed_layout_strategy(payload))
    layout.addWidget(temp_widget)
    
    # Mass with compact layout
    layout.addWidget(QLabel("<h3>3. Compact Layout (edit + unit only):</h3>"))
    mass = ObservableSingleValue(RealUnitedScalar(5.5, Unit("kg")))
    
    mass_widget = IQtRealUnitedScalar(
        mass,
        obs_available_units,
        debounce_ms=DEBOUNCE_MS
    )
    # Apply compact layout strategy
    mass_widget.set_layout_strategy(lambda payload, **_: compact_layout_strategy(payload))
    layout.addWidget(mass_widget)
    
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

