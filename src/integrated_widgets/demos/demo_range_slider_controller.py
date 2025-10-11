#!/usr/bin/env python3
"""
Demo application for RangeSliderController.

This demo showcases the RangeSliderController with multiple range slider widgets
that demonstrate various features including:
1. Basic range slider functionality with float values
2. Range slider with RealUnitedScalar values and units
3. Different initialization patterns (direct value, observable)
4. Observable integration for real-time updates
5. Signal handling and state synchronization
6. Tick-based nomenclature and positioning

The demo includes:
1. Float-based range slider (0.0 to 100.0)
2. RealUnitedScalar-based range slider with distance units
3. Dynamic updates when values change programmatically
4. Real-time logging of all state changes
5. Display of computed values (range size, center, step size)
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QGroupBox, QGridLayout
from PySide6.QtCore import Qt

# BAB imports
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit, Dimension, NamedQuantity

# Local imports
from integrated_widgets import RangeSliderController, DisplayValueController
from .utils import debug_logger


def main():
    """Main demo function."""
    # Use the debug logger from utils
    logger = debug_logger
    logger.info("Starting RangeSliderController demo...")
    
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("RangeSliderController Demo")
    window.setGeometry(100, 100, 1000, 800)
    
    # Create the central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add a title label
    title_label = QLabel("RangeSliderController Demo")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title_label)
    
    # Create observable values for different range sliders
    logger.info("Creating observable values for range sliders...")
    
    # Float-based range slider
    float_lower_observable = ObservableSingleValue(10.0)
    float_upper_observable = ObservableSingleValue(80.0)
    float_number_of_ticks_observable = ObservableSingleValue(100)
    
    # RealUnitedScalar-based range slider
    distance_unit = Unit("km")
    scalar_lower_observable = ObservableSingleValue(RealUnitedScalar(5.0, distance_unit))
    scalar_upper_observable = ObservableSingleValue(RealUnitedScalar(95.0, distance_unit))
    scalar_number_of_ticks_observable = ObservableSingleValue(50)
    
    logger.info(f"Initial float range: {float_lower_observable.value} to {float_upper_observable.value}")
    logger.info(f"Initial scalar range: {scalar_lower_observable.value} to {scalar_upper_observable.value}")
    
    # Create controllers for different range sliders
    logger.info("Creating RangeSliderController instances...")
    
    # Float-based range slider controller
    float_controller = RangeSliderController(
        full_range_lower_value=0.0,
        full_range_upper_value=100.0,
        number_of_ticks=100,
        minimum_number_of_ticks=5,
        selected_range_lower_tick_relative_value=0.1,
        selected_range_upper_tick_relative_value=0.8,
        unit=None,
        logger=logger,
        parent_of_widgets=central_widget
    )
    
    # RealUnitedScalar-based range slider controller
    scalar_controller = RangeSliderController(
        full_range_lower_value=RealUnitedScalar(0.0, distance_unit),
        full_range_upper_value=RealUnitedScalar(100.0, distance_unit),
        number_of_ticks=50,
        minimum_number_of_ticks=2,
        selected_range_lower_tick_relative_value=0.1,
        selected_range_upper_tick_relative_value=0.9,
        unit=distance_unit,
        logger=logger,
        parent_of_widgets=central_widget
    )
    
    # Create layout for the demo
    main_layout = QHBoxLayout()
    layout.addLayout(main_layout)
    
    # Left side - Float-based range slider
    float_group = QGroupBox("Float Range Slider (0.0 - 100.0)")
    float_layout = QVBoxLayout(float_group)
    
    # Add the range slider widget
    float_layout.addWidget(float_controller.widget_range_slider)
    
    # Add display labels for float controller
    float_info_layout = QGridLayout()
    
    float_info_layout.addWidget(QLabel("Full Range:"), 0, 0)
    float_info_layout.addWidget(float_controller.widget_label_full_range_lower_value, 0, 1)
    float_info_layout.addWidget(QLabel("to"), 0, 2)
    float_info_layout.addWidget(float_controller.widget_label_full_range_upper_value, 0, 3)
    
    float_info_layout.addWidget(QLabel("Selected Range:"), 1, 0)
    float_info_layout.addWidget(float_controller.widget_label_selected_range_lower_value, 1, 1)
    float_info_layout.addWidget(QLabel("to"), 1, 2)
    float_info_layout.addWidget(float_controller.widget_label_selected_range_upper_value, 1, 3)
    
    float_info_layout.addWidget(QLabel("Range Size:"), 2, 0)
    float_info_layout.addWidget(float_controller.widget_label_selected_range_size_value, 2, 1)
    
    float_info_layout.addWidget(QLabel("Center:"), 3, 0)
    float_info_layout.addWidget(float_controller.widget_label_center_of_selected_range_value, 3, 1)
    
    float_layout.addLayout(float_info_layout)
    
    # Add manual input fields for float controller
    float_input_layout = QHBoxLayout()
    float_input_layout.addWidget(QLabel("Lower:"))
    float_input_layout.addWidget(float_controller.widget_text_edit_selected_range_lower_value)
    float_input_layout.addWidget(QLabel("Upper:"))
    float_input_layout.addWidget(float_controller.widget_text_edit_selected_range_upper_value)
    float_layout.addLayout(float_input_layout)
    
    # Add control buttons for float controller
    float_button_layout = QHBoxLayout()
    
    def reset_float_range():
        """Reset float range to default values."""
        float_controller.set_full_range_values(5.0, 95.0)
        logger.info("Reset float range to 5.0 - 95.0")
    
    def set_float_wide_range():
        """Set float range to a wide selection."""
        float_controller.set_relative_selected_range_values(0.1, 0.9)
        logger.info("Set float range to wide selection (10% - 90%)")
    
    def set_float_narrow_range():
        """Set float range to a narrow selection."""
        float_controller.set_relative_selected_range_values(0.4, 0.6)
        logger.info("Set float range to narrow selection (40% - 60%)")
    
    # Toggle counter for float controller (even = normal, odd = NaN)
    float_toggle_counter = [0]  # Use list to make it mutable in closure
    
    def toggle_float_nan():
        """Toggle float range between NaN and normal values."""
        float_toggle_counter[0] += 1
        if float_toggle_counter[0] % 2 == 0:  # Even = normal values
            float_controller.set_full_range_values(10.0, 80.0)
            logger.info("Set float range to normal values (10.0 - 80.0)")
        else:  # Odd = NaN values
            float_controller.set_full_range_values(float('nan'), float('nan'))
            logger.info("Set float range to NaN values")
    
    reset_float_btn = QPushButton("Change Full Range")
    reset_float_btn.clicked.connect(reset_float_range)
    
    wide_float_btn = QPushButton("Wide Range")
    wide_float_btn.clicked.connect(set_float_wide_range)
    
    narrow_float_btn = QPushButton("Narrow Range")
    narrow_float_btn.clicked.connect(set_float_narrow_range)
    
    toggle_nan_float_btn = QPushButton("Toggle NaN")
    toggle_nan_float_btn.clicked.connect(toggle_float_nan)
    
    float_button_layout.addWidget(reset_float_btn)
    float_button_layout.addWidget(wide_float_btn)
    float_button_layout.addWidget(narrow_float_btn)
    float_button_layout.addWidget(toggle_nan_float_btn)
    float_layout.addLayout(float_button_layout)
    
    main_layout.addWidget(float_group)
    
    # Right side - RealUnitedScalar-based range slider
    scalar_group = QGroupBox("RealUnitedScalar Range Slider (0.0 - 100.0 km)")
    scalar_layout = QVBoxLayout(scalar_group)
    
    # Add the range slider widget
    scalar_layout.addWidget(scalar_controller.widget_range_slider)
    
    # Add display labels for scalar controller
    scalar_info_layout = QGridLayout()
    
    scalar_info_layout.addWidget(QLabel("Full Range:"), 0, 0)
    scalar_info_layout.addWidget(scalar_controller.widget_label_full_range_lower_value, 0, 1)
    scalar_info_layout.addWidget(QLabel("to"), 0, 2)
    scalar_info_layout.addWidget(scalar_controller.widget_label_full_range_upper_value, 0, 3)
    
    scalar_info_layout.addWidget(QLabel("Selected Range:"), 1, 0)
    scalar_info_layout.addWidget(scalar_controller.widget_label_selected_range_lower_value, 1, 1)
    scalar_info_layout.addWidget(QLabel("to"), 1, 2)
    scalar_info_layout.addWidget(scalar_controller.widget_label_selected_range_upper_value, 1, 3)
    
    scalar_info_layout.addWidget(QLabel("Range Size:"), 2, 0)
    scalar_info_layout.addWidget(scalar_controller.widget_label_selected_range_size_value, 2, 1)
    
    scalar_info_layout.addWidget(QLabel("Center:"), 3, 0)
    scalar_info_layout.addWidget(scalar_controller.widget_label_center_of_selected_range_value, 3, 1)
    
    scalar_info_layout.addWidget(QLabel("Unit:"), 4, 0)
    scalar_info_layout.addWidget(scalar_controller.widget_label_unit, 4, 1)
    
    scalar_layout.addLayout(scalar_info_layout)
    
    # Add manual input fields for scalar controller
    scalar_input_layout = QHBoxLayout()
    scalar_input_layout.addWidget(QLabel("Lower:"))
    scalar_input_layout.addWidget(scalar_controller.widget_text_edit_selected_range_lower_value)
    scalar_input_layout.addWidget(QLabel("Upper:"))
    scalar_input_layout.addWidget(scalar_controller.widget_text_edit_selected_range_upper_value)
    scalar_layout.addLayout(scalar_input_layout)
    
    # Add control buttons for scalar controller
    scalar_button_layout = QHBoxLayout()
    
    def reset_scalar_range():
        """Reset scalar range to default values."""
        scalar_controller.set_full_range_values(
            RealUnitedScalar(2.0, distance_unit),
            RealUnitedScalar(98.0, distance_unit)
        )
        logger.info("Reset scalar range to 2.0 - 98.0 km")
    
    def set_scalar_wide_range():
        """Set scalar range to a wide selection."""
        scalar_controller.set_relative_selected_range_values(0.1, 0.9)
        logger.info("Set scalar range to wide selection (10% - 90%)")
    
    def set_scalar_narrow_range():
        """Set scalar range to a narrow selection."""
        scalar_controller.set_relative_selected_range_values(0.4, 0.6)
        logger.info("Set scalar range to narrow selection (40% - 60%)")
    
    # Toggle counter for scalar controller (even = normal, odd = NaN)
    scalar_toggle_counter = [0]  # Use list to make it mutable in closure
    
    def toggle_scalar_nan():
        """Toggle scalar range between NaN and normal values."""
        scalar_toggle_counter[0] += 1
        if scalar_toggle_counter[0] % 2 == 0:  # Even = normal values
            scalar_controller.set_full_range_values(
                RealUnitedScalar(5.0, distance_unit),
                RealUnitedScalar(95.0, distance_unit)
            )
            logger.info("Set scalar range to normal values (5.0 - 95.0 km)")
        else:  # Odd = NaN values
            scalar_controller.set_full_range_values(
                RealUnitedScalar(float('nan'), distance_unit),
                RealUnitedScalar(float('nan'), distance_unit)
            )
            logger.info("Set scalar range to NaN values")
    
    reset_scalar_btn = QPushButton("Change Full Range")
    reset_scalar_btn.clicked.connect(reset_scalar_range)
    
    wide_scalar_btn = QPushButton("Wide Range")
    wide_scalar_btn.clicked.connect(set_scalar_wide_range)
    
    narrow_scalar_btn = QPushButton("Narrow Range")
    narrow_scalar_btn.clicked.connect(set_scalar_narrow_range)
    
    toggle_nan_scalar_btn = QPushButton("Toggle NaN")
    toggle_nan_scalar_btn.clicked.connect(toggle_scalar_nan)
    
    scalar_button_layout.addWidget(reset_scalar_btn)
    scalar_button_layout.addWidget(wide_scalar_btn)
    scalar_button_layout.addWidget(narrow_scalar_btn)
    scalar_button_layout.addWidget(toggle_nan_scalar_btn)
    scalar_layout.addLayout(scalar_button_layout)
    
    main_layout.addWidget(scalar_group)
    
    # Add hook monitoring section
    hook_group = QGroupBox("Hook Monitoring")
    hook_layout = QVBoxLayout(hook_group)
    
    # Create labels to display hook values
    float_hook_label = QLabel("Float Hook Values: (will update in real-time)")
    float_hook_label.setWordWrap(True)
    scalar_hook_label = QLabel("Scalar Hook Values: (will update in real-time)")
    scalar_hook_label.setWordWrap(True)
    
    hook_layout.addWidget(float_hook_label)
    hook_layout.addWidget(scalar_hook_label)
    
    layout.addWidget(hook_group)
    
    # Function to update hook display
    def update_hook_display():
        """Update the hook value display."""
        # For now, just show a simple message
        float_hook_label.setText("Float Hooks: (Hook display temporarily disabled)")
        scalar_hook_label.setText("Scalar Hooks: (Hook display temporarily disabled)")
    
    # Hook listeners removed to prevent excessive debug logging
    # The update_hook_display function only shows static text anyway
    
    # Initial hook display update
    update_hook_display()
    
    # Add status displays showing current values
    logger.info("Creating status display controllers...")
    status_layout = QHBoxLayout()
    
    # Create DisplayValueController instances connected to the RangeSliderController hooks
    float_lower_status = DisplayValueController[float](float_controller.selected_range_lower_tick_value_hook, logger=logger)
    float_upper_status = DisplayValueController[float](float_controller.selected_range_upper_tick_value_hook, logger=logger)
    scalar_lower_status = DisplayValueController[RealUnitedScalar](scalar_controller.selected_range_lower_tick_value_hook, logger=logger)
    scalar_upper_status = DisplayValueController[RealUnitedScalar](scalar_controller.selected_range_upper_tick_value_hook, logger=logger)
    
    # Add status widgets to layout
    status_layout.addWidget(QLabel("Float Lower:"))
    status_layout.addWidget(float_lower_status.widget_label)
    status_layout.addWidget(QLabel("Float Upper:"))
    status_layout.addWidget(float_upper_status.widget_label)
    status_layout.addWidget(QLabel("Scalar Lower:"))
    status_layout.addWidget(scalar_lower_status.widget_label)
    status_layout.addWidget(QLabel("Scalar Upper:"))
    status_layout.addWidget(scalar_upper_status.widget_label)
    
    layout.addLayout(status_layout)
    
    # Add a close button
    close_button = QPushButton("Close Demo")
    close_button.clicked.connect(window.close)
    close_button.setStyleSheet("font-size: 14px; padding: 10px;")
    layout.addWidget(close_button)
    
    # Show the window
    window.show()
    logger.info("RangeSliderController demo window shown")
    
    # Log initial state
    logger.info("=== Initial State ===")
    logger.info(f"Float controller - Full range: {float_controller.full_range_lower_value_hook} to {float_controller.full_range_upper_value_hook}")
    logger.info(f"Float controller - Selected range: {float_controller.selected_range_lower_tick_value_hook} to {float_controller.selected_range_upper_tick_value_hook}")
    logger.info(f"Float controller - Number of ticks: {float_controller.number_of_ticks_hook}")
    logger.info(f"Scalar controller - Full range: {scalar_controller.full_range_lower_value_hook} to {scalar_controller.full_range_upper_value_hook}")
    logger.info(f"Scalar controller - Selected range: {scalar_controller.selected_range_lower_tick_value_hook} to {scalar_controller.selected_range_upper_tick_value_hook}")
    logger.info(f"Scalar controller - Number of ticks: {scalar_controller.number_of_ticks_hook}")
    logger.info("===================")
    
    # Run the application
    logger.info("Starting Qt event loop...")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
