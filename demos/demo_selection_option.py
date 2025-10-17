#!/usr/bin/env python3
"""Demo application for IQtSelectionOption widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from observables import ObservableSingleValue, ObservableSelectionOption

from integrated_widgets import IQtSelectionOption, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtSelectionOption Demo")
    window.resize(500, 400)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtSelectionOption Demo</h2>"))
    
    # Simple selection
    layout.addWidget(QLabel("<b>Choose a color:</b>"))
    colors = {"red", "green", "blue", "yellow", "purple"}
    color = ObservableSingleValue("red")
    
    color_widget = IQtSelectionOption(
        color,
        colors,
        formatter=lambda x: x.upper()
    )
    layout.addWidget(color_widget)
    color_display = IQtDisplayValue(color, formatter=lambda x: f"Selected color: {x}")
    layout.addWidget(color_display)
    
    # Mode selection
    layout.addWidget(QLabel("<b>Operating mode:</b>"))
    modes = {"auto", "manual", "eco", "performance"}
    mode_observable = ObservableSelectionOption("auto", modes)
    
    mode_widget = IQtSelectionOption(mode_observable, None)
    layout.addWidget(mode_widget)
    mode_display = IQtDisplayValue(
        mode_observable.selected_option_hook,
        formatter=lambda x: f"Mode: {x.title()}"
    )
    layout.addWidget(mode_display)
    
    # Priority selection
    layout.addWidget(QLabel("<b>Priority level:</b>"))
    priorities = {"low", "medium", "high", "critical"}
    priority = ObservableSingleValue("medium")
    
    priority_widget = IQtSelectionOption(
        priority,
        priorities,
        formatter=lambda x: f"⚠️ {x.upper()}" if x == "critical" else f"Priority: {x.title()}"
    )
    layout.addWidget(priority_widget)
    priority_display = IQtDisplayValue(priority, formatter=lambda x: f"Current: {x}")
    layout.addWidget(priority_display)
    
    # Button to cycle through values
    def cycle_color():
        colors_list = list(colors)
        current_idx = colors_list.index(color.value)
        next_idx = (current_idx + 1) % len(colors_list)
        color.value = colors_list[next_idx]
    
    cycle_button = QPushButton("Cycle Color")
    cycle_button.clicked.connect(cycle_color)
    layout.addWidget(cycle_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

