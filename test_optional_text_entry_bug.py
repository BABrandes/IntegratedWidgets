#!/usr/bin/env python3
"""
Test script to reproduce the OptionalTextEntryController widget update issue.
"""

import sys
import os
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton
    from PySide6.QtCore import QTimer

    from integrated_widgets.controllers.singleton.optional_text_entry_controller import OptionalTextEntryController
    from integrated_widgets.auxiliaries import default
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the correct environment with PySide6 installed")
    sys.exit(1)


def test_controller_value_setting():
    """Test if setting the controller value updates the widgets properly."""

    # Create controller with initial None value
    controller = OptionalTextEntryController(None, none_value="<none>", debounce_ms=10)

    print("Initial state:")
    print(f"  controller.value: {controller.value}")
    print(f"  controller.widget_optional_text_entry.text(): '{controller.widget_optional_text_entry.text()}'")
    print(f"  controller.widget_optional_text_label.text(): '{controller.widget_optional_text_label.text()}'")
    print()

    # Set value to a string
    print("Setting value to 'new_text'...")
    controller.value = "new_text"

    print("After setting value:")
    print(f"  controller.value: {controller.value}")
    print(f"  controller.widget_optional_text_entry.text(): '{controller.widget_optional_text_entry.text()}'")
    print(f"  controller.widget_optional_text_label.text(): '{controller.widget_optional_text_label.text()}'")
    print()

    # Check if widgets match expected values
    expected_text = controller._formatter("new_text")  # Should be "new_text"
    actual_entry_text = controller.widget_optional_text_entry.text()
    actual_label_text = controller.widget_optional_text_label.text()

    print(f"Expected text: '{expected_text}'")
    print(f"Entry widget text: '{actual_entry_text}'")
    print(f"Label widget text: '{actual_label_text}'")

    if actual_entry_text == expected_text and actual_label_text == expected_text:
        print("✓ Widgets updated correctly")
        return True
    else:
        print("✗ Widgets NOT updated correctly!")
        return False


def test_with_qt_app():
    """Test with a Qt application to ensure proper GUI thread handling."""

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create controller
    controller = OptionalTextEntryController(None, none_value="<none>", debounce_ms=10)

    # Create a simple window to show the widgets
    window = QWidget()
    layout = QVBoxLayout(window)

    layout.addWidget(QLabel("Controller value:"))
    layout.addWidget(controller.widget_optional_text_label)
    layout.addWidget(controller.widget_optional_text_entry)

    # Add test buttons
    set_text_button = QPushButton("Set to 'test_text'")
    set_none_button = QPushButton("Set to None")

    def set_to_text():
        print("Setting value to 'test_text' via button...")
        controller.value = "test_text"
        # Force update check
        print(f"Value after setting: {controller.value}")
        print(f"Entry text: '{controller.widget_optional_text_entry.text()}'")
        print(f"Label text: '{controller.widget_optional_text_label.text()}'")

    def set_to_none():
        print("Setting value to None via button...")
        controller.value = None
        print(f"Value after setting: {controller.value}")
        print(f"Entry text: '{controller.widget_optional_text_entry.text()}'")
        print(f"Label text: '{controller.widget_optional_text_label.text()}'")

    set_text_button.clicked.connect(set_to_text)
    set_none_button.clicked.connect(set_to_none)

    layout.addWidget(set_text_button)
    layout.addWidget(set_none_button)

    window.show()

    # Test programmatically
    print("Testing programmatic value setting...")

    print("Initial state:")
    print(f"  Value: {controller.value}")
    print(f"  Entry: '{controller.widget_optional_text_entry.text()}'")
    print(f"  Label: '{controller.widget_optional_text_label.text()}'")

    # Set to text
    controller.value = "programmatic_text"
    print("After setting to 'programmatic_text':")
    print(f"  Value: {controller.value}")
    print(f"  Entry: '{controller.widget_optional_text_entry.text()}'")
    print(f"  Label: '{controller.widget_optional_text_label.text()}'")

    # Process events to ensure GUI updates
    app.processEvents()

    print("After processEvents():")
    print(f"  Value: {controller.value}")
    print(f"  Entry: '{controller.widget_optional_text_entry.text()}'")
    print(f"  Label: '{controller.widget_optional_text_label.text()}'")

    # Check if the issue exists
    if controller.widget_optional_text_entry.text() != "programmatic_text":
        print("BUG REPRODUCED: Widget text does not match controller value!")
        return False
    else:
        print("Widgets updated correctly")
        return True


def test_invalidate_widgets_directly():
    """Test calling invalidate_widgets directly to see if it works."""

    controller = OptionalTextEntryController(None, none_value="<none>", debounce_ms=10)

    print("Initial state:")
    print(f"  Value: {controller.value}")
    print(f"  Entry: '{controller.widget_optional_text_entry.text()}'")
    print(f"  Label: '{controller.widget_optional_text_label.text()}'")

    # Set value
    controller.value = "direct_invalidate_test"

    print("After setting value (before invalidate_widgets):")
    print(f"  Value: {controller.value}")
    print(f"  Entry: '{controller.widget_optional_text_entry.text()}'")
    print(f"  Label: '{controller.widget_optional_text_label.text()}'")

    # Call invalidate_widgets directly
    controller.invalidate_widgets()

    print("After calling invalidate_widgets():")
    print(f"  Value: {controller.value}")
    print(f"  Entry: '{controller.widget_optional_text_entry.text()}'")
    print(f"  Label: '{controller.widget_optional_text_label.text()}'")

    # Check result
    if controller.widget_optional_text_entry.text() == "direct_invalidate_test":
        print("✓ invalidate_widgets() works correctly")
        return True
    else:
        print("✗ invalidate_widgets() doesn't work!")
        return False


if __name__ == "__main__":
    print("Testing OptionalTextEntryController widget update issue...")

    # Test 1: Basic programmatic test
    print("\n=== Test 1: Basic programmatic test ===")
    success1 = test_controller_value_setting()

    # Test 2: With Qt application
    print("\n=== Test 2: With Qt application ===")
    success2 = test_with_qt_app()

    # Test 3: Direct invalidate_widgets call
    print("\n=== Test 3: Direct invalidate_widgets call ===")
    success3 = test_invalidate_widgets_directly()

    if not success1 or not success2 or not success3:
        print("\n❌ Bug reproduced!")
        sys.exit(1)
    else:
        print("\n✅ No bug found")
        sys.exit(0)
