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
from united_system import RealUnitedScalar, Unit, Dimension, NamedQuantity

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
    IQtRealUnitedScalarEntry,
    IQtUnitEntry,
    IQtDoubleListSelection
)
from integrated_widgets.iqt_widgets.iqt_display_value import Controller_Payload
from integrated_widgets.iqt_widgets.iqt_real_united_scalar_entry import Controller_Payload as RealUnitedScalar_Payload

from integrated_widgets import default as integrated_widgets_default
integrated_widgets_default.DEFAULT_DEBOUNCE_MS = 20


def real_united_scalar_layout_strategy(payload: RealUnitedScalar_Payload, **_: Any) -> QWidget:
    """Comprehensive layout for real united scalar with all widgets."""
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)

    # Main value display and editing
    main_layout = QHBoxLayout()
    main_layout.addWidget(QLabel("Full value:"))
    main_layout.addWidget(payload.real_united_scalar_label)
    main_layout.addWidget(payload.real_united_scalar_line_edit)
    main_layout.addWidget(payload.float_value_label)
    main_layout.addWidget(payload.float_value_line_edit)
    main_layout.addWidget(payload.unit_label)
    main_layout.addWidget(payload.unit_line_edit)
    main_layout.addWidget(payload.unit_combobox)
    main_layout.addWidget(payload.unit_editable_combobox)
    layout.addLayout(main_layout)

    # Value-only editing
    value_layout = QHBoxLayout()
    value_layout.addWidget(QLabel("Numeric value:"))
    value_layout.addWidget(payload.float_value_label)
    value_layout.addWidget(payload.float_value_line_edit)
    layout.addLayout(value_layout)

    # Unit editing
    unit_layout = QHBoxLayout()
    unit_layout.addWidget(QLabel("Type units:"))
    unit_layout.addWidget(payload.unit_editable_combobox)
    layout.addLayout(unit_layout)

    return widget


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
    
    # UnitComboBox - allows switching between different dimensions
    layout.addWidget(QLabel("<h3>1. Unit Combo Box (Multi-Dimension):</h3>"))
    selected_unit = XValue(Unit("m"))
    available_units_dict: dict[Dimension, set[Unit]] = {
        Dimension("L"): {Unit("m"), Unit("km"), Unit("cm"), Unit("mm"), Unit("in")},
        NamedQuantity.MASS.dimension: {Unit("kg"), Unit("g"), Unit("mg"), Unit("t"), Unit("lb")},
        NamedQuantity.TIME.dimension: {Unit("s"), Unit("min"), Unit("h")},
        NamedQuantity.TEMPERATURE.dimension: {Unit("°C"), Unit("K"), Unit("°F")}
    }

    unit_combo = IQtUnitEntry(
        selected_unit=selected_unit,
        available_units=available_units_dict,
        allowed_dimensions=None  # Allow all dimensions
    )
    layout.addWidget(unit_combo)

    # Add the editable combo box widget
    layout.addWidget(QLabel("Editable Combo Box:"))
    editable_combo = unit_combo.controller.widget_unit_editable_combobox
    layout.addWidget(editable_combo)

    # Add the line edit widget
    layout.addWidget(QLabel("Line Edit:"))
    line_edit = unit_combo.controller.widget_unit_line_edit
    layout.addWidget(line_edit)

    status_label_unit = IQtDisplayValue(
        value=selected_unit,
        formatter=lambda x: f"Selected unit: {x if x else 'None'}"
    )
    layout.addWidget(status_label_unit)

    # Range slider lower and upper range value

    # Range slider lower value
    lower_range_value = IQtRealUnitedScalarEntry(
        value=RealUnitedScalar(0.0, Unit("m")),
        display_unit_options=available_units_dict,
    )
    upper_range_value = IQtRealUnitedScalarEntry(
        value=RealUnitedScalar(100.0, Unit("m")),
        display_unit_options=available_units_dict,
    )

    lower_range_value.unit_hook.join(unit_combo.selected_unit_hook, initial_sync_mode="use_target_value")
    upper_range_value.unit_hook.join(unit_combo.selected_unit_hook, initial_sync_mode="use_target_value")

    from integrated_widgets.iqt_widgets.iqt_real_united_scalar_entry import Controller_Payload as RealUnitedScalar_Payload

    def float_value_range_layout_strategy(payload: RealUnitedScalar_Payload, **_: Any) -> QWidget:
        """Layout strategy for float value range slider."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(payload.float_value_line_edit)
        return widget

    lower_range_value.set_layout_strategy(float_value_range_layout_strategy)
    upper_range_value.set_layout_strategy(float_value_range_layout_strategy)

    layout.addWidget(lower_range_value)
    layout.addWidget(upper_range_value)

    # Display the range slider values
    lower_range_value_display = IQtDisplayValue(lower_range_value.value_hook)
    layout.addWidget(lower_range_value_display)

    upper_range_value_display = IQtDisplayValue(upper_range_value.value_hook)
    layout.addWidget(upper_range_value_display)

    # Range Slider
    layout.addWidget(QLabel("<h3>3. Range Slider:</h3>"))
    range_slider = IQtRangeSlider[RealUnitedScalar](
        number_of_ticks=100,
        span_lower_relative_value=0.25,
        span_upper_relative_value=0.75,
        range_lower_value=lower_range_value.value_hook,
        range_upper_value=upper_range_value.value_hook
    )

    layout.addWidget(range_slider.controller.widget_range_slider)

    # Add value displays
    range_lower_display = IQtDisplayValue(
        value=range_slider.controller.range_lower_value_hook,
        formatter=lambda x: f"Range min: {x}"
    )
    layout.addWidget(range_lower_display)

    range_upper_display = IQtDisplayValue(
        value=range_slider.controller.range_upper_value_hook,
        formatter=lambda x: f"Range max: {x}"
    )
    layout.addWidget(range_upper_display)

    span_lower_display = IQtDisplayValue(
        value=range_slider.controller.span_lower_value_hook,
        formatter=lambda x: f"Span min: {x}"
    )
    layout.addWidget(span_lower_display)

    span_upper_display = IQtDisplayValue(
        value=range_slider.controller.span_upper_value_hook,
        formatter=lambda x: f"Span max: {x}"
    )
    layout.addWidget(span_upper_display)

    span_relative_lower_display = IQtDisplayValue(
        value=range_slider.controller.span_lower_relative_value_hook,
        formatter=lambda x: f"Relative min: {x:.3f}"
    )
    layout.addWidget(span_relative_lower_display)

    span_relative_upper_display = IQtDisplayValue(
        value=range_slider.controller.span_upper_relative_value_hook,
        formatter=lambda x: f"Relative max: {x:.3f}"
    )
    layout.addWidget(span_relative_upper_display)
    
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

    add_option_button = QPushButton("Add Option")
    add_option_button.clicked.connect(lambda: size_selection.add_available_option("Extra Large"))
    layout.addWidget(add_option_button)

    remove_option_button = QPushButton("Remove Option")
    remove_option_button.clicked.connect(lambda: size_selection.remove_available_option("Extra Large"))
    layout.addWidget(remove_option_button)

    layout.addStretch()
    return tab


def create_real_united_scalar_tab() -> QWidget:
    """Create tab with real united scalar widgets."""
    tab = QWidget()
    layout = QVBoxLayout(tab)

    layout.addWidget(QLabel("<h2>Real United Scalar Widgets</h2>"))

    # Distance measurement
    layout.addWidget(QLabel("<h3>1. Distance Measurement:</h3>"))
    L = Dimension("L")
    distance = XValue(RealUnitedScalar(100.0, Unit("m")))
    unit_options_dict = {L: frozenset({Unit("m"), Unit("km"), Unit("cm"), Unit("mm"), Unit("in")})}

    distance_widget = IQtRealUnitedScalarEntry(
        value=distance,
        display_unit_options=unit_options_dict,
        layout_strategy=real_united_scalar_layout_strategy
    )
    layout.addWidget(distance_widget)

    status_label_distance = IQtDisplayValue(
        value=distance,
        formatter=lambda x: f"Distance: {x.value():.2f} {x.unit}"
    )
    layout.addWidget(status_label_distance)

    allowed_dims_distance = QLabel(f"Allowed dimensions: {', '.join(str(d) for d in distance_widget.controller.allowed_dimensions) if distance_widget.controller.allowed_dimensions else 'All dimensions are allowed'}")
    layout.addWidget(allowed_dims_distance)

    # Temperature measurement
    layout.addWidget(QLabel("<h3>2. Temperature Measurement:</h3>"))
    temperature = XValue(RealUnitedScalar(25.0, Unit("°C")))
    temp_unit_options = {NamedQuantity.TEMPERATURE.dimension: frozenset({Unit("°C"), Unit("K"), Unit("°F")})}

    temp_widget = IQtRealUnitedScalarEntry(
        value=temperature,
        display_unit_options=temp_unit_options,
        layout_strategy=real_united_scalar_layout_strategy
    )
    layout.addWidget(temp_widget)

    status_label_temp = IQtDisplayValue(
        value=temperature,
        formatter=lambda x: f"Temperature: {x.value():.1f} {x.unit}"
    )
    layout.addWidget(status_label_temp)

    allowed_dims_temp = QLabel(f"Allowed dimensions: {', '.join(str(d) for d in temp_widget.controller.allowed_dimensions) if temp_widget.controller.allowed_dimensions else 'All dimensions are allowed'}")
    layout.addWidget(allowed_dims_temp)

    # Mass measurement
    layout.addWidget(QLabel("<h3>3. Mass or Time Measurement:</h3>"))
    mass = XValue(RealUnitedScalar(5.5, Unit("kg")))
    mass_unit_options = {
        NamedQuantity.MASS.dimension: frozenset({Unit("kg"), Unit("g"), Unit("mg"), Unit("t"), Unit("lb")}),
        NamedQuantity.TIME.dimension: frozenset({Unit("s"), Unit("min"), Unit("h")})
    }

    mass_widget = IQtRealUnitedScalarEntry(
        value=mass,
        display_unit_options=mass_unit_options,
        allowed_dimensions={NamedQuantity.MASS.dimension, NamedQuantity.TIME.dimension},
        layout_strategy=real_united_scalar_layout_strategy
    )
    layout.addWidget(mass_widget)

    status_label_mass = IQtDisplayValue(
        value=mass,
        formatter=lambda x: f"Mass: {x.value():.2f} {x.unit}"
    )
    layout.addWidget(status_label_mass)

    allowed_dims_mass = QLabel(f"Allowed dimensions: {', '.join(str(d) for d in mass_widget.controller.allowed_dimensions) if mass_widget.controller.allowed_dimensions else 'All dimensions are allowed'}")
    layout.addWidget(allowed_dims_mass)

    # Buttons to interact with the values
    button_layout = QHBoxLayout()

    double_distance_button = QPushButton("Double Distance")
    double_distance_button.clicked.connect(
        lambda: setattr(distance, 'value',
                       RealUnitedScalar(distance.value.value() * 2, distance.value.unit))
    )
    button_layout.addWidget(double_distance_button)

    convert_temp_button = QPushButton("Convert Temp to °F")
    convert_temp_button.clicked.connect(
        lambda: setattr(temperature, 'value',
                       temperature.value.scalar_in_unit(Unit("°F")))
    )
    button_layout.addWidget(convert_temp_button)

    layout.addLayout(button_layout)

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
        value=selected_fruits.set_hook,
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
    tab_widget.addTab(create_real_united_scalar_tab(), "United Scalar")
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

