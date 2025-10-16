"""
Demo showcasing the new IQ (Integrated Quantum) Widget system.

This demonstrates how to use IQ widgets with the default layout strategies
and how to customize layouts using custom strategies.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QLabel
from observables import ObservableSingleValue

# Import the IQ widgets
from integrated_widgets.iq_widgets import (
    IQCheckBox,
    IQFloatEntry,
    IQIntegerEntry,
    IQTextEntry,
    IQDisplayValue,
    IQSelectionOption,
    LayoutStrategy
)
from integrated_widgets.widget_controllers.selection_option_controller import SelectionOptionController


def main():
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQ Widgets Demo")
    window.resize(600, 400)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    
    # === Demo 1: Simple widgets with default layouts ===
    group1 = QGroupBox("Simple Entry Widgets (Default Layouts)")
    group1_layout = QVBoxLayout(group1)
    
    # CheckBox
    checkbox = IQCheckBox(True, text="Enable feature")
    group1_layout.addWidget(checkbox)
    
    # Float entry
    float_entry = IQFloatEntry(3.14159, validator=lambda x: x > 0)
    group1_layout.addWidget(float_entry)
    
    # Integer entry
    integer_entry = IQIntegerEntry(42, validator=lambda x: 0 <= x <= 100)
    group1_layout.addWidget(integer_entry)
    
    # Text entry
    text_entry = IQTextEntry("Hello World", validator=lambda x: len(x) > 0)
    group1_layout.addWidget(text_entry)
    
    main_layout.addWidget(group1)
    
    # === Demo 2: Observable value with display ===
    group2 = QGroupBox("Observable Value with Display")
    group2_layout = QVBoxLayout(group2)
    
    # Create an observable
    temperature_observable = ObservableSingleValue(25.5)
    
    # Display value widget
    temp_display = IQDisplayValue(
        temperature_observable,
        formatter=lambda x: f"{x:.1f} °C"
    )
    group2_layout.addWidget(temp_display)
    
    main_layout.addWidget(group2)
    
    # === Demo 3: Selection widget ===
    group3 = QGroupBox("Selection Widget")
    group3_layout = QVBoxLayout(group3)
    
    colors = {"red", "green", "blue", "yellow"}
    color_selector = IQSelectionOption(
        selected_option="red",
        available_options=colors,
        formatter=lambda x: x.upper()
    )
    group3_layout.addWidget(color_selector)
    
    main_layout.addWidget(group3)
    
    # === Demo 4: Custom Layout Strategy ===
    group4 = QGroupBox("Custom Layout Strategy")
    group4_layout = QVBoxLayout(group4)
    
    # Custom strategy that adds a label
    class LabeledLayoutStrategy(LayoutStrategy[SelectionOptionController]):
        def __call__(self, parent, controller):
            layout = QHBoxLayout(parent)
            layout.addWidget(QLabel("Choose:"))
            layout.addWidget(controller.widget_combobox)
            return layout
    
    animals = {"cat", "dog", "bird", "fish"}
    animal_selector = IQSelectionOption(
        selected_option="cat",
        available_options=animals,
        layout_strategy=LabeledLayoutStrategy()
    )
    group4_layout.addWidget(animal_selector)
    
    main_layout.addWidget(group4)
    
    main_layout.addStretch()
    
    # Show window
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

