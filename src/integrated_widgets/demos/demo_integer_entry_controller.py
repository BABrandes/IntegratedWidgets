#!/usr/bin/env python3
"""
Demo application for IntegerEntryController.

This demo showcases the IntegerEntryController with multiple integer entry widgets
that demonstrate various features including:
1. Basic integer entry functionality
2. Custom validation (positive numbers, even numbers, range validation)
3. Observable integration for real-time updates
4. Different initialization patterns (direct value, observable, hook)
5. Signal handling and state synchronization

The demo includes:
1. Individual integer entries with different validation rules
2. Dynamic updates when values change programmatically
3. Real-time logging of all state changes
4. Validation feedback and error handling
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QGroupBox
from PySide6.QtCore import Qt

# BAB imports
from observables import ObservableSingleValue
from integrated_widgets import IntegerEntryController

# Local imports
from .utils import debug_logger


def main():
    """Main demo function."""
    # Use the debug logger from utils
    logger = debug_logger
    logger.info("Starting IntegerEntryController demo...")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("IntegerEntryController Demo")
    window.setGeometry(100, 100, 800, 600)
    
    # Create the central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add a title label
    title_label = QLabel("IntegerEntryController Demo")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title_label)
    
    # Create observable values for different integer entries
    logger.info("Creating observable values for integer entries...")
    
    # Basic integer entry with no validation
    basic_integer_observable = ObservableSingleValue(42)
    
    # Positive integer entry with validation
    positive_integer_observable = ObservableSingleValue(100)
    
    # Even integer entry with validation
    even_integer_observable = ObservableSingleValue(24)
    
    # Range-limited integer entry with validation (0-100)
    range_integer_observable = ObservableSingleValue(50)
    
    logger.info(f"Initial basic integer value: {basic_integer_observable.value}")
    logger.info(f"Initial positive integer value: {positive_integer_observable.value}")
    logger.info(f"Initial even integer value: {even_integer_observable.value}")
    logger.info(f"Initial range integer value: {range_integer_observable.value}")
    
    # Create controllers for different integer entries
    logger.info("Creating IntegerEntryController instances...")
    
    # Basic integer entry with no validation
    basic_controller = IntegerEntryController(
        value=basic_integer_observable,
        logger=logger
    )
    
    # Positive integer entry with validation
    positive_controller = IntegerEntryController(
        value=positive_integer_observable,
        validator=lambda x: x > 0,
        logger=logger
    )
    
    # Even integer entry with validation
    even_controller = IntegerEntryController(
        value=even_integer_observable,
        validator=lambda x: x % 2 == 0,
        logger=logger
    )
    
    # Range-limited integer entry with validation (0-100)
    range_controller = IntegerEntryController(
        value=range_integer_observable,
        validator=lambda x: 0 <= x <= 100,
        logger=logger
    )
    
    # Create control buttons
    logger.info("Creating control buttons...")
    
    # Button to set basic integer to a random value
    set_basic_button = QPushButton("Set Basic to 123")
    set_basic_button.clicked.connect(lambda: basic_integer_observable.change_value(123))
    
    # Button to set positive integer
    set_positive_button = QPushButton("Set Positive to 200")
    set_positive_button.clicked.connect(lambda: positive_integer_observable.change_value(200))
    
    # Button to set even integer
    set_even_button = QPushButton("Set Even to 36")
    set_even_button.clicked.connect(lambda: even_integer_observable.change_value(36))
    
    # Button to set range integer
    set_range_button = QPushButton("Set Range to 75")
    set_range_button.clicked.connect(lambda: range_integer_observable.change_value(75))
    
    # Button to test validation failure
    test_validation_button = QPushButton("Test Validation (set -5)")
    test_validation_button.clicked.connect(lambda: positive_integer_observable.change_value(-5))
    
    # Create groups for better organization
    logger.info("Organizing widgets into groups...")
    
    # Individual integer entries group
    individual_group = QGroupBox("Integer Entries with Different Validation Rules")
    individual_layout = QVBoxLayout(individual_group)
    
    # Add labels and controllers
    individual_layout.addWidget(QLabel("Basic Integer (no validation):"))
    individual_layout.addWidget(basic_controller.all_widgets_as_frame())
    
    individual_layout.addWidget(QLabel("Positive Integer (must be > 0):"))
    individual_layout.addWidget(positive_controller.all_widgets_as_frame())
    
    individual_layout.addWidget(QLabel("Even Integer (must be even):"))
    individual_layout.addWidget(even_controller.all_widgets_as_frame())
    
    individual_layout.addWidget(QLabel("Range Integer (must be 0-100):"))
    individual_layout.addWidget(range_controller.all_widgets_as_frame())
    
    # Control buttons group
    control_group = QGroupBox("Control Buttons")
    control_layout = QVBoxLayout(control_group)
    
    # Create button rows
    button_row1 = QHBoxLayout()
    button_row1.addWidget(set_basic_button)
    button_row1.addWidget(set_positive_button)
    
    button_row2 = QHBoxLayout()
    button_row2.addWidget(set_even_button)
    button_row2.addWidget(set_range_button)
    
    button_row3 = QHBoxLayout()
    button_row3.addWidget(test_validation_button)
    
    control_layout.addLayout(button_row1)
    control_layout.addLayout(button_row2)
    control_layout.addLayout(button_row3)
    
    # Add all groups to main layout
    layout.addWidget(individual_group)
    layout.addWidget(control_group)
    
    # Add status information
    status_label = QLabel("Status: All integer entries are functional and validated")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
    layout.addWidget(status_label)
    
    # Add some information about what to test
    info_label = QLabel(
        "Test the controller by:\n"
        "1. Typing different values in each entry field\n"
        "2. Using the control buttons to set values programmatically\n"
        "3. Testing validation by entering invalid values (e.g., -5 for positive)\n"
        "4. Observing how the entries update dynamically\n"
        "5. Notice the different validation rules for each entry"
    )
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_label.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
    layout.addWidget(info_label)
    
    logger.info("Demo window setup completed successfully")
    
    # Show the window
    window.show()
    logger.info("Demo window displayed")
    
    try:
        # Run the application
        return app.exec()
    except Exception as e:
        logger.error(f"Error running demo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
