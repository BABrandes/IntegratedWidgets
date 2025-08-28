#!/usr/bin/env python3
"""
Demo application for SelectionOptionController.

This demo showcases the SelectionOptionController with a combo box widget
that allows users to select from a predefined set of options. The controller
manages the selection state and validates that the selected option is always
within the available options set.

The demo includes:
1. A combo box for selecting from available options
2. Dynamic updates when available options change
3. Validation that selected options are always valid
4. Observable integration for real-time updates
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

# BAB imports
from observables import ObservableSingleValue, ObservableSet
from integrated_widgets import SelectionOptionController

# Local imports
from .utils import debug_logger


def main():
    """Main demo function."""
    # Use the debug logger from utils
    logger = debug_logger
    logger.info("Starting SelectionOptionController demo...")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("SelectionOptionController Demo")
    window.setGeometry(100, 100, 600, 500)
    
    # Create the central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add a title label
    title_label = QLabel("SelectionOptionController Demo")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title_label)
    
    # Create initial options for different data types
    # String options
    string_options = {"Apple", "Banana", "Cherry", "Date", "Elderberry"}
    selected_string_observable = ObservableSingleValue("Apple")
    string_options_observable = ObservableSet(string_options)
    
    # Integer options
    number_options = {1, 2, 3, 5, 8, 13, 21}
    selected_number_observable = ObservableSingleValue(5)
    number_options_observable = ObservableSet(number_options)
    
    # Color options
    color_options = {"Red", "Green", "Blue", "Yellow", "Purple", "Orange"}
    selected_color_observable = ObservableSingleValue("Blue")
    color_options_observable = ObservableSet(color_options)
    
    logger.info(f"Initial string selection: {selected_string_observable.single_value}")
    logger.info(f"Initial number selection: {selected_number_observable.single_value}")
    logger.info(f"Initial color selection: {selected_color_observable.single_value}")
    
    # Create controllers for different data types
    string_controller = SelectionOptionController(
        selected_option=selected_string_observable,
        available_options=string_options_observable,
        formatter=lambda s: f"🍎 {s}",
        logger=logger
    )
    
    number_controller = SelectionOptionController(
        selected_option=selected_number_observable,
        available_options=number_options_observable,
        formatter=lambda n: f"#{n:02d}",
        logger=logger
    )
    
    color_controller = SelectionOptionController(
        selected_option=selected_color_observable,
        available_options=color_options_observable,
        formatter=lambda c: f"🎨 {c}",
        logger=logger
    )
    
    # Add controllers to layout
    layout.addWidget(QLabel("String Selection (with emoji formatter):"))
    layout.addWidget(string_controller.all_widgets_as_frame())
    
    layout.addWidget(QLabel("Number Selection (with number formatter):"))
    layout.addWidget(number_controller.all_widgets_as_frame())
    
    layout.addWidget(QLabel("Color Selection (with color formatter):"))
    layout.addWidget(color_controller.all_widgets_as_frame())
    
    # Add buttons to modify available options dynamically
    button_layout = QHBoxLayout()
    
    add_string_btn = QPushButton("Add 'Fig' to strings")
    add_string_btn.clicked.connect(lambda: string_options_observable.set_value.add("Fig"))
    button_layout.addWidget(add_string_btn)
    
    add_number_btn = QPushButton("Add '34' to numbers")
    add_number_btn.clicked.connect(lambda: number_options_observable.set_value.add(34))
    button_layout.addWidget(add_number_btn)
    
    add_color_btn = QPushButton("Add 'Pink' to colors")
    add_color_btn.clicked.connect(lambda: color_options_observable.set_value.add("Pink"))
    button_layout.addWidget(add_color_btn)
    
    layout.addLayout(button_layout)
    
    # Add some information about what to test
    info_label = QLabel(
        "Test the controller by:\n"
        "1. Selecting different options from each combo box\n"
        "2. Adding new options using the buttons above\n"
        "3. Observing how the combo boxes update dynamically\n"
        "4. Notice the custom formatters for each data type"
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
