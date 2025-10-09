#!/usr/bin/env python3
"""
Test script to demonstrate blanking behavior with invalid relative values.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

from src.integrated_widgets import RangeSliderController

def main():
    """Main test function."""
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Range Slider Blanking Test")
    window.setGeometry(100, 100, 800, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add title
    title = QLabel("Range Slider Blanking Test")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    layout.addWidget(title)
    
    # Create a range slider controller
    controller = RangeSliderController(
        full_range_lower_value=0.0,
        full_range_upper_value=100.0,
        number_of_ticks=100,
        minimum_number_of_ticks=5,
        selected_range_lower_tick_relative_value=0.2,
        selected_range_upper_tick_relative_value=0.8,
        parent=central_widget
    )
    
    # Add the slider widget
    layout.addWidget(QLabel("Range Slider (should be visible initially):"))
    layout.addWidget(controller.widget_range_slider)
    
    # Add buttons to test different invalid states
    layout.addWidget(QLabel("\nTest Buttons:"))
    
    # Button 1: Set valid values
    btn_valid = QPushButton("Set Valid Values (0.2 - 0.8)")
    def set_valid():
        controller.set_relative_selected_range_values(0.2, 0.8)
        print("✓ Set valid values: 0.2 - 0.8")
    btn_valid.clicked.connect(set_valid)
    layout.addWidget(btn_valid)
    
    # Button 2: Set lower > upper
    btn_inverted = QPushButton("Set Invalid: Lower > Upper (0.8 - 0.2) - Should BLANK")
    def set_inverted():
        try:
            controller.set_relative_selected_range_values(0.8, 0.2)
            print("✗ Set invalid (lower > upper): 0.8 - 0.2 - Widgets should be BLANKED")
        except ValueError as e:
            print(f"✓ Correctly rejected: {e}")
    btn_inverted.clicked.connect(set_inverted)
    layout.addWidget(btn_inverted)
    
    # Button 3: Set out of range (> 1.0)
    btn_too_high = QPushButton("Set Invalid: Value > 1.0 (0.5 - 1.5) - Should BLANK")
    def set_too_high():
        try:
            controller.set_relative_selected_range_values(0.5, 1.5)
            print("✗ Set invalid (> 1.0): 0.5 - 1.5 - Widgets should be BLANKED")
        except ValueError as e:
            print(f"✓ Correctly rejected: {e}")
    btn_too_high.clicked.connect(set_too_high)
    layout.addWidget(btn_too_high)
    
    # Button 4: Set out of range (< 0.0)
    btn_too_low = QPushButton("Set Invalid: Value < 0.0 (-0.2 - 0.5) - Should BLANK")
    def set_too_low():
        try:
            controller.set_relative_selected_range_values(-0.2, 0.5)
            print("✗ Set invalid (< 0.0): -0.2 - 0.5 - Widgets should be BLANKED")
        except ValueError as e:
            print(f"✓ Correctly rejected: {e}")
    btn_too_low.clicked.connect(set_too_low)
    layout.addWidget(btn_too_low)
    
    # Button 5: Set NaN value (requires direct access)
    btn_nan = QPushButton("Set Invalid: NaN Value - Should BLANK")
    def set_nan():
        import math
        # Bypass validation by directly submitting to hooks
        controller.selected_range_lower_tick_relative_value_hook.submit_value(math.nan)
        print("✗ Set NaN value - Widgets should be BLANKED")
    btn_nan.clicked.connect(set_nan)
    layout.addWidget(btn_nan)
    
    # Add info label
    info = QLabel("\nExpected behavior:\n"
                  "- Valid values: Slider is visible and interactive\n"
                  "- Invalid values: Slider and labels are BLANKED (grayed out overlay)\n"
                  "- Verification will reject invalid values, but if they slip through,\n"
                  "  the blanking mechanism provides a visual safety net")
    info.setWordWrap(True)
    info.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
    layout.addWidget(info)
    
    layout.addStretch()
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

