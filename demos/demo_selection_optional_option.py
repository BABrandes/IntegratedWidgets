#!/usr/bin/env python3
"""Demo application for IQtSelectionOptionalOption widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from observables import ObservableSingleValue, ObservableOptionalSelectionOption

from integrated_widgets import IQtSelectionOptionalOption, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtSelectionOptionalOption Demo")
    window.resize(500, 450)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtSelectionOptionalOption Demo</h2>"))
    layout.addWidget(QLabel("None is a valid selection (shown as dash or custom text)"))
    
    # Optional color selection
    layout.addWidget(QLabel("<b>Favorite color (optional):</b>"))
    colors = {"red", "green", "blue", "yellow", "purple"}
    color = ObservableSingleValue[str | None](None)
    
    color_widget = IQtSelectionOptionalOption(
        color,
        colors,
        formatter=lambda x: x.upper(),
        none_option_text="- No preference -"
    )
    layout.addWidget(color_widget)
    color_display = IQtDisplayValue(
        color,
        formatter=lambda x: f"Selected: {x if x else 'None'}"
    )
    layout.addWidget(color_display)
    
    # Optional size selection
    layout.addWidget(QLabel("<b>T-shirt size (optional):</b>"))
    sizes = {"XS", "S", "M", "L", "XL", "XXL"}
    size_observable = ObservableOptionalSelectionOption[str](None, sizes)
    
    size_widget = IQtSelectionOptionalOption(
        size_observable,
        none_option_text="(not selected)"
    )
    layout.addWidget(size_widget)
    size_display = IQtDisplayValue(
        size_observable.selected_option_hook,
        formatter=lambda x: f"Size: {x if x else 'Not selected'}"
    )
    layout.addWidget(size_display)
    
    # Optional country selection
    layout.addWidget(QLabel("<b>Country (optional):</b>"))
    countries = {"USA", "UK", "Germany", "France", "Japan", "Australia"}
    country = ObservableSingleValue[str | None]("USA")
    
    country_widget = IQtSelectionOptionalOption(
        country,
        countries,
        none_option_text="- Select country -"
    )
    layout.addWidget(country_widget)
    country_display = IQtDisplayValue(
        country,
        formatter=lambda x: f"Country: {x if x else 'Not specified'}"
    )
    layout.addWidget(country_display)
    
    # Button to clear all selections
    def clear_all():
        color.value = None
        size_observable.selected_option = None
        country.value = None
    
    clear_button = QPushButton("Clear All Selections")
    clear_button.clicked.connect(clear_all)
    layout.addWidget(clear_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

