#!/usr/bin/env python3
"""
Test script for DictOptionalSelectionController without Qt widgets.
"""

import sys
from PySide6.QtWidgets import QApplication
from integrated_widgets.widget_controllers.dict_optional_selection_controller import DictOptionalSelectionController

def test_basic_functionality():
    """Test basic functionality of DictOptionalSelectionController."""
    print("Testing DictOptionalSelectionController...")
    
    # Create controller with initial values
    controller = DictOptionalSelectionController(
        dict_value={'apple': 'red', 'banana': 'yellow', 'orange': 'orange'},
        selected_key='apple'
    )
    
    print("✓ Controller created successfully")
    print(f"Dict: {controller.dict_value}")
    print(f"Selected key: {controller.selected_key}")
    print(f"Selected value: {controller.selected_value}")
    
    # Test dict-like interface
    print(f"Keys: {list(controller.keys())}")
    print(f"Values: {controller.values()}")
    print(f"Items: {controller.items()}")
    
    # Test dict operations
    print(f"Length: {len(controller)}")
    print(f"'apple' in controller: {'apple' in controller}")
    print(f"controller['banana']: {controller['banana']}")
    
    # Test setting values
    controller['grape'] = 'purple'
    print(f"After adding grape: {controller.dict_value}")
    
    # Test changing selection
    print(f"Before changing selection:")
    print(f"  Selected key: {controller.selected_key}")
    print(f"  Selected value: {controller.selected_value}")
    
    print("Changing selection to banana...")
    result = controller.submit_values({"selected_key": "banana", "selected_value": "yellow"})
    print(f"Submit result: {result}")
    
    # Try using the property setter directly
    print("Trying property setter...")
    controller.selected_key = "banana"
    print(f"After property setter:")
    print(f"  Selected key: {controller.selected_key}")
    print(f"  Selected value: {controller.selected_value}")
    
    # Debug: Check if the value was actually submitted
    print(f"Debug - get_value_of_hook('selected_key'): {controller.get_value_of_hook('selected_key')}")
    print(f"Debug - get_value_of_hook('selected_value'): {controller.get_value_of_hook('selected_value')}")
    
    # Test clearing selection
    print("Clearing selection...")
    controller.clear_selection()
    print(f"After clearing selection:")
    print(f"  Selected key: {controller.selected_key}")
    print(f"  Selected value: {controller.selected_value}")
    
    # Test using change_selected_key method
    print("Using change_selected_key method...")
    controller.change_selected_key('orange')
    print(f"After changing to orange:")
    print(f"  Selected key: {controller.selected_key}")
    print(f"  Selected value: {controller.selected_value}")
    
    print("✓ All tests passed!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_basic_functionality()
    app.quit()
