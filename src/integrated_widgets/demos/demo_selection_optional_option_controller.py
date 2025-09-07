#!/usr/bin/env python3
"""
Demo application for SelectionOptionalOptionController.

This demo showcases the SelectionOptionalOptionController with a combo box widget
that allows users to select from a predefined set of options OR select "None".
The controller manages the selection state and validates that the selected option
is always either None or within the available options set.

The demo includes:
1. A combo box for selecting from available options (including None)
2. Dynamic updates when available options change
3. Validation that selected options are always valid
4. Observable integration for real-time updates
5. Demonstration of None selection handling
"""

# Standard library imports
import sys
from typing import Optional
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QGroupBox
from PySide6.QtCore import Qt

# BAB imports
from observables import ObservableSingleValue, ObservableSet
from integrated_widgets import SelectionOptionalOptionController

# Local imports
from .utils import debug_logger


def main():
    """Main demo function."""
    # Use the debug logger from utils
    logger = debug_logger
    logger.info("Starting SelectionOptionalOptionController demo...")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("SelectionOptionalOptionController Demo")
    window.setGeometry(100, 100, 700, 600)
    
    # Create the central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add a title label
    title_label = QLabel("SelectionOptionalOptionController Demo")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title_label)
    
    # Create initial options for different data types
    # Country options (with None as valid selection)
    country_options: set[str] = {"USA", "Canada", "Germany", "France", "Japan", "Australia"}
    selected_country_observable: ObservableSingleValue[Optional[str]] = ObservableSingleValue("Germany")
    country_options_observable: ObservableSet[str] = ObservableSet(country_options)
    
    # Priority options (with None as valid selection)
    priority_options: set[str] = {"Low", "Medium", "High", "Critical"}
    selected_priority_observable: ObservableSingleValue[Optional[str]] = ObservableSingleValue(None)
    priority_options_observable: ObservableSet[str] = ObservableSet(priority_options)
    
    # Category options (with None as valid selection)
    category_options: set[str] = {"Electronics", "Clothing", "Books", "Sports", "Home"}
    selected_category_observable: ObservableSingleValue[Optional[str]] = ObservableSingleValue("Electronics")
    category_options_observable: ObservableSet[str] = ObservableSet(category_options)
    
    logger.info(f"Initial country selection: {selected_country_observable.value}")
    logger.info(f"Initial priority selection: {selected_priority_observable.value}")
    logger.info(f"Initial category selection: {selected_category_observable.value}")
    
    # Create controllers for different data types
    country_controller: SelectionOptionalOptionController[str] = SelectionOptionalOptionController[str](
        selected_option=selected_country_observable,
        available_options=country_options_observable,
        formatter=lambda c: f"🌍 {c}" if c else "🌍 None",
        none_option_label="🌍 No Country Selected",
        logger=logger
    )
    
    priority_controller: SelectionOptionalOptionController[str] = SelectionOptionalOptionController[str](
        selected_option=selected_priority_observable,
        available_options=priority_options_observable,
        formatter=lambda p: f"⚡ {p}" if p else "⚡ None",
        none_option_label="⚡ No Priority Set",
        logger=logger
    )
    
    category_controller: SelectionOptionalOptionController[str] = SelectionOptionalOptionController[str](
        selected_option=selected_category_observable,
        available_options=category_options_observable,
        formatter=lambda c: f"📦 {c}" if c else "📦 None",
        none_option_label="📦 No Category Assigned",
        logger=logger
    )
    
    # Add controllers to layout with group boxes
    country_group = QGroupBox("Country Selection (with None option)")
    country_layout = QVBoxLayout()
    country_layout.addWidget(country_controller.all_widgets_as_frame())
    country_group.setLayout(country_layout)
    layout.addWidget(country_group)
    
    priority_group = QGroupBox("Priority Selection (with None option)")
    priority_layout = QVBoxLayout()
    priority_layout.addWidget(priority_controller.all_widgets_as_frame())
    priority_group.setLayout(priority_layout)
    layout.addWidget(priority_group)
    
    category_group = QGroupBox("Category Selection (with None option)")
    category_layout = QVBoxLayout()
    category_layout.addWidget(category_controller.all_widgets_as_frame())
    category_group.setLayout(category_layout)
    layout.addWidget(category_group)
    
    # Add buttons to modify available options dynamically
    button_layout = QHBoxLayout()
    
    add_country_btn = QPushButton("Add 'Brazil' to countries")
    add_country_btn.clicked.connect(lambda: country_options_observable.value.add("Brazil"))
    button_layout.addWidget(add_country_btn)
    
    add_priority_btn = QPushButton("Add 'Urgent' to priorities")
    add_priority_btn.clicked.connect(lambda: priority_options_observable.value.add("Urgent"))
    button_layout.addWidget(add_priority_btn)
    
    add_category_btn = QPushButton("Add 'Food' to categories")
    add_category_btn.clicked.connect(lambda: category_options_observable.value.add("Food"))
    button_layout.addWidget(add_category_btn)
    
    layout.addLayout(button_layout)
    
    # Add buttons to set selections to None
    none_button_layout = QHBoxLayout()
    
    none_country_btn = QPushButton("Set Country to None")
    none_country_btn.clicked.connect(lambda: selected_country_observable.change_value(None))
    none_button_layout.addWidget(none_country_btn)
    
    none_priority_btn = QPushButton("Set Priority to None")
    none_priority_btn.clicked.connect(lambda: selected_priority_observable.change_value(None))
    none_button_layout.addWidget(none_priority_btn)
    
    none_category_btn = QPushButton("Set Category to None")
    none_category_btn.clicked.connect(lambda: selected_category_observable.change_value(None))
    none_button_layout.addWidget(none_category_btn)
    
    layout.addLayout(none_button_layout)
    
    # Add some information about what to test
    info_label = QLabel(
        "Test the controller by:\n"
        "1. Selecting different options from each combo box\n"
        "2. Selecting 'None' from the dropdown (first option)\n"
        "3. Adding new options using the buttons above\n"
        "4. Using the 'Set to None' buttons to clear selections\n"
        "5. Observing how the combo boxes update dynamically\n"
        "6. Notice the custom formatters and None labels for each data type"
    )
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_label.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
    layout.addWidget(info_label)
    
    # Show the window
    window.show()
    logger.info("Demo window opened successfully!")
    
    try:
        # Run the application
        return app.exec()
    except Exception as e:
        logger.error(f"Error running demo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
