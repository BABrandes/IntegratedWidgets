#!/usr/bin/env python3
"""Demo application for IQtCheckBox widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from observables import ObservableSingleValue

from integrated_widgets import IQtCheckBox, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtCheckBox Demo")
    window.resize(400, 300)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtCheckBox Demo</h2>"))
    
    # Create observable boolean values
    feature_enabled = ObservableSingleValue(True)
    debug_mode = ObservableSingleValue(False)
    auto_save = ObservableSingleValue(True)
    
    # Create checkbox widgets
    layout.addWidget(QLabel("<b>Checkboxes bound to observables:</b>"))
    checkbox1 = IQtCheckBox(feature_enabled, text="Enable Feature")
    checkbox2 = IQtCheckBox(debug_mode, text="Debug Mode")
    checkbox3 = IQtCheckBox(auto_save, text="Auto-save")
    
    layout.addWidget(checkbox1)
    layout.addWidget(checkbox2)
    layout.addWidget(checkbox3)
    
    # Display current values
    layout.addWidget(QLabel("<b>Current values:</b>"))
    display1 = IQtDisplayValue(feature_enabled, formatter=lambda x: f"Feature: {'ON' if x else 'OFF'}")
    display2 = IQtDisplayValue(debug_mode, formatter=lambda x: f"Debug: {'ON' if x else 'OFF'}")
    display3 = IQtDisplayValue(auto_save, formatter=lambda x: f"Auto-save: {'ON' if x else 'OFF'}")
    
    layout.addWidget(display1)
    layout.addWidget(display2)
    layout.addWidget(display3)
    
    # Button to toggle values programmatically
    def toggle_all():
        feature_enabled.value = not feature_enabled.value
        debug_mode.value = not debug_mode.value
        auto_save.value = not auto_save.value
    
    toggle_button = QPushButton("Toggle All")
    toggle_button.clicked.connect(toggle_all)
    layout.addWidget(toggle_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

