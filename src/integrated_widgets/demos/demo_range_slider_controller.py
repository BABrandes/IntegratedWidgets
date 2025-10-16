#!/usr/bin/env python3
"""
Demo application for RangeSliderController.

This demo showcases the RangeSliderController with comprehensive hook monitoring
using DisplayValueController instances. It demonstrates:

1. **Two coordinate systems**:
   - Tick-based (discrete integer positions)
   - Relative (normalized 0.0 to 1.0)

2. **Float-based range slider** (left):
   - Full range: 0.0 to 100.0
   - Shows all primary and computed hooks
   - Interactive buttons to test programmatic updates

3. **RealUnitedScalar-based range slider** (right):
   - Full range: 0.0 to 100.0 km
   - Shows physical values with units
   - Demonstrates value_type and value_unit hooks

4. **Real-time hook monitoring**:
   - All DisplayValueController instances update automatically
   - Demonstrates the observable/hook system working correctly
   - No built-in widgets needed - everything via hooks

5. **Interactive testing**:
   - Drag slider handles to see all values update
   - Use buttons to test programmatic span changes
   - Toggle NaN values to test edge cases
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QGroupBox, QGridLayout
from PySide6.QtCore import Qt

# BAB imports
from united_system import RealUnitedScalar, Unit

# Local imports
from integrated_widgets import RangeSliderController, DisplayValueController
from integrated_widgets.widget_controllers.float_entry_controller import FloatEntryController
from integrated_widgets.widget_controllers.real_united_scalar_controller import RealUnitedScalarController as RUSController
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
    
    # Define unit for scalar-based slider
    distance_unit = Unit("km")
    
    # Create controllers for different range sliders
    logger.info("Creating RangeSliderController instances with comprehensive hook monitoring...")
    
    # Float-based range slider controller
    float_controller = RangeSliderController(
        range_lower_value=0.0,
        range_upper_value=100.0,
        number_of_ticks=100,
        minimum_span_size_relative_value=0.05,
        span_lower_relative_value=0.1,
        span_upper_relative_value=0.8,
        logger=None,
        parent_of_widgets=central_widget
    )
    
    # RealUnitedScalar-based range slider controller
    scalar_controller = RangeSliderController(
        range_lower_value=RealUnitedScalar(0.0, distance_unit),
        range_upper_value=RealUnitedScalar(100.0, distance_unit),
        number_of_ticks=50,
        minimum_span_size_relative_value=0.04,
        span_lower_relative_value=0.1,
        span_upper_relative_value=0.9,
        logger=None,
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
    
    # Create DisplayValueControllers for all float controller hooks
    float_displays = {
        "range_lower": DisplayValueController(float_controller.range_lower_value_hook),
        "range_upper": DisplayValueController(float_controller.range_upper_value_hook),
        "span_lower_rel": DisplayValueController(float_controller.span_lower_relative_value_hook, 
                                                  formatter=lambda x: f"{x:.3f}"),
        "span_upper_rel": DisplayValueController(float_controller.span_upper_relative_value_hook,
                                                  formatter=lambda x: f"{x:.3f}"),
        "span_lower": DisplayValueController(float_controller.span_lower_value_hook,
                                            formatter=lambda x: f"{x:.2f}"),
        "span_upper": DisplayValueController(float_controller.span_upper_value_hook,
                                            formatter=lambda x: f"{x:.2f}"),
        "span_size": DisplayValueController(float_controller.span_size_value_hook,
                                           formatter=lambda x: f"{x:.2f}"),
        "span_center": DisplayValueController(float_controller.span_center_value_hook,
                                             formatter=lambda x: f"{x:.2f}"),
        "num_ticks": DisplayValueController(float_controller.number_of_ticks_hook),
        "min_span_rel": DisplayValueController(float_controller.minimum_span_size_relative_value_hook,
                                               formatter=lambda x: f"{x:.3f}"),
    }
    
    # Add display labels in a grid
    float_info_layout = QGridLayout()
    
    float_info_layout.addWidget(QLabel("Full Range:"), 0, 0)
    float_info_layout.addWidget(float_displays["range_lower"].widget_label, 0, 1)
    float_info_layout.addWidget(QLabel("to"), 0, 2)
    float_info_layout.addWidget(float_displays["range_upper"].widget_label, 0, 3)
    
    float_info_layout.addWidget(QLabel("Span (Relative):"), 1, 0)
    float_info_layout.addWidget(float_displays["span_lower_rel"].widget_label, 1, 1)
    float_info_layout.addWidget(QLabel("to"), 1, 2)
    float_info_layout.addWidget(float_displays["span_upper_rel"].widget_label, 1, 3)
    
    float_info_layout.addWidget(QLabel("Span (Physical):"), 2, 0)
    float_info_layout.addWidget(float_displays["span_lower"].widget_label, 2, 1)
    float_info_layout.addWidget(QLabel("to"), 2, 2)
    float_info_layout.addWidget(float_displays["span_upper"].widget_label, 2, 3)
    
    float_info_layout.addWidget(QLabel("Span Size:"), 3, 0)
    float_info_layout.addWidget(float_displays["span_size"].widget_label, 3, 1)
    float_info_layout.addWidget(QLabel("Center:"), 3, 2)
    float_info_layout.addWidget(float_displays["span_center"].widget_label, 3, 3)
    
    float_info_layout.addWidget(QLabel("Ticks:"), 4, 0)
    float_info_layout.addWidget(float_displays["num_ticks"].widget_label, 4, 1)
    float_info_layout.addWidget(QLabel("Min Span (Rel):"), 4, 2)
    float_info_layout.addWidget(float_displays["min_span_rel"].widget_label, 4, 3)
    
    float_layout.addLayout(float_info_layout)
    
    # Add entry fields for range control (full range, not span)
    float_entry_layout = QGridLayout()
    
    # Create FloatEntryController instances for range lower/upper values
    float_range_lower_entry = FloatEntryController(
        float_controller.range_lower_value_hook # type: ignore
    )
    float_range_upper_entry = FloatEntryController(
        float_controller.range_upper_value_hook # type: ignore
    )
    
    float_entry_layout.addWidget(QLabel("Edit Range Lower:"), 0, 0)
    float_entry_layout.addWidget(float_range_lower_entry.widget_line_edit, 0, 1)
    float_entry_layout.addWidget(QLabel("Edit Range Upper:"), 0, 2)
    float_entry_layout.addWidget(float_range_upper_entry.widget_line_edit, 0, 3)
    
    float_layout.addLayout(float_entry_layout)
    
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
    
    reset_float_btn = QPushButton("Change Full Range")
    reset_float_btn.clicked.connect(reset_float_range)
    
    wide_float_btn = QPushButton("Wide Range")
    wide_float_btn.clicked.connect(set_float_wide_range)
    
    narrow_float_btn = QPushButton("Narrow Range")
    narrow_float_btn.clicked.connect(set_float_narrow_range)
    
    float_button_layout.addWidget(reset_float_btn)
    float_button_layout.addWidget(wide_float_btn)
    float_button_layout.addWidget(narrow_float_btn)
    float_layout.addLayout(float_button_layout)
    
    main_layout.addWidget(float_group)
    
    # Right side - RealUnitedScalar-based range slider
    scalar_group = QGroupBox("RealUnitedScalar Range Slider (0.0 - 100.0 km)")
    scalar_layout = QVBoxLayout(scalar_group)
    
    # Add the range slider widget
    scalar_layout.addWidget(scalar_controller.widget_range_slider)
    
    # Create DisplayValueControllers for all scalar controller hooks
    scalar_displays = {
        "range_lower": DisplayValueController(scalar_controller.range_lower_value_hook),
        "range_upper": DisplayValueController(scalar_controller.range_upper_value_hook),
        "span_lower_rel": DisplayValueController(scalar_controller.span_lower_relative_value_hook,
                                                  formatter=lambda x: f"{x:.3f}"),
        "span_upper_rel": DisplayValueController(scalar_controller.span_upper_relative_value_hook,
                                                  formatter=lambda x: f"{x:.3f}"),
        "span_lower": DisplayValueController(scalar_controller.span_lower_value_hook),
        "span_upper": DisplayValueController(scalar_controller.span_upper_value_hook),
        "span_size": DisplayValueController(scalar_controller.span_size_value_hook),
        "span_center": DisplayValueController(scalar_controller.span_center_value_hook),
        "num_ticks": DisplayValueController(scalar_controller.number_of_ticks_hook),
        "min_span_rel": DisplayValueController(scalar_controller.minimum_span_size_relative_value_hook,
                                               formatter=lambda x: f"{x:.3f}"),
        "value_type": DisplayValueController(scalar_controller.value_type_hook,
                                            formatter=lambda x: x.value),
        "value_unit": DisplayValueController(scalar_controller.value_unit_hook,
                                            formatter=lambda x: str(x) if x else "None"),
    }
    
    # Add display labels in a grid
    scalar_info_layout = QGridLayout()
    
    scalar_info_layout.addWidget(QLabel("Full Range:"), 0, 0)
    scalar_info_layout.addWidget(scalar_displays["range_lower"].widget_label, 0, 1)
    scalar_info_layout.addWidget(QLabel("to"), 0, 2)
    scalar_info_layout.addWidget(scalar_displays["range_upper"].widget_label, 0, 3)
    
    scalar_info_layout.addWidget(QLabel("Span (Relative):"), 1, 0)
    scalar_info_layout.addWidget(scalar_displays["span_lower_rel"].widget_label, 1, 1)
    scalar_info_layout.addWidget(QLabel("to"), 1, 2)
    scalar_info_layout.addWidget(scalar_displays["span_upper_rel"].widget_label, 1, 3)
    
    scalar_info_layout.addWidget(QLabel("Span (Physical):"), 2, 0)
    scalar_info_layout.addWidget(scalar_displays["span_lower"].widget_label, 2, 1)
    scalar_info_layout.addWidget(QLabel("to"), 2, 2)
    scalar_info_layout.addWidget(scalar_displays["span_upper"].widget_label, 2, 3)
    
    scalar_info_layout.addWidget(QLabel("Span Size:"), 3, 0)
    scalar_info_layout.addWidget(scalar_displays["span_size"].widget_label, 3, 1)
    scalar_info_layout.addWidget(QLabel("Center:"), 3, 2)
    scalar_info_layout.addWidget(scalar_displays["span_center"].widget_label, 3, 3)
    
    scalar_info_layout.addWidget(QLabel("Ticks:"), 4, 0)
    scalar_info_layout.addWidget(scalar_displays["num_ticks"].widget_label, 4, 1)
    scalar_info_layout.addWidget(QLabel("Min Span (Rel):"), 4, 2)
    scalar_info_layout.addWidget(scalar_displays["min_span_rel"].widget_label, 4, 3)
    
    scalar_info_layout.addWidget(QLabel("Value Type:"), 5, 0)
    scalar_info_layout.addWidget(scalar_displays["value_type"].widget_label, 5, 1)
    scalar_info_layout.addWidget(QLabel("Unit:"), 5, 2)
    scalar_info_layout.addWidget(scalar_displays["value_unit"].widget_label, 5, 3)
    
    scalar_layout.addLayout(scalar_info_layout)
    
    # Add entry fields for range control (full range, not span)
    scalar_entry_layout = QGridLayout()
    
    # Create unit options for the RealUnitedScalar controllers
    unit_options = {
        distance_unit.dimension: {distance_unit, Unit("m"), Unit("cm"), Unit("mm")}
    }
    
    # Create RealUnitedScalarController instances for range lower/upper values
    scalar_range_lower_entry = RUSController(
        value=scalar_controller.range_lower_value_hook, # type: ignore
        display_unit_options=unit_options
    )
    scalar_range_upper_entry = RUSController(
        value=scalar_controller.range_upper_value_hook, # type: ignore
        display_unit_options=unit_options
    )
    
    scalar_entry_layout.addWidget(QLabel("Edit Range Lower:"), 0, 0)
    scalar_entry_layout.addWidget(scalar_range_lower_entry.widget_value_line_edit, 0, 1)
    scalar_entry_layout.addWidget(scalar_range_lower_entry.widget_display_unit_combobox, 0, 2)
    scalar_entry_layout.addWidget(QLabel("Edit Range Upper:"), 1, 0)
    scalar_entry_layout.addWidget(scalar_range_upper_entry.widget_value_line_edit, 1, 1)
    scalar_entry_layout.addWidget(scalar_range_upper_entry.widget_display_unit_combobox, 1, 2)
    
    scalar_layout.addLayout(scalar_entry_layout)
    
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
    
    reset_scalar_btn = QPushButton("Change Full Range")
    reset_scalar_btn.clicked.connect(reset_scalar_range)
    
    wide_scalar_btn = QPushButton("Wide Range")
    wide_scalar_btn.clicked.connect(set_scalar_wide_range)
    
    narrow_scalar_btn = QPushButton("Narrow Range")
    narrow_scalar_btn.clicked.connect(set_scalar_narrow_range)
    
    scalar_button_layout.addWidget(reset_scalar_btn)
    scalar_button_layout.addWidget(wide_scalar_btn)
    scalar_button_layout.addWidget(narrow_scalar_btn)
    scalar_layout.addLayout(scalar_button_layout)
    
    main_layout.addWidget(scalar_group)
    
    # Add hook monitoring section with explanation
    info_group = QGroupBox("Demo Information")
    info_layout = QVBoxLayout(info_group)
    
    info_text = QLabel(
        "This demo shows the RangeSliderController with DisplayValueController "
        "instances connected to all available hooks. All displays update in real-time "
        "as you drag the slider handles.\n\n"
        "• Relative values: Normalized positions [0.0, 1.0]\n"
        "• Physical values: Actual values mapped to the full range\n"
        "• All hooks update automatically via the observable system"
    )
    info_text.setWordWrap(True)
    info_layout.addWidget(info_text)
    
    layout.addWidget(info_group)
    
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
    logger.info(f"Float controller - Full range: {float_controller.range_lower_value_hook.value} to {float_controller.range_upper_value_hook.value}")
    logger.info(f"Float controller - Selected range: {float_controller.span_lower_value_hook.value} to {float_controller.span_upper_value_hook.value}")
    logger.info(f"Float controller - Number of ticks: {float_controller.number_of_ticks_hook.value}")
    logger.info(f"Scalar controller - Full range: {scalar_controller.range_lower_value_hook.value} to {scalar_controller.range_upper_value_hook.value}")
    logger.info(f"Scalar controller - Selected range: {scalar_controller.span_lower_value_hook.value} to {scalar_controller.span_upper_value_hook.value}")
    logger.info(f"Scalar controller - Number of ticks: {scalar_controller.number_of_ticks_hook.value}")
    logger.info("===================")
    
    # Run the application
    logger.info("Starting Qt event loop...")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
