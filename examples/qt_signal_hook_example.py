#!/usr/bin/env python3
"""
Example: QtSignalHook integration with observables
=================================================

This example demonstrates how to use QtSignalHook to integrate Qt signals
with the observables system. The hook can be connected to any observable
and will emit Qt signals when the observable's value changes.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import QTimer

# Add the src directory to the path so we can import our modules
sys.path.insert(0, 'src')

from integrated_widgets.util.composition_signal_hook import QtSignalHook
from observables.core import ObservableValue


class ExampleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QtSignalHook Example")
        self.setGeometry(100, 100, 400, 200)
        
        # Create the main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create a label to display the value
        self.value_label = QLabel("Value: 0")
        layout.addWidget(self.value_label)
        
        # Create a button to change the value
        self.change_button = QPushButton("Change Value")
        self.change_button.clicked.connect(self.change_value)
        layout.addWidget(self.change_button)
        
        # Create an observable value
        self.observable = ObservableValue(0)
        
        # Create a Qt signal hook connected to the observable
        self.signal_hook = QtSignalHook(initial_value=0)
        
        # Connect the hook to the observable
        self.observable.connect_hook(self.signal_hook)
        
        # Connect the hook's signal to our update method
        self.signal_hook.value_changed.connect(self.on_value_changed)
        
        # Create a timer to automatically change the value
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_change_value)
        self.timer.start(1000)  # Change every second
        
        self.counter = 0
    
    def change_value(self):
        """Manually change the observable value."""
        new_value = self.observable.value + 1
        self.observable.value = new_value
    
    def auto_change_value(self):
        """Automatically change the value every second."""
        self.counter += 1
        self.observable.value = self.counter
    
    def on_value_changed(self, value):
        """Called when the Qt signal hook emits a value change."""
        self.value_label.setText(f"Value: {value}")
        print(f"Qt signal received: {value}")


def main():
    app = QApplication(sys.argv)
    
    window = ExampleWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
