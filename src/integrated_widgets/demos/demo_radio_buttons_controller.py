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
from observables import ObservableSingleValue, ObservableSet, InitialSyncMode
from integrated_widgets import RadioButtonsController, DisplayValueController

# Local imports
from .utils import debug_logger

def main() -> int:
    """Main function to run the demo."""
    debug_logger.info("Starting RadioButtonsController demo")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("RadioButtonsController Demo")
    window.setGeometry(100, 100, 600, 500)
    
    # Create central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    
    # Create observable for string options
    string_options = {"Apple", "Banana", "Cherry", "Date", "Elderberry"}
    string_selected = ObservableSingleValue("Apple")
    string_available = ObservableSet(string_options)
    
    # Create observable for number options
    number_options = {1, 2, 3, 4, 5}
    number_selected = ObservableSingleValue(3)
    number_available = ObservableSet(number_options)
    
    # Create observable for enum-like options
    enum_options = {"Red", "Green", "Blue", "Yellow", "Purple"}
    enum_selected = ObservableSingleValue("Blue")
    enum_available = ObservableSet(enum_options)
    
    debug_logger.info("Creating RadioButtonsController instances...")
    
    # Create controllers
    string_controller = RadioButtonsController(
        string_selected,
        string_available,
        formatter=lambda x: f"🍎 {x}",
        logger=debug_logger
    )
    
    number_controller = RadioButtonsController(
        number_selected,
        number_available,
        formatter=lambda x: f"#{x}",
        logger=debug_logger
    )
    
    enum_controller = RadioButtonsController(
        enum_selected,
        enum_available,
        formatter=lambda x: f"🎨 {x}",
        logger=debug_logger
    )
    
    debug_logger.info("Creating control buttons...")
    
    # Button to change string selection
    change_string_button = QPushButton("Change String to 'Cherry'")
    change_string_button.clicked.connect(lambda: string_controller.change_selected_option("Cherry"))
    
    # Button to change number selection
    change_number_button = QPushButton("Change Number to 5")
    change_number_button.clicked.connect(lambda: number_controller.change_selected_option(5))
    
    # Button to change enum selection
    change_enum_button = QPushButton("Change Color to 'Red'")
    change_enum_button.clicked.connect(lambda: enum_controller.change_selected_option("Red"))
    
    # Button to add new option
    add_option_button = QPushButton("Add 'Orange' to Fruits")
    add_option_button.clicked.connect(lambda: string_controller.add_option("Orange"))
    
    # Button to remove option
    remove_option_button = QPushButton("Remove 'Date' from Fruits")
    remove_option_button.clicked.connect(lambda: string_controller.remove_option("Date"))
    
    # Button to change available options
    change_options_button = QPushButton("Change Numbers to 0 to 6")
    change_options_button.clicked.connect(lambda: number_controller.change_available_options({0, 1, 2, 3, 4, 5, 6}))
    
    # Button to change both at once
    change_both_button = QPushButton("Change Color to 'Green' and Add 'Pink'")
    change_both_button.clicked.connect(lambda: enum_controller.change_selected_option_and_available_options("Green", {"Red", "Green", "Blue", "Yellow", "Purple", "Pink"}))
    
    debug_logger.info("Organizing widgets into groups...")
    
    # Create groups for better organization
    string_group = QGroupBox("Fruit Selection (String Options)")
    string_layout = QVBoxLayout()
    string_group.setLayout(string_layout)
    string_layout.addWidget(string_controller.all_widgets_as_frame())
    string_layout.addWidget(change_string_button)
    string_layout.addWidget(add_option_button)
    string_layout.addWidget(remove_option_button)
    
    number_group = QGroupBox("Number Selection (Integer Options)")
    number_layout = QVBoxLayout()
    number_group.setLayout(number_layout)
    number_layout.addWidget(number_controller.all_widgets_as_frame())
    number_layout.addWidget(change_number_button)
    number_layout.addWidget(change_options_button)
    
    enum_group = QGroupBox("Color Selection (Enum-like Options)")
    enum_layout = QVBoxLayout()
    enum_group.setLayout(enum_layout)
    enum_layout.addWidget(enum_controller.all_widgets_as_frame())
    enum_layout.addWidget(change_enum_button)
    enum_layout.addWidget(change_both_button)
    
    # Add groups to main layout
    main_layout.addWidget(string_group)
    main_layout.addWidget(number_group)
    main_layout.addWidget(enum_group)
    
    # Add status labels
    status_layout = QHBoxLayout()
    
    string_status: DisplayValueController[str] = DisplayValueController[str](string_controller.selected_option)
    string_selected.single_value_hook.connect_to(string_status.single_value_hook, sync_mode=InitialSyncMode.PULL_FROM_TARGET)
    
    number_status: DisplayValueController[int] = DisplayValueController[int](number_controller.selected_option)
    number_selected.single_value_hook.connect_to(number_status.single_value_hook, sync_mode=InitialSyncMode.PULL_FROM_TARGET)
    
    enum_status: DisplayValueController[str] = DisplayValueController[str](enum_controller.selected_option)
    enum_selected.single_value_hook.connect_to(enum_status.single_value_hook, sync_mode=InitialSyncMode.PULL_FROM_TARGET)
    
    status_layout.addWidget(string_status.widget_label)
    status_layout.addWidget(number_status.widget_label)
    status_layout.addWidget(enum_status.widget_label)
    
    main_layout.addLayout(status_layout)
    
    debug_logger.info("Demo window setup completed successfully")
    
    # Show the window
    window.show()
    debug_logger.info("Demo window displayed")
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
