#!/usr/bin/env python3
"""
Demo for RadioButtonsController.

This demo shows how to use the RadioButtonsController with different types of options
and demonstrates the binding capabilities.
"""

# Standard library imports
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QGroupBox, QPushButton
)

# BAB imports
from observables import ObservableSingleValue, ObservableSet, write_report
from integrated_widgets import RadioButtonsController, DisplayValueController

# Local imports
try:
    from .utils import debug_logger
except ImportError:
    # Fallback for when running directly
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from utils import debug_logger # type: ignore

def main() -> int:
    """Main function to run the demo."""
    debug_logger.info("Starting RadioButtonsController demo")
    
    # Create the Qt application
    debug_logger.info("Creating Qt application")
    app = QApplication(sys.argv)
    
    # Create the main window
    debug_logger.info("Creating main window")
    window = QMainWindow()
    window.setWindowTitle("RadioButtonsController Demo")
    window.setGeometry(100, 100, 600, 500)
    
    # Create central widget and layout
    debug_logger.info("Setting up central widget and layout")
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    
    # Create observable for string options
    debug_logger.info("Creating string observables")
    string_options = {"Apple", "Banana", "Cherry", "Date", "Elderberry"}
    string_selected = ObservableSingleValue("Apple")
    string_available = ObservableSet(string_options)
    debug_logger.info(f"String options: {string_options}, selected: Apple")
    
    # Create observable for number options
    debug_logger.info("Creating number observables")
    number_options = {1, 2, 3, 4, 5}
    number_selected = ObservableSingleValue(3)
    number_available = ObservableSet(number_options)
    debug_logger.info(f"Number options: {number_options}, selected: 3")
    
    # Create observable for enum-like options
    debug_logger.info("Creating enum observables")
    enum_options = {"Red", "Green", "Blue", "Yellow", "Purple"}
    enum_selected = ObservableSingleValue("Blue")
    enum_available = ObservableSet(enum_options)
    debug_logger.info(f"Enum options: {enum_options}, selected: Blue")
    
    debug_logger.info("Creating RadioButtonsController instances...")
    
    # Create controllers
    debug_logger.info("Creating string controller")
    string_controller = RadioButtonsController(
        string_selected,
        string_available,
        formatter=lambda x: f"🍎 {x}",
        logger=debug_logger
    )
    debug_logger.info("String controller created successfully")
    
    debug_logger.info("Creating number controller")
    number_controller = RadioButtonsController(
        number_selected,
        number_available,
        formatter=lambda x: f"#{x}",
        logger=debug_logger
    )
    debug_logger.info("Number controller created successfully")
    
    debug_logger.info("Creating enum controller")
    enum_controller = RadioButtonsController(
        enum_selected,
        enum_available,
        formatter=lambda x: f"🎨 {x}",
        logger=debug_logger
    )
    debug_logger.info("Enum controller created successfully")
    
    debug_logger.info("Creating control buttons...")
    
    # Button to change string selection
    debug_logger.info("Creating string change button")
    change_string_button = QPushButton("Change String to 'Cherry'")
    change_string_button.clicked.connect(lambda: string_controller.change_selected_option("Cherry"))
    
    # Button to change number selection
    debug_logger.info("Creating number change button")
    change_number_button = QPushButton("Change Number to 5")
    change_number_button.clicked.connect(lambda: number_controller.change_selected_option(5))
    
    # Button to change enum selection
    debug_logger.info("Creating enum change button")
    change_enum_button = QPushButton("Change Color to 'Red'")
    change_enum_button.clicked.connect(lambda: enum_controller.change_selected_option("Red"))
    
    # Button to add new option
    debug_logger.info("Creating add option button")
    add_option_button = QPushButton("Add 'Orange' to Fruits")
    add_option_button.clicked.connect(lambda: string_controller.add_option("Orange"))
    
    # Button to remove option
    debug_logger.info("Creating remove option button")
    remove_option_button = QPushButton("Remove 'Date' from Fruits")
    remove_option_button.clicked.connect(lambda: string_controller.remove_option("Date"))
    
    # Button to change available options
    debug_logger.info("Creating change options button")
    change_options_button = QPushButton("Change Numbers to 0 to 6")
    change_options_button.clicked.connect(lambda: number_controller.change_available_options({0, 1, 2, 3, 4, 5, 6}))
    
    # Button to change both at once
    debug_logger.info("Creating change both button")
    change_both_button = QPushButton("Change Color to 'Green' and Add 'Pink'")
    change_both_button.clicked.connect(lambda: enum_controller.change_selected_option_and_available_options("Green", {"Red", "Green", "Blue", "Yellow", "Purple", "Pink"}))
    
    debug_logger.info("Organizing widgets into groups...")
    
    # Create groups for better organization
    debug_logger.info("Creating string group")
    string_group = QGroupBox("Fruit Selection (String Options)")
    string_layout = QVBoxLayout()
    string_group.setLayout(string_layout)
    string_layout.addWidget(string_controller.all_widgets_as_frame())
    string_layout.addWidget(change_string_button)
    string_layout.addWidget(add_option_button)
    string_layout.addWidget(remove_option_button)
    debug_logger.info("String group created and populated")
    
    debug_logger.info("Creating number group")
    number_group = QGroupBox("Number Selection (Integer Options)")
    number_layout = QVBoxLayout()
    number_group.setLayout(number_layout)
    number_layout.addWidget(number_controller.all_widgets_as_frame())
    number_layout.addWidget(change_number_button)
    number_layout.addWidget(change_options_button)
    debug_logger.info("Number group created and populated")
    
    debug_logger.info("Creating enum group")
    enum_group = QGroupBox("Color Selection (Enum-like Options)")
    enum_layout = QVBoxLayout()
    enum_group.setLayout(enum_layout)
    enum_layout.addWidget(enum_controller.all_widgets_as_frame())
    enum_layout.addWidget(change_enum_button)
    enum_layout.addWidget(change_both_button)
    debug_logger.info("Enum group created and populated")
    
    # Add groups to main layout
    debug_logger.info("Adding groups to main layout")
    main_layout.addWidget(string_group)
    main_layout.addWidget(number_group)
    main_layout.addWidget(enum_group)
    debug_logger.info("Groups added to main layout")
    
    # Add status labels
    debug_logger.info("Creating status display controllers")
    status_layout = QHBoxLayout()
    
    # Create DisplayValueController instances directly with the original observables
    # This ensures they automatically update when the observables change
    debug_logger.info("Creating string status display")
    string_status: DisplayValueController[str] = DisplayValueController[str](string_selected, logger=debug_logger)
    debug_logger.info("Creating number status display")
    number_status: DisplayValueController[int] = DisplayValueController[int](number_selected, logger=debug_logger)
    debug_logger.info("Creating enum status display")
    enum_status: DisplayValueController[str] = DisplayValueController[str](enum_selected, logger=debug_logger)
    
    debug_logger.info("Adding status widgets to layout")
    status_layout.addWidget(string_status.widget_label)
    status_layout.addWidget(number_status.widget_label)
    status_layout.addWidget(enum_status.widget_label)
    
    debug_logger.info("Adding status layout to main layout")
    main_layout.addLayout(status_layout)
    
    debug_logger.info("Demo window setup completed successfully")
    
    # Show the window
    debug_logger.info("Showing demo window")
    window.show()
    debug_logger.info("Demo window displayed")

    # Check that the hook system is correctly connected. Collect all the carries hooks.
    debug_logger.info("Checking hook system...")
    debug_logger.info(write_report(
        dict_of_carries_hooks={
            "string_controller": string_controller,
            "number_controller": number_controller,
            "enum_controller": enum_controller,
            "string_selected": string_selected,
            "number_selected": number_selected,
            "enum_selected": enum_selected,
            "string_status": string_status,
            "number_status": number_status,
            "enum_status": enum_status,
        }
    ))

    # Run the application
    debug_logger.info("Starting Qt application event loop")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
