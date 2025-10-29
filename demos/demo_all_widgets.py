#!/usr/bin/env python3
"""Comprehensive demo application showcasing all IntegratedWidgets."""

import sys
from typing import Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QPushButton, QHBoxLayout, QTabWidget
)
from nexpy import (
    XValue, 
    XSet,
    XSetSingleSelect,
    XSetSingleSelectOptional
)
from united_system import RealUnitedScalar, Unit, Dimension

from integrated_widgets import (
    IQtDisplayValue,
    IQtCheckBox,
    IQtIntegerEntry,
    IQtFloatEntry,
    IQtTextEntry,
    IQtRangeSlider,
    IQtComboboxSelect,
    IQtRadioButtonsSelect,
    IQtComboboxOptionalSelect,
    IQtListviewSingleOptionalSelect,
    IQtRealUnitedScalar,
    IQtUnitComboBox,
    IQtDoubleListSelection
)
from integrated_widgets.iqt_widgets.iqt_display_value import Controller_Payload

from integrated_widgets import default as integrated_widgets_default
integrated_widgets_default.DEFAULT_DEBOUNCE_MS = 20


def simple_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Simple layout: just the label."""
    return payload.label


def labeled_layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
    """Layout with a prefix label."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    layout.addWidget(QLabel("Current Value:"))
    layout.addWidget(payload.label)
    
    return widget


def create_display_value_tab() -> QWidget:
    """Create the display value demo tab."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    layout.addWidget(QLabel("<h2>DisplayValue Widgets</h2>"))
    layout.addWidget(QLabel("Read-only value display with custom formatters"))
    
    # Counter with simple layout
    layout.addWidget(QLabel("<h3>1. Simple Number Display:</h3>"))
    counter = XValue(0)
    
    counter_display = IQtDisplayValue(
        value=counter,
        formatter=lambda x: f"Count: {x}",
        layout_strategy=simple_layout_strategy # type: ignore
    )
    layout.addWidget(counter_display)
    
    counter_button = QPushButton("Increment Counter")
    counter_button.clicked.connect(lambda: setattr(counter, 'value', counter.value + 1))
    layout.addWidget(counter_button)
    
    # Temperature with labeled layout
    layout.addWidget(QLabel("<h3>2. Temperature Display (RealUnitedScalar):</h3>"))
    temperature = XValue(RealUnitedScalar(20.0, Unit("°C")))
    
    temp_display = IQtDisplayValue(
        value=temperature,
        formatter=lambda x: f"{x.value():.1f} {x.unit}",
        layout_strategy=labeled_layout_strategy # type: ignore
    )
    layout.addWidget(temp_display)
    
    temp_up_button = QPushButton("Increase Temperature (+5°C)")
    temp_up_button.clicked.connect(
        lambda: setattr(temperature, 'value', 
                       RealUnitedScalar(temperature.value.value() + 5, Unit("°C")))
    )
    layout.addWidget(temp_up_button)
    
    # Status message with grid layout
    layout.addWidget(QLabel("<h3>3. Status Message Display:</h3>"))
    status = XValue("Ready")
    
    status_display = IQtDisplayValue(
        value=status,
        formatter=lambda x: f"✓ {x}" if x == "Ready" else f"⚠ {x}"
    )
    layout.addWidget(status_display)
    
    status_buttons_layout = QHBoxLayout()
    ready_button = QPushButton("Set Ready")
    ready_button.clicked.connect(lambda: setattr(status, 'value', "Ready"))
    status_buttons_layout.addWidget(ready_button)
    
    busy_button = QPushButton("Set Busy")
    busy_button.clicked.connect(lambda: setattr(status, 'value', "Busy"))
    status_buttons_layout.addWidget(busy_button)
    
    layout.addLayout(status_buttons_layout)
    
    layout.addStretch()
    return tab


def create_input_widgets_tab() -> QWidget:
    """Create tab with basic input widgets."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    layout.addWidget(QLabel("<h2>Basic Input Widgets</h2>"))
    
    # CheckBox
    layout.addWidget(QLabel("<h3>1. CheckBox:</h3>"))
    enabled = XValue(True)
    checkbox = IQtCheckBox(
        value=enabled,
        text="Enable Feature"
    )
    layout.addWidget(checkbox)
    
    status_label_checkbox = IQtDisplayValue(
        value=enabled,
        formatter=lambda x: f"Status: {'Enabled' if x else 'Disabled'}"
    )
    layout.addWidget(status_label_checkbox)
    
    # Integer Entry
    layout.addWidget(QLabel("<h3>2. Integer Entry:</h3>"))
    count = XValue(42)
    int_entry = IQtIntegerEntry(value=count)
    layout.addWidget(int_entry)
    
    status_label_int = IQtDisplayValue(
        value=count,
        formatter=lambda x: f"Current count: {x}"
    )
    layout.addWidget(status_label_int)
    
    # Float Entry
    layout.addWidget(QLabel("<h3>3. Float Entry:</h3>"))
    pi_value = XValue(3.14159)
    float_entry = IQtFloatEntry(value=pi_value)
    layout.addWidget(float_entry)
    
    status_label_float = IQtDisplayValue(
        value=pi_value,
        formatter=lambda x: f"Value: {x:.5f}"
    )
    layout.addWidget(status_label_float)
    
    # Text Entry
    layout.addWidget(QLabel("<h3>4. Text Entry:</h3>"))
    name = XValue("John Doe")
    text_entry = IQtTextEntry(value_or_hook_or_observable=name)
    layout.addWidget(text_entry)
    
    status_label_text = IQtDisplayValue(
        value=name,
        formatter=lambda x: f"Hello, {x}!"
    )
    layout.addWidget(status_label_text)
    
    layout.addStretch()
    return tab


