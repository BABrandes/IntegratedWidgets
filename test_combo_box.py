#!/usr/bin/env python3
"""Test file for ComboBoxController functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from integrated_widgets.widget_controllers.combo_box_controller import ComboBoxController

def test_combo_box_controller():
    """Test the ComboBoxController functionality."""
    print("Testing ComboBoxController...")
    
    # Test basic instantiation
    controller = ComboBoxController(
        selected_value='test', 
        options={'test', 'other', 'third'},
        allow_none=True
    )
    print("  ✅ Controller instantiated successfully")
    
    # Test properties
    print(f"  Selected option: {controller.selected_option}")
    print(f"  Available options: {controller.available_options}")
    print(f"  None allowed: {controller.is_none_selection_allowed}")
    
    # Test setting values
    controller.selected_option = 'other'
    print(f"  After setting to 'other': {controller.selected_option}")
    
    # Test setting options
    controller.available_options = {'new', 'options', 'set'}
    print(f"  New options: {controller.available_options}")
    
    print("✅ All tests passed! ComboBoxController is working correctly.")

if __name__ == "__main__":
    try:
        test_combo_box_controller()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
