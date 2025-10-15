#!/usr/bin/env python3
"""
Demo application for SingleListSelectionController.

This demo showcases the SingleListSelectionController with a list widget
that allows users to select a single item from a list of available options.
The controller manages the selection state and supports optional deselection.

The demo includes:
1. List widgets for selecting from available options
2. Dynamic updates when available options change
3. Support for optional deselection (click to deselect)
4. Custom formatters for display
5. Observable integration for real-time updates
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QGroupBox
from PySide6.QtCore import Qt

# BAB imports
from observables import ObservableSingleValue, ObservableSet
from integrated_widgets import SingleListSelectionController, DisplayValueController

# Local imports
from .utils import debug_logger


def main():
    """Main demo function."""
    # Use the debug logger from utils
    logger = debug_logger
    logger.info("Starting SingleListSelectionController demo...")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("SingleListSelectionController Demo")
    window.setGeometry(100, 100, 900, 700)
    
    # Create the central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    
    # Add a title label
    title_label = QLabel("SingleListSelectionController Demo")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    main_layout.addWidget(title_label)
    
    # Create initial options for different data types
    # String options - Fruits
    fruit_options = {"Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"}
    selected_fruit_observable = ObservableSingleValue[str|None]("Apple")
    fruit_options_observable = ObservableSet[str](fruit_options)
    
    # Integer options - Fibonacci numbers
    number_options = {1, 2, 3, 5, 8, 13, 21, 34}
    selected_number_observable = ObservableSingleValue[int|None](5)
    number_options_observable = ObservableSet[int](number_options)
    
    # Color options - with deselection disabled
    color_options = {"Red", "Green", "Blue", "Yellow", "Purple", "Orange"}
    selected_color_observable = ObservableSingleValue[str|None]("Blue")
    color_options_observable = ObservableSet[str](color_options)
    
    # Programming languages - with deselection allowed (can be None)
    language_options = {"Python", "JavaScript", "TypeScript", "Rust", "Go", "C++", "Java"}
    selected_language_observable = ObservableSingleValue[str|None]("Python")
    language_options_observable = ObservableSet[str](language_options)
    
    logger.info(f"Initial fruit selection: {selected_fruit_observable.value}")
    logger.info(f"Initial number selection: {selected_number_observable.value}")
    logger.info(f"Initial color selection: {selected_color_observable.value}")
    logger.info(f"Initial language selection: {selected_language_observable.value}")
    
    # Create horizontal layout for list controllers
    lists_layout = QHBoxLayout()
    
    # Create controllers for different data types
    
    # 1. Fruit controller with emoji formatter
    fruit_group = QGroupBox("Fruits (with deselection)")
    fruit_layout = QVBoxLayout(fruit_group)
    fruit_controller = SingleListSelectionController[str](
        selected_option=selected_fruit_observable,
        available_options=fruit_options_observable,
        formatter=lambda s: f"🍎 {s}",
        allow_deselection=True,
        logger=logger
    )
    fruit_layout.addWidget(fruit_controller.widget_list)
    lists_layout.addWidget(fruit_group)
    
    # 2. Number controller with number formatter
    number_group = QGroupBox("Fibonacci Numbers (with deselection)")
    number_layout = QVBoxLayout(number_group)
    number_controller = SingleListSelectionController(
        selected_option=selected_number_observable,
        available_options=number_options_observable,
        formatter=lambda n: f"#{n:03d}",
        order_by_callable=lambda n: n,  # Sort numerically
        allow_deselection=True,
        logger=logger
    )
    number_layout.addWidget(number_controller.widget_list)
    lists_layout.addWidget(number_group)
    
    main_layout.addLayout(lists_layout)
    
    # Create second row of lists
    lists_layout2 = QHBoxLayout()
    
    # 3. Color controller WITHOUT deselection
    color_group = QGroupBox("Colors (NO deselection - always selected)")
    color_layout = QVBoxLayout(color_group)
    color_controller = SingleListSelectionController(
        selected_option=selected_color_observable,
        available_options=color_options_observable,
        formatter=lambda c: f"🎨 {c}",
        allow_deselection=False,  # Cannot deselect!
        logger=logger
    )
    color_layout.addWidget(color_controller.widget_list)
    lists_layout2.addWidget(color_group)
    
    # 4. Language controller with deselection
    language_group = QGroupBox("Programming Languages (with deselection)")
    language_layout = QVBoxLayout(language_group)
    language_controller = SingleListSelectionController[str](
        selected_option=selected_language_observable,
        available_options=language_options_observable,
        formatter=lambda l: f"💻 {l}",
        logger=logger
    )
    language_layout.addWidget(language_controller.widget_list)
    lists_layout2.addWidget(language_group)
    
    main_layout.addLayout(lists_layout2)
    
    # Add buttons to modify available options dynamically
    button_group = QGroupBox("Modify Available Options")
    button_layout = QVBoxLayout(button_group)
    
    button_row1 = QHBoxLayout()
    add_fruit_btn = QPushButton("Add 'Mango' to fruits")
    add_fruit_btn.clicked.connect(lambda: fruit_options_observable.add("Mango"))
    button_row1.addWidget(add_fruit_btn)
    
    remove_fruit_btn = QPushButton("Remove 'Date' from fruits")
    remove_fruit_btn.clicked.connect(lambda: fruit_options_observable.discard("Date"))
    button_row1.addWidget(remove_fruit_btn)
    
    add_number_btn = QPushButton("Add '55' to numbers")
    add_number_btn.clicked.connect(lambda: number_options_observable.add(55))
    button_row1.addWidget(add_number_btn)
    
    button_layout.addLayout(button_row1)
    
    button_row2 = QHBoxLayout()
    add_color_btn = QPushButton("Add 'Pink' to colors")
    add_color_btn.clicked.connect(lambda: color_options_observable.add("Pink"))
    button_row2.addWidget(add_color_btn)
    
    add_language_btn = QPushButton("Add 'Swift' to languages")
    add_language_btn.clicked.connect(lambda: language_options_observable.add("Swift"))
    button_row2.addWidget(add_language_btn)
    
    clear_language_btn = QPushButton("Clear language selection")
    clear_language_btn.clicked.connect(lambda: selected_language_observable.change_value(None))
    button_row2.addWidget(clear_language_btn)
    
    button_layout.addLayout(button_row2)
    main_layout.addWidget(button_group)
    
    # Add status displays showing current values
    logger.info("Creating status display controllers...")
    status_group = QGroupBox("Current Selections")
    status_layout = QHBoxLayout(status_group)
    
    # Create DisplayValueController instances connected to the SingleListSelectionController hooks
    fruit_status = DisplayValueController[str|None](fruit_controller.selected_option_hook, logger=logger)
    number_status = DisplayValueController[int|None](number_controller.selected_option_hook, logger=logger)
    color_status = DisplayValueController[str|None](color_controller.selected_option_hook, logger=logger)
    language_status = DisplayValueController[str|None](language_controller.selected_option_hook, logger=logger)
    
    # Add status widgets to layout
    status_layout.addWidget(QLabel("Fruit:"))
    status_layout.addWidget(fruit_status.widget_label)
    status_layout.addWidget(QLabel("Number:"))
    status_layout.addWidget(number_status.widget_label)
    status_layout.addWidget(QLabel("Color:"))
    status_layout.addWidget(color_status.widget_label)
    status_layout.addWidget(QLabel("Language:"))
    status_layout.addWidget(language_status.widget_label)
    
    main_layout.addWidget(status_group)
    
    # Add some information about what to test
    info_label = QLabel(
        "Test the controller by:\n"
        "1. Clicking on items in the lists to select them\n"
        "2. Clicking on an already-selected item to deselect it (where allowed)\n"
        "3. Note that the Colors list does NOT allow deselection\n"
        "4. Adding/removing options using the buttons above\n"
        "5. Observing how the lists update dynamically\n"
        "6. Notice the custom formatters for each data type"
    )
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_label.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
    main_layout.addWidget(info_label)
    
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

