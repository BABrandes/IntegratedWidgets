#!/usr/bin/env python3
"""Demo application for IQtDictOptionalSelection widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
from observables import ObservableSingleValue, ObservableOptionalSelectionDict

from integrated_widgets import IQtDictOptionalSelection, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtDictOptionalSelection Demo")
    window.resize(600, 500)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtDictOptionalSelection Demo</h2>"))
    layout.addWidget(QLabel("Select keys from dictionaries with optional None selection"))
    
    # Country-capital dictionary
    layout.addWidget(QLabel("<b>Country-Capital Dictionary:</b>"))
    countries = {
        "USA": "Washington D.C.",
        "UK": "London", 
        "Germany": "Berlin",
        "France": "Paris",
        "Japan": "Tokyo",
        "Australia": "Canberra"
    }
    country_selected = ObservableSingleValue[str | None](None)
    
    country_widget = IQtDictOptionalSelection(
        countries,
        country_selected,
        formatter=lambda key: f"{key} ({countries[key]})",
        none_option_text="- Select Country -"
    )
    layout.addWidget(country_widget)
    
    # Display selected country and capital
    country_display = IQtDisplayValue(
        country_selected,
        formatter=lambda key: f"Selected: {key if key else 'None'}"
    )
    layout.addWidget(country_display)
    
    capital_display = IQtDisplayValue(
        country_widget.selected_value_hook,
        formatter=lambda capital: f"Capital: {capital if capital else 'None'}"
    )
    layout.addWidget(capital_display)
    
    # Color-hex dictionary
    layout.addWidget(QLabel("<b>Color-Hex Dictionary:</b>"))
    colors = {
        "red": "#FF0000",
        "green": "#00FF00", 
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "purple": "#800080",
        "orange": "#FFA500"
    }
    color_observable = ObservableOptionalSelectionDict[str, str](colors, None)
    
    color_widget = IQtDictOptionalSelection(
        color_observable,
        None,
        None,
        formatter=lambda color: f"{color.upper()}",
        none_option_text="(no color selected)"
    )
    layout.addWidget(color_widget)
    
    # Display selected color and hex
    color_display = IQtDisplayValue(
        color_observable.key_hook,
        formatter=lambda color: f"Color: {color if color else 'None'}"
    )
    layout.addWidget(color_display)
    
    hex_display = IQtDisplayValue(
        color_observable.value_hook,
        formatter=lambda hex_val: f"Hex: {hex_val if hex_val else 'None'}"
    )
    layout.addWidget(hex_display)
    
    # Size-price dictionary
    layout.addWidget(QLabel("<b>T-shirt Size-Price Dictionary:</b>"))
    sizes = {
        "XS": 15.99,
        "S": 16.99,
        "M": 17.99, 
        "L": 18.99,
        "XL": 19.99,
        "XXL": 20.99
    }
    size_selected = ObservableSingleValue[str | None]("M")
    
    size_widget = IQtDictOptionalSelection(
        sizes,
        size_selected,
        formatter=lambda size: f"{size} - ${sizes[size]:.2f}",
        none_option_text="(no size selected)"
    )
    layout.addWidget(size_widget)
    
    # Display selected size and price
    size_display = IQtDisplayValue(
        size_selected,
        formatter=lambda size: f"Size: {size if size else 'None'}"
    )
    layout.addWidget(size_display)
    
    price_display = IQtDisplayValue(
        size_widget.selected_value_hook,
        formatter=lambda price: f"Price: ${price:.2f}" if price is not None else "Price: None"
    )
    layout.addWidget(price_display)
    
    # Control buttons
    button_layout = QHBoxLayout()
    
    def clear_all():
        country_widget.selected_key = None
        color_widget.selected_key = None
        size_widget.selected_key = None
    
    def set_defaults():
        country_widget.selected_key = "Germany"
        color_widget.selected_key = "blue"
        size_widget.selected_key = "L"
    
    def modify_dicts():
        # Add new entries to demonstrate dynamic updates
        countries["Canada"] = "Ottawa"
        colors["pink"] = "#FFC0CB"
        sizes["XXXL"] = 21.99
    
    clear_button = QPushButton("Clear All Selections")
    clear_button.clicked.connect(clear_all)
    button_layout.addWidget(clear_button)
    
    defaults_button = QPushButton("Set Defaults")
    defaults_button.clicked.connect(set_defaults)
    button_layout.addWidget(defaults_button)
    
    modify_button = QPushButton("Add New Entries")
    modify_button.clicked.connect(modify_dicts)
    button_layout.addWidget(modify_button)
    
    layout.addLayout(button_layout)
    
    # Dict-like interface demo
    layout.addWidget(QLabel("<b>Dict-like Interface Demo:</b>"))
    
    def demo_dict_interface():
        # Demonstrate dict-like operations
        print("=== Dict Interface Demo ===")
        print(f"Country widget length: {len(country_widget)}")
        print(f"Country widget keys: {list(country_widget.keys())}")
        print(f"Country widget values: {list(country_widget.values())}")
        print(f"Country widget items: {list(country_widget.items())}")
        print(f"'USA' in country_widget: {'USA' in country_widget}")
        print(f"country_widget.get('France'): {country_widget.get('France')}")
        print(f"country_widget.get('NonExistent'): {country_widget.get('NonExistent')}")
        
        # Demonstrate modification
        country_widget["Spain"] = "Madrid"
        print(f"After adding Spain: {list(country_widget.keys())}")
        
        # Demonstrate deletion
        if "Spain" in country_widget:
            del country_widget["Spain"]
            print(f"After deleting Spain: {list(country_widget.keys())}")
        else:
            print("Spain not found in widget (as expected)")
        
        # Demonstrate update
        country_widget.update({"Italy": "Rome", "Brazil": "Brasilia"})
        print(f"After update: {list(country_widget.keys())}")
        
        print("=== End Demo ===")
    
    demo_button = QPushButton("Demo Dict Interface (Check Console)")
    demo_button.clicked.connect(demo_dict_interface)
    layout.addWidget(demo_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
