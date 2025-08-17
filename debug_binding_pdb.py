#!/usr/bin/env python3

import sys
import pdb
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer

from integrated_widgets import DisplayValueController, CheckBoxController

def test_binding():
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    
    # Create a CheckBoxController
    print("🔍 Creating CheckBoxController...")
    c_chk = CheckBoxController(value_or_observable_or_hook=True, text="Test Checkbox", parent=window)
    layout.addWidget(c_chk.widget_check_box)
    
    # Create a DisplayValueController bound to it
    print("🔍 Creating DisplayValueController...")
    status_chk = DisplayValueController(c_chk.distinct_single_value_hook, parent=window)
    layout.addWidget(status_chk.widget_label)
    
    # Add a button to change the value
    change_btn = QPushButton("Change Value", window)
    layout.addWidget(change_btn)
    
    # Add a label to show current values
    info_label = QLabel("Initial state", window)
    layout.addWidget(info_label)
    
    def update_info():
        checkbox_value = c_chk.single_value
        display_value = status_chk.single_value
        info_label.setText(f"CheckBox: {checkbox_value}, Display: {display_value}")
    
    def change_value():
        print("\n" + "="*50)
        print("🔄 VALUE CHANGE TRIGGERED")
        print("="*50)
        
        new_value = not c_chk.single_value
        print(f"DEBUG: Changing CheckBox value from {c_chk.single_value} to {new_value}")
        print(f"DEBUG: Before change - CheckBox hook value: {c_chk.distinct_single_value_hook.value}")
        print(f"DEBUG: Before change - Display hook value: {status_chk.distinct_single_value_hook.value}")
        
        # Set a breakpoint here to step through the value change
        pdb.set_trace()
        
        c_chk.single_value = new_value
        
        print(f"DEBUG: After change - CheckBox: {c_chk.single_value}, Display: {status_chk.single_value}")
        print(f"DEBUG: After change - CheckBox hook value: {c_chk.distinct_single_value_hook.value}")
        print(f"DEBUG: After change - Display hook value: {status_chk.distinct_single_value_hook.value}")
        update_info()
    
    change_btn.clicked.connect(change_value)
    
    # Update info initially
    update_info()
    
    # Set up a timer to periodically check values
    timer = QTimer()
    timer.timeout.connect(update_info)
    timer.start(1000)  # Check every second
    
    window.setWindowTitle("Binding Debug Test (with PDB)")
    window.resize(400, 200)
    window.show()
    
    print("🚀 App started! Click 'Change Value' button to trigger debug breakpoint.")
    print("💡 Use 'n' to step over, 's' to step into, 'c' to continue")
    print("💡 Use 'justMyCode' to only step through your code")
    
    return app.exec()

if __name__ == "__main__":
    # Configure debugger to only step through user code
    import os
    os.environ['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
    
    sys.exit(test_binding())
