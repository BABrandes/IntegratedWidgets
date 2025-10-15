#!/usr/bin/env python3
"""
Demo application for UnitComboBoxController.

This demo showcases the UnitComboBoxController with its three main widgets:
1. A regular combo box for selecting from available units
2. An editable combo box that allows typing new units
3. A line edit for direct unit input

The controller manages unit selection, validates user input, and automatically
adds new valid units to the available options.
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from typing import Optional
from united_system import Unit

# BAB imports
from united_system import Unit, Dimension, NamedQuantity
from observables import ObservableSingleValue, ObservableDict
from integrated_widgets.widget_controllers.unit_combo_box_controller import UnitComboBoxController
from integrated_widgets import DisplayValueController

# Local imports
from utils import debug_logger


def main():
    """Main demo function."""
    # Use the debug logger from utils
    logger = debug_logger
    logger.info("Starting UnitComboBoxController demo...")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("UnitComboBoxController Demo")
    window.setGeometry(100, 100, 600, 400)
    
    # Create the central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add a title label
    title_label = QLabel("UnitComboBoxController Demo")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title_label)
    
    # Create initial unit options
    # Start with basic length units
    initial_unit_options = {
        NamedQuantity.LENGTH.dimension: {Unit("m"), Unit("km"), Unit("cm")},
        NamedQuantity.TIME.dimension: {Unit("s"), Unit("min"), Unit("h")},
        NamedQuantity.MASS.dimension: {Unit("kg"), Unit("g")}
    }

    # Create observables for the controller
    selected_unit_observable = ObservableSingleValue[Optional[Unit]](Unit("m"))
    unit_options_observable = ObservableDict(initial_unit_options)
    
    logger.info(f"Initial selected unit: {selected_unit_observable.value}")
    logger.info(f"Initial unit options: {unit_options_observable.value}")
    
    # Create the controller with logger
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=unit_options_observable,
        logger=logger
    )
    
    # Get the demo frame with all widgets
    demo_frame = controller.all_widgets_as_frame()
    layout.addWidget(demo_frame)
    
    # Add some information about what to test
    info_label = QLabel(
        "Test the controller by:\n"
        "1. Selecting different units from the combo boxes\n"
        "2. Typing new units in the editable combo box\n"
        "3. Typing new units in the line edit field\n"
        "4. Adding units of new dimensions (e.g., type 'V' for voltage)"
    )
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_label.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;")
    layout.addWidget(info_label)
    
    # Add status displays showing current values
    logger.info("Creating status display controllers...")
    status_layout = QVBoxLayout()
    
    # Create DisplayValueController instances connected to the UnitComboBoxController hooks
    selected_unit_status = DisplayValueController[Optional[Unit]](controller.selected_unit_hook, logger=logger)
    
    # Add status widgets to layout
    status_layout.addWidget(QLabel("Selected Unit:"))
    status_layout.addWidget(selected_unit_status.widget_label)
    
    layout.addLayout(status_layout)
    
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