def create_selection_widgets_tab() -> QWidget:
    """Create tab with selection widgets."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    layout.addWidget(QLabel("<h2>Selection Widgets</h2>"))
    
    # SelectionOption (required selection)
    layout.addWidget(QLabel("<h3>1. Selection Option (Required):</h3>"))
    color_options = frozenset(["Red", "Green", "Blue", "Yellow"])
    color_selection = XSetSingleSelect("Red", color_options)
    
    color_widget = IQtComboboxSelect(
        selected_option=color_selection.selected_option_hook,
        available_options=color_selection.available_options_hook
    )
    layout.addWidget(color_widget)
    
    status_label_color = IQtDisplayValue(
        value=color_selection.selected_option_hook,
        formatter=lambda x: f"Selected color: {x}"
    )
    layout.addWidget(status_label_color)
    
    # SelectionOptionalOption (optional selection)
    layout.addWidget(QLabel("<h3>2. Selection Optional Option (with None):</h3>"))
    country_options = frozenset(["USA", "UK", "Germany", "France", "Japan"])
    country_selection = XSetSingleSelectOptional(None, country_options)
    
    country_widget = IQtComboboxOptionalSelect(
        selected_option=country_selection.selected_option_hook,
        available_options=country_selection.available_options_hook,
        none_option_text="(No country selected)"
    )
    layout.addWidget(country_widget)
    
    status_label_country = IQtDisplayValue(
        value=country_selection.selected_option_hook,
        formatter=lambda x: f"Country: {x if x else 'None'}"
    )
    layout.addWidget(status_label_country)
    
    layout.addStretch()
    return tab


def create_advanced_widgets_tab() -> QWidget:
    """Create tab with advanced widgets."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    layout.addWidget(QLabel("<h2>Advanced Widgets</h2>"))
    
    # RealUnitedScalar
    layout.addWidget(QLabel("<h3>1. Real United Scalar (with unit conversion):</h3>"))
    L = Dimension("L")
    distance = XValue(RealUnitedScalar(100.0, Unit("m")))
    unit_options_dict = {L: set({Unit("m"), Unit("km"), Unit("cm")})}
    
    scalar_widget = IQtRealUnitedScalar(
        value=distance,
        display_unit_options=unit_options_dict
    )
    layout.addWidget(scalar_widget)
    
    status_label_distance = IQtDisplayValue(
        value=distance,
        formatter=lambda x: f"Distance: {x.value():.2f} {x.unit}"
    )
    layout.addWidget(status_label_distance)
    
    # UnitComboBox
    layout.addWidget(QLabel("<h3>2. Unit Combo Box:</h3>"))
    selected_unit = XValue[Unit | None](Unit("m"))
    available_units_dict = {L: set({Unit("m"), Unit("km"), Unit("mm")})}
    
    unit_combo = IQtUnitComboBox(
        selected_unit=selected_unit,
        available_units=available_units_dict
    )
    layout.addWidget(unit_combo)
    
    status_label_unit = IQtDisplayValue(
        value=selected_unit,
        formatter=lambda x: f"Selected unit: {x if x else 'None'}"
    )
    layout.addWidget(status_label_unit)
    
    # Range Slider
    layout.addWidget(QLabel("<h3>3. Range Slider:</h3>"))
    range_slider = IQtRangeSlider[float](
        number_of_ticks=100,
        span_lower_relative_value=0.25,
        span_upper_relative_value=0.75,
        range_lower_value=0.0,
        range_upper_value=100.0
    )
    layout.addWidget(range_slider.controller.widget_range_slider)
    
    status_label_range = IQtDisplayValue(
        value=range_slider.controller.span_lower_value_hook,
        formatter=lambda x: f"Range: {x:.1f} to {range_slider.controller.span_upper_value:.1f}"
    )
    layout.addWidget(status_label_range)
    
    layout.addStretch()
    return tab


