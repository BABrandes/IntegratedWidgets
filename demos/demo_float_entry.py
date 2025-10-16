#!/usr/bin/env python3
"""Demo application for IQtFloatEntry widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from observables import ObservableSingleValue

from integrated_widgets import IQtFloatEntry, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtFloatEntry Demo")
    window.resize(500, 400)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtFloatEntry Demo</h2>"))
    
    # Create observable float values
    temperature = ObservableSingleValue(25.5)
    percentage = ObservableSingleValue(75.0)
    price = ObservableSingleValue(99.99)
    
    # Float entry with range validation
    layout.addWidget(QLabel("<b>Temperature (-50 to 150°C):</b>"))
    temp_widget = IQtFloatEntry(
        temperature,
        validator=lambda x: -50.0 <= x <= 150.0
    )
    layout.addWidget(temp_widget)
    temp_display = IQtDisplayValue(temperature, formatter=lambda x: f"{x:.1f}°C")
    layout.addWidget(temp_display)
    
    # Percentage with validation
    layout.addWidget(QLabel("<b>Percentage (0-100%):</b>"))
    pct_widget = IQtFloatEntry(
        percentage,
        validator=lambda x: 0.0 <= x <= 100.0
    )
    layout.addWidget(pct_widget)
    pct_display = IQtDisplayValue(percentage, formatter=lambda x: f"{x:.1f}%")
    layout.addWidget(pct_display)
    
    # Price (positive values only)
    layout.addWidget(QLabel("<b>Price (positive only):</b>"))
    price_widget = IQtFloatEntry(
        price,
        validator=lambda x: x >= 0.0
    )
    layout.addWidget(price_widget)
    price_display = IQtDisplayValue(price, formatter=lambda x: f"${x:.2f}")
    layout.addWidget(price_display)
    
    # Button to set random values
    import random
    def randomize():
        temperature.value = random.uniform(-50, 150)
        percentage.value = random.uniform(0, 100)
        price.value = random.uniform(0, 999)
    
    random_button = QPushButton("Randomize Values")
    random_button.clicked.connect(randomize)
    layout.addWidget(random_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

