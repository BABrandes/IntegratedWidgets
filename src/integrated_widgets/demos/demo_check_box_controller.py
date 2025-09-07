#!/usr/bin/env python3
"""
Demo application for CheckBoxController.

This demo showcases the CheckBoxController with multiple checkbox widgets
that demonstrate various features including:
1. Basic checkbox functionality with custom text
2. Different initialization patterns (direct value, observable)
3. Observable integration for real-time updates
4. Signal handling and state synchronization

The demo includes:
1. Individual checkboxes with different initial states
2. Dynamic updates when values change programmatically
3. Real-time logging of all state changes
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QGroupBox
from PySide6.QtCore import Qt
from observables import ObservableSingleValue

# BAB imports
from observables import ObservableSingleValue
from integrated_widgets import CheckBoxController

# Local imports
from .utils import debug_logger


def main():
    """Main demo function."""
    # Use the debug logger from utils
    logger = debug_logger
    logger.info("Starting CheckBoxController demo...")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("CheckBoxController Demo")
    window.setGeometry(100, 100, 800, 600)
    
    # Create the central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add a title label
    title_label = QLabel("CheckBoxController Demo")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title_label)
    
    # Create observable values for different checkboxes
    logger.info("Creating observable values for checkboxes...")
    
    # Basic checkbox with direct boolean value
    basic_checkbox_observable = ObservableSingleValue(False)
    
    # Checkbox with initial True value
    enabled_checkbox_observable = ObservableSingleValue(True)
    
    # Checkbox for user preferences
    preferences_checkbox_observable = ObservableSingleValue(False)
    
    # Checkbox for system settings
    system_checkbox_observable = ObservableSingleValue(True)
    
    logger.info(f"Initial basic checkbox value: {basic_checkbox_observable.value}")
    logger.info(f"Initial enabled checkbox value: {enabled_checkbox_observable.value}")
    logger.info(f"Initial preferences checkbox value: {preferences_checkbox_observable.value}")
    logger.info(f"Initial system checkbox value: {system_checkbox_observable.value}")
    
    # Create controllers for different checkboxes
    logger.info("Creating CheckBoxController instances...")
    
    # Basic checkbox with custom text
    basic_controller = CheckBoxController(
        value=basic_checkbox_observable,
        text="Basic Checkbox (starts unchecked)",
        logger=logger
    )
    
    # Enabled checkbox with custom text
    enabled_controller = CheckBoxController(
        value=enabled_checkbox_observable,
        text="Enabled Checkbox (starts checked)",
        logger=logger
    )
    
    # Preferences checkbox with custom text
    preferences_controller = CheckBoxController(
        value=preferences_checkbox_observable,
        text="User Preferences (starts unchecked)",
        logger=logger
    )
    
    # System settings checkbox with custom text
    system_controller = CheckBoxController(
        value=system_checkbox_observable,
        text="System Settings (starts checked)",
        logger=logger
    )
    
    # Create control buttons
    logger.info("Creating control buttons...")
    
    # Button to toggle basic checkbox
    toggle_basic_button = QPushButton("Toggle Basic Checkbox")
    toggle_basic_button.clicked.connect(lambda: basic_checkbox_observable.change_value(not basic_checkbox_observable.value))
    
    # Button to toggle enabled checkbox
    toggle_enabled_button = QPushButton("Toggle Enabled Checkbox")
    toggle_enabled_button.clicked.connect(lambda: enabled_checkbox_observable.change_value(not enabled_checkbox_observable.value))
    
    # Button to toggle preferences checkbox
    toggle_preferences_button = QPushButton("Toggle Preferences Checkbox")
    toggle_preferences_button.clicked.connect(lambda: preferences_checkbox_observable.change_value(not preferences_checkbox_observable.value))
    
    # Button to toggle system checkbox
    toggle_system_button = QPushButton("Toggle System Checkbox")
    toggle_system_button.clicked.connect(lambda: system_checkbox_observable.change_value(not system_checkbox_observable.value))
    
    # Create groups for better organization
    logger.info("Organizing widgets into groups...")
    
    # Individual checkboxes group
    individual_group = QGroupBox("Individual Checkboxes")
    individual_layout = QVBoxLayout(individual_group)
    
    individual_layout.addWidget(basic_controller.all_widgets_as_frame())
    individual_layout.addWidget(enabled_controller.all_widgets_as_frame())
    individual_layout.addWidget(preferences_controller.all_widgets_as_frame())
    individual_layout.addWidget(system_controller.all_widgets_as_frame())
    
    # Control buttons group
    control_group = QGroupBox("Control Buttons")
    control_layout = QVBoxLayout(control_group)
    
    # Create button rows
    button_row1 = QHBoxLayout()
    button_row1.addWidget(toggle_basic_button)
    button_row1.addWidget(toggle_enabled_button)
    
    button_row2 = QHBoxLayout()
    button_row2.addWidget(toggle_preferences_button)
    button_row2.addWidget(toggle_system_button)
    
    control_layout.addLayout(button_row1)
    control_layout.addLayout(button_row2)
    
    # Add all groups to main layout
    layout.addWidget(individual_group)
    layout.addWidget(control_group)
    
    # Add status information
    status_label = QLabel("Status: All checkboxes are functional and synchronized")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
    layout.addWidget(status_label)
    
    # Add some information about what to test
    info_label = QLabel(
        "Test the controller by:\n"
        "1. Clicking on different checkboxes to change their state\n"
        "2. Using the toggle buttons to change values programmatically\n"
        "3. Observing how the checkboxes update dynamically\n"
        "4. Notice the custom text for each checkbox"
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