def create_radio_buttons_tab() -> QWidget:
    """Create tab with radio button widgets."""
    tab = QWidget()
    layout = QVBoxLayout(tab)

    layout.addWidget(QLabel("<h2>Radio Button Widgets</h2>"))

    # RadioButtons
    layout.addWidget(QLabel("<h3>Radio Buttons:</h3>"))
    size_options = frozenset(["Small", "Medium", "Large"])
    size_selection = XSetSingleSelect("Medium", size_options)

    radio_buttons = IQtRadioButtonsSelect(
        selected_option=size_selection.selected_option_hook,
        available_options=size_selection.available_options_hook
    )
    layout.addWidget(radio_buttons)

    status_label_size = IQtDisplayValue(
        value=size_selection.selected_option_hook,
        formatter=lambda x: f"Selected size: {x}"
    )
    layout.addWidget(status_label_size)

    layout.addStretch()
    return tab


def create_list_widgets_tab() -> QWidget:
    """Create tab with list selection widgets."""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    layout.addWidget(QLabel("<h2>List Selection Widgets</h2>"))
    
    # Single List Selection
    layout.addWidget(QLabel("<h3>1. Single List Selection:</h3>"))
    city_options = frozenset(["New York", "London", "Tokyo", "Paris", "Sydney"])
    city_selection = XSetSingleSelectOptional(None, city_options)
    
    single_list = IQtListviewSingleOptionalSelect(
        selected_option=city_selection.selected_option_hook,
        available_options=city_selection.available_options_hook
    )
    layout.addWidget(single_list)
    
    status_label_city = IQtDisplayValue(
        value=city_selection.selected_option_hook,
        formatter=lambda x: f"Selected city: {x if x else 'None'}"
    )
    layout.addWidget(status_label_city)
    
    # Double List Selection
    layout.addWidget(QLabel("<h3>2. Double List Selection:</h3>"))
    available_fruits = XSet(frozenset(["Apple", "Banana", "Cherry", "Date", "Elderberry"]))
    selected_fruits = XSet(frozenset(["Apple"]))
    
    double_list = IQtDoubleListSelection(
        selected_options=selected_fruits,
        available_options=available_fruits
    )
    layout.addWidget(double_list)
    
    status_label_fruits = IQtDisplayValue(
        value=selected_fruits,
        formatter=lambda x: f"Selected fruits: {', '.join(sorted(x)) if x else 'None'}"
    )
    layout.addWidget(status_label_fruits)
    
    layout.addStretch()
    return tab


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IntegratedWidgets - Complete Demo")
    window.resize(800, 700)
    
    # Central widget with tab widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    
    # Title
    title_label = QLabel("<h1>IntegratedWidgets - Complete Demo</h1>")
    main_layout.addWidget(title_label)
    
    subtitle_label = QLabel(
        "Comprehensive demonstration of all widget controllers with observables 5.0.0"
    )
    main_layout.addWidget(subtitle_label)
    
    # Create tab widget
    tab_widget = QTabWidget()
    main_layout.addWidget(tab_widget)
    
    # Add tabs
    tab_widget.addTab(create_display_value_tab(), "Display Values")
    tab_widget.addTab(create_input_widgets_tab(), "Input Widgets")
    tab_widget.addTab(create_selection_widgets_tab(), "Selection Widgets")
    tab_widget.addTab(create_radio_buttons_tab(), "Radio Buttons")
    tab_widget.addTab(create_advanced_widgets_tab(), "Advanced Widgets")
    tab_widget.addTab(create_list_widgets_tab(), "List Widgets")
    
    # Info footer
    info_layout = QHBoxLayout()
    info_label = QLabel("ℹ All widgets are bidirectionally synchronized with observables")
    info_label.setStyleSheet("color: #666; font-style: italic;")
    info_layout.addWidget(info_label)
    info_layout.addStretch()
    main_layout.addLayout(info_layout)
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

