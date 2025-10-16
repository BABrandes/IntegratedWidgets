from __future__ import annotations

import sys
from typing import Sequence
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
)

from integrated_widgets import (
    RadioButtonsController,
    IntegerEntryController,
    CheckBoxController,
    PathSelectorController,
    RangeSliderController,
    UnitComboBoxController,
    DoubleListSelectionController,
    DisplayValueController,
    RealUnitedScalarController,
    SelectionOptionController,
    TextEntryController,
    FloatEntryController,
    SingleListSelectionController,
)
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit, Dimension


def _add_row(layout: QVBoxLayout, label: str, widgets: Sequence[QWidget]) -> None:
    row = QHBoxLayout()
    if label:
        row.addWidget(QLabel(label))
    for w in widgets:
        row.addWidget(w)
    layout.addLayout(row)


def build_demo_window() -> QWidget:
    window = QWidget()
    outer = QVBoxLayout(window)
    outer.setContentsMargins(12, 12, 12, 12)
    outer.setSpacing(12)

    tabs = QTabWidget(window)
    outer.addWidget(tabs)

    # --- RealUnitedScalarController tab ---
    page_real = QWidget()
    lay_real = QVBoxLayout(page_real)
    
    # Create a shared observable value
    shared_value = ObservableSingleValue(RealUnitedScalar(10, Unit("m")))
    c_real = RealUnitedScalarController(
        shared_value,
        display_unit_options={Dimension("L"): {Unit("m"), Unit("km"), Unit("cm")}}
    )
    
    # Add the widgets
    _add_row(lay_real, "display:", [c_real.widget_real_united_scalar_label])
    _add_row(lay_real, "value:", [c_real.widget_value_label])
    _add_row(lay_real, "unit combo:", [c_real.widget_display_unit_combobox])
    _add_row(lay_real, "unit edit:", [c_real.widget_unit_editable_combobox])
    _add_row(lay_real, "edit value:", [c_real.widget_real_united_scalar_line_edit])
    _add_row(lay_real, "value edit:", [c_real.widget_value_line_edit])
    _add_row(lay_real, "unit line:", [c_real.widget_unit_line_edit])
    
    # Display the actual value
    status_real = DisplayValueController(c_real.value_hook, parent_of_widgets=page_real)
    lay_real.addWidget(status_real.widget_label)
    
    tabs.addTab(page_real, "Real United Scalar")

    # --- SelectionOptionController tab ---
    page_combo = QWidget()
    lay_combo = QVBoxLayout(page_combo)
    
    # Create a selection controller
    c_combo = SelectionOptionController(
        selected_option="A", 
        available_options={"A", "B", "C"}, 
        parent_of_widgets=page_combo
    )
    _add_row(lay_combo, "combo:", [c_combo.widget_combobox])
    
    # Display the actual selected option
    status_combo = DisplayValueController(c_combo.selected_option_hook, parent_of_widgets=page_combo)
    lay_combo.addWidget(status_combo.widget_label)
    
    tabs.addTab(page_combo, "Selection Option")

    # --- RadioButtonsController tab ---
    page_radio = QWidget()
    lay_radio = QVBoxLayout(page_radio)
    
    # Create the controller with explicit type handling
    c_radio = RadioButtonsController[str](
        selected_option="A", 
        available_options={"A", "B", "C"}, 
    )
    # Add all exposed radio buttons
    _add_row(lay_radio, "options:", c_radio.widget_radio_buttons)
    
    # Display the actual selected option
    status_radio = DisplayValueController(c_radio.selected_option_hook, parent_of_widgets=page_radio)
    lay_radio.addWidget(status_radio.widget_label)
    
    tabs.addTab(page_radio, "Radio Buttons")

    # --- IntegerEntryController tab ---
    page_int = QWidget()
    lay_int = QVBoxLayout(page_int)
    c_int = IntegerEntryController(42)
    _add_row(lay_int, "value:", [c_int.widget_line_edit])
    
    # Display the actual value
    status_int = DisplayValueController(c_int.value_hook, parent_of_widgets=page_int)
    lay_int.addWidget(status_int.widget_label)
    
    tabs.addTab(page_int, "Integer Entry")

    # --- FloatEntryController tab ---
    page_float = QWidget()
    lay_float = QVBoxLayout(page_float)
    c_float = FloatEntryController(3.14159)
    _add_row(lay_float, "value:", [c_float.widget_line_edit])
    
    # Display the actual value
    status_float = DisplayValueController(c_float.value_hook, parent_of_widgets=page_float)
    lay_float.addWidget(status_float.widget_label)
    
    tabs.addTab(page_float, "Float Entry")

    # --- TextEntryController tab ---
    page_text = QWidget()
    lay_text = QVBoxLayout(page_text)
    c_text = TextEntryController("Hello, World!")
    _add_row(lay_text, "text:", [c_text.widget_line_edit])
    
    # Display the actual value
    status_text = DisplayValueController(c_text.value_hook, parent_of_widgets=page_text)
    lay_text.addWidget(status_text.widget_label)
    
    tabs.addTab(page_text, "Text Entry")

    # --- CheckBoxController tab ---
    page_chk = QWidget()
    lay_chk = QVBoxLayout(page_chk)
    c_chk = CheckBoxController(True)
    _add_row(lay_chk, "check:", [c_chk.widget_check_box])
    
    # Display the actual value
    status_chk = DisplayValueController(c_chk.value_hook, parent_of_widgets=page_chk)
    lay_chk.addWidget(status_chk.widget_label)
    
    tabs.addTab(page_chk, "Check Box")

    # --- PathSelectorController tab ---
    page_path = QWidget()
    lay_path = QVBoxLayout(page_path)
    c_path = PathSelectorController(None)
    _add_row(lay_path, "path:", [c_path.widget_line_edit])
    _add_row(lay_path, "label:", [c_path.widget_label])
    
    # Display the actual path
    status_path = DisplayValueController(c_path.value_hook, parent_of_widgets=page_path)
    lay_path.addWidget(status_path.widget_label)
    
    tabs.addTab(page_path, "Path Selector")

    # --- RangeSliderController tab ---
    page_range = QWidget()
    lay_range = QVBoxLayout(page_range)
    
    # Start with float values
    range_value: tuple[float, float] = (1.2, 1.5)
    c_range = RangeSliderController(
        number_of_ticks=100,
        span_lower_relative_value=0.2,
        span_upper_relative_value=0.8,
        minimum_span_size_relative_value=0.1,
        range_lower_value=RealUnitedScalar(0.0, Unit("m")),
        range_upper_value=RealUnitedScalar(100.0, Unit("m")),
    )
    
    # Add all the widget properties
    _add_row(lay_range, "range slider:", [c_range.widget_range_slider])
    
    # Display the actual selected range
    status_range_lower = DisplayValueController(c_range.span_lower_value_hook, parent_of_widgets=page_range)
    status_range_upper = DisplayValueController(c_range.span_upper_value_hook, parent_of_widgets=page_range)
    status_range_size = DisplayValueController(c_range.span_size_value_hook, parent_of_widgets=page_range)
    status_range_center = DisplayValueController(c_range.span_center_value_hook, parent_of_widgets=page_range)
    status_range_num_ticks = DisplayValueController(c_range.number_of_ticks_hook, parent_of_widgets=page_range)
    status_range_min_span_rel = DisplayValueController(c_range.minimum_span_size_relative_value_hook, parent_of_widgets=page_range)
    status_range_value_type = DisplayValueController(c_range.value_type_hook, parent_of_widgets=page_range)
    status_range_value_unit = DisplayValueController(c_range.value_unit_hook, parent_of_widgets=page_range)
    for status in [status_range_lower, status_range_upper, status_range_size, status_range_center, status_range_num_ticks, status_range_min_span_rel, status_range_value_type, status_range_value_unit]:
        lay_range.addWidget(status.widget_label)
    
    tabs.addTab(page_range, "Range Slider")

    # --- UnitComboBoxController tab ---
    page_ucombo = QWidget()
    lay_ucombo = QVBoxLayout(page_ucombo)
    
    # Start with canonical unit of volts
    voltage_dimension = Unit("V").dimension
    c_ucombo = UnitComboBoxController(
        selected_unit=Unit("V"), 
        available_units={voltage_dimension: {Unit("V"), Unit("mV")}}, 
    )
    _add_row(lay_ucombo, "unit:", [c_ucombo.widget_combobox])
    _add_row(lay_ucombo, "unit edit:", [c_ucombo.widget_editable_combobox])
    
    tabs.addTab(page_ucombo, "Unit Combo Box")

    # --- DoubleListSelectionController tab ---
    page_dlist = QWidget()
    lay_dlist = QVBoxLayout(page_dlist)
    
    c_dlist = DoubleListSelectionController(
        selected_options={"A", "B"}, 
        available_options={"A", "B", "C", "D"}, 
    )
    _add_row(lay_dlist, "available:", [c_dlist.widget_available_list])
    _add_row(lay_dlist, "move:", [c_dlist.widget_button_move_to_selected, c_dlist.widget_button_remove_from_selected])
    _add_row(lay_dlist, "selected:", [c_dlist.widget_selected_list])
    
    # Display the actual selected options
    status_dlist = DisplayValueController(c_dlist.selected_options_hook, parent_of_widgets=page_dlist)
    lay_dlist.addWidget(status_dlist.widget_label)
    
    tabs.addTab(page_dlist, "Double List Selection")

    # --- SingleListSelectionController tab ---
    page_slist = QWidget()
    lay_slist = QVBoxLayout(page_slist)
    
    c_slist = SingleListSelectionController(
        selected_option="A", 
        available_options={"A", "B", "C", "D"}, 
    )
    _add_row(lay_slist, "list:", [c_slist.widget_list])
    
    # Display the actual selected options
    status_slist = DisplayValueController(c_slist.selected_option_hook, parent_of_widgets=page_slist)
    lay_slist.addWidget(status_slist.widget_label)
    
    tabs.addTab(page_slist, "Single List")

    # --- DisplayValueController tab ---
    page_display = QWidget()
    lay_display = QVBoxLayout(page_display)
    
    # Create a display controller for a simple string value
    c_display_value = DisplayValueController("Hello, World!", parent_of_widgets=page_display)
    _add_row(lay_display, "Display Value:", [c_display_value.widget_label])
    
    # Display the actual value using DisplayValueController
    status_display = DisplayValueController(c_display_value.value_hook, parent_of_widgets=page_display)
    lay_display.addWidget(status_display.widget_label)
    
    tabs.addTab(page_display, "Display Value")

    window.setLayout(outer)
    window.setWindowTitle("Integrated Widgets Demo")
    window.resize(800, 600)
    return window


def main(argv: list[str] | None = None) -> int:
    app = QApplication.instance() or QApplication(sys.argv if argv is None else argv)
    w = build_demo_window()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


