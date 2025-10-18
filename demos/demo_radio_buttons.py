#!/usr/bin/env python3
"""Demo application for IQtRadioButtons widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from observables import ObservableSingleValue, ObservableSelectionOption

from integrated_widgets import IQtRadioButtons, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtRadioButtons Demo")
    window.resize(600, 500)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QHBoxLayout(central_widget)
    
    # Left column
    left_layout = QVBoxLayout()
    layout.addLayout(left_layout)
    
    # Title
    left_layout.addWidget(QLabel("<h2>IQtRadioButtons Demo</h2>"))
    
    # Size selection
    left_layout.addWidget(QLabel("<b>Pizza Size:</b>"))
    sizes = {"Small", "Medium", "Large", "Extra Large"}
    size = ObservableSingleValue("Medium")
    
    size_widget = IQtRadioButtons(
        size,
        sizes,
        sorter=lambda x: {"Small": 1, "Medium": 2, "Large": 3, "Extra Large": 4}[x]
    )
    left_layout.addWidget(size_widget)
    size_display = IQtDisplayValue(size, formatter=lambda x: f"Selected: {x}")
    left_layout.addWidget(size_display)
    
    # Difficulty selection
    left_layout.addWidget(QLabel("<b>Game Difficulty:</b>"))
    difficulties = {"Easy", "Normal", "Hard", "Expert"}
    difficulty_observable = ObservableSelectionOption("Normal", difficulties)
    
    difficulty_widget = IQtRadioButtons(
        difficulty_observable,
        None,
        formatter=lambda x: f"⭐ {x}" if x == "Expert" else x
    )
    left_layout.addWidget(difficulty_widget)
    difficulty_display = IQtDisplayValue(
        difficulty_observable.selected_option_hook,
        formatter=lambda x: f"Level: {x}"
    )
    left_layout.addWidget(difficulty_display)
    
    left_layout.addStretch()
    
    # Right column
    right_layout = QVBoxLayout()
    layout.addLayout(right_layout)
    
    # Transport mode
    right_layout.addWidget(QLabel("<b>Transport Mode:</b>"))
    transports = {"🚗 Car", "🚲 Bike", "🚶 Walk", "🚌 Bus", "🚊 Train"}
    transport = ObservableSingleValue("🚗 Car")
    
    transport_widget = IQtRadioButtons(
        transport,
        transports,
        sorter=lambda x: x
    )
    right_layout.addWidget(transport_widget)
    transport_display = IQtDisplayValue(transport, formatter=lambda x: f"Selected: {x}")
    right_layout.addWidget(transport_display)
    
    # Theme selection
    right_layout.addWidget(QLabel("<b>UI Theme:</b>"))
    themes = {"Light", "Dark", "Auto"}
    theme = ObservableSingleValue("Auto")
    
    theme_widget = IQtRadioButtons(theme, themes)
    right_layout.addWidget(theme_widget)
    theme_display = IQtDisplayValue(theme, formatter=lambda x: f"Theme: {x}")
    right_layout.addWidget(theme_display)
    
    right_layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

