from __future__ import annotations

import sys
from typing import Sequence, cast

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QPushButton,
)

from integrated_widgets import (
    DisplayRealUnitedScalarController,
    EditRealUnitedScalarController,
    ComboBoxController,
    RadioButtonsController,
    IntegerEntryController,
    CheckBoxController,
    PathSelectorController,
    RangeSliderController,
    UnitComboBoxController,
    DoubleListSelectionController,
    DisplayValueController,
)
from observables import ObservableSingleValueLike, ObservableSelectionOptionLike, InitialSyncMode
from united_system import RealUnitedScalar, Unit


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

    # --- DisplayRealUnitedScalarController tab ---
    page_disp = QWidget()
    lay_disp = QVBoxLayout(page_disp)
    # Create a shared observable value that both controllers will bind to
    shared_value = RealUnitedScalar(10, Unit("m"))
    c_display: DisplayRealUnitedScalarController = DisplayRealUnitedScalarController(shared_value, parent=page_disp)
    _add_row(lay_disp, "value:", [c_display.widget_real_united_scalar_label])
    _add_row(lay_disp, "unit:", [c_display.widget_unit_combo])
    
    # Display the actual value using DisplayValueController
    print(f"DEBUG: Creating DisplayValueController for DisplayRealUnitedScalarController")
    print(f"DEBUG: c_display.distinct_single_value_hook = {c_display.distinct_single_value_hook}")
    print(f"DEBUG: c_display.distinct_single_value_reference = {c_display.distinct_single_value_reference}")
    status_disp = DisplayValueController(c_display.distinct_single_value_hook, parent=page_disp)
    print(f"DEBUG: status_disp created, current value = {status_disp.single_value}")
    lay_disp.addWidget(status_disp.widget_label)
    
    tabs.addTab(page_disp, "Display RealUnited")

    # --- EditRealUnitedScalarController tab ---
    page_edit = QWidget()
    lay_edit = QVBoxLayout(page_edit)
    # Create the edit controller with the same shared value
    c_edit: EditRealUnitedScalarController = EditRealUnitedScalarController(shared_value, parent=page_edit)
    _add_row(lay_edit, "display:", [c_edit.widget_display_label])
    _add_row(lay_edit, "value:", [c_edit.widget_value_line_edit])
    _add_row(lay_edit, "unit:", [c_edit.widget_unit_line_edit])
    _add_row(lay_edit, "value with unit:", [c_edit.widget_value_with_unit_line_edit])
    
    # Display the actual value using DisplayValueController
    status_edit = DisplayValueController(c_edit.distinct_single_value_hook, parent=page_edit)
    lay_edit.addWidget(status_edit.widget_label)
    
    tabs.addTab(page_edit, "Edit RealUnited")

    # --- ComboBoxController tab ---
    page_combo = QWidget()
    lay_combo = QVBoxLayout(page_combo)
    # Create a controller as the observable
    selection = ComboBoxController("A", available_options={"A", "B", "C"}, allow_none=False, parent=page_combo)
    c_combo = ComboBoxController(selection.selected_option, available_options=selection.available_options, parent=page_combo)
    _add_row(lay_combo, "combo:", [c_combo.widget_combobox])
    
    # Display the actual selected option using DisplayValueController
    status_combo = DisplayValueController(c_combo.distinct_single_value_hook, parent=page_combo)
    lay_combo.addWidget(status_combo.widget_label)
    
    tabs.addTab(page_combo, "ComboBox")

    # --- RadioButtonsController tab ---
    page_radio = QWidget()
    lay_radio = QVBoxLayout(page_radio)
    # Create the controller with explicit type handling
    c_radio = RadioButtonsController[str](
        selected_option=selection.selected_option or "A", 
        available_options=selection.available_options, 
        parent=page_radio
    )
    # Add all exposed radio buttons
    btns = c_radio.widgets_radio_buttons
    if btns:
        _add_row(lay_radio, "options:", btns)
    
    # Display the actual selected option using DisplayValueController
    status_radio = DisplayValueController(c_radio.distinct_single_value_hook, parent=page_radio)
    lay_radio.addWidget(status_radio.widget_label)
    
    tabs.addTab(page_radio, "Radio Buttons")

    # --- IntegerEntryController tab ---
    page_int = QWidget()
    lay_int = QVBoxLayout(page_int)
    c_int = IntegerEntryController(42, parent=page_int)
    _add_row(lay_int, "value:", [c_int.widget_line_edit])
    
    # Display the actual value using DisplayValueController
    status_int = DisplayValueController(c_int.distinct_single_value_hook, parent=page_int)
    lay_int.addWidget(status_int.widget_label)
    
    tabs.addTab(page_int, "Integer Entry")

    # --- CheckBoxController tab ---
    page_chk = QWidget()
    lay_chk = QVBoxLayout(page_chk)
    # Create the controller with explicit type handling
    c_chk = CheckBoxController(
        True, 
        text="Enable feature", 
        parent=page_chk
    )
    _add_row(lay_chk, "check:", [c_chk.widget_check_box])
    
    # Display the actual value using DisplayValueController
    print(f"DEBUG: Creating DisplayValueController for CheckBoxController")
    print(f"DEBUG: c_chk.distinct_single_value_hook = {c_chk.distinct_single_value_hook}")
    print(f"DEBUG: c_chk.distinct_single_value_reference = {c_chk.distinct_single_value_reference}")
    status_chk = DisplayValueController(c_chk.distinct_single_value_hook, parent=page_chk)
    print(f"DEBUG: status_chk created, current value = {status_chk.single_value}")
    lay_chk.addWidget(status_chk.widget_label)
    
    tabs.addTab(page_chk, "Check Box")

    # --- PathSelectorController tab ---
    page_path = QWidget()
    lay_path = QVBoxLayout(page_path)
    c_path = PathSelectorController(None, parent=page_path)
    _add_row(lay_path, "path:", [c_path.path_line_edit, c_path.browse_button, c_path.clear_button])
    _add_row(lay_path, "label:", [c_path.path_label])
    
    # Display the actual path using DisplayValueController
    status_path = DisplayValueController(c_path.distinct_single_value_hook, parent=page_path)
    lay_path.addWidget(status_path.widget_label)
    
    tabs.addTab(page_path, "Path Selector")

    # --- RangeSliderController tab ---
    page_range = QWidget()
    lay_range = QVBoxLayout(page_range)
    
    # Start with float values
    range_value: tuple[float, float] = (1.2, 1.5)
    c_range = RangeSliderController[float](
        selected_range_values=range_value, 
        full_range_values=(1.0, 2.0), 
        minimum_range_value=0.1, 
        parent=page_range
    )
    
    # Add all the new widget properties
    print(f"DEBUG: Adding min value label: {c_range.widget_min_value_label}")
    _add_row(lay_range, "min value:", [c_range.widget_min_value_label])
    print(f"DEBUG: Adding max value label: {c_range.widget_max_value_label}")
    _add_row(lay_range, "max value:", [c_range.widget_max_value_label])
    print(f"DEBUG: Adding unit label: {c_range.widget_unit_label}")
    print(f"DEBUG: Unit label text: '{c_range.widget_unit_label.text()}'")
    print(f"DEBUG: Unit label visible: {c_range.widget_unit_label.isVisible()}")
    _add_row(lay_range, "unit:", [c_range.widget_unit_label])
    print(f"DEBUG: Adding range slider: {c_range.widget_range_slider}")
    _add_row(lay_range, "range slider:", [c_range.widget_range_slider])
    print(f"DEBUG: Adding lower value label: {c_range.widget_lower_range_value_label}")
    _add_row(lay_range, "lower value:", [c_range.widget_lower_range_value_label])
    print(f"DEBUG: Adding upper value label: {c_range.widget_upper_range_value_label}")
    _add_row(lay_range, "upper value:", [c_range.widget_upper_range_value_label])
    
    # Display the actual selected range using DisplayValueController
    print(f"DEBUG: Creating DisplayValueController for RangeSliderController")
    print(f"DEBUG: c_range.selected_range_values_hook = {c_range.selected_range_values_hook}")
    print(f"DEBUG: c_range.selected_range_values = {c_range.selected_range_values}")
    status_range = DisplayValueController(c_range.selected_range_values_hook, parent=page_range)
    print(f"DEBUG: status_range created, current value = {status_range.single_value}")
    lay_range.addWidget(status_range.widget_label)
    
    tabs.addTab(page_range, "Range Slider")

    # --- UnitComboBoxController tab ---
    print("DEBUG: Creating UnitComboBoxController tab...")
    page_ucombo = QWidget()
    lay_ucombo = QVBoxLayout(page_ucombo)
    # Start with canonical unit of volts
    print("DEBUG: Creating UnitComboBoxController...")
    c_ucombo = UnitComboBoxController(selected_unit=Unit("V"), available_units={Unit("V"), Unit("mV")}, adding_unit_options_allowed=True, parent=page_ucombo)
    print("DEBUG: UnitComboBoxController created successfully")
    print("DEBUG: Adding UnitComboBoxController widgets to layout...")
    _add_row(lay_ucombo, "unit:", [c_ucombo.widget_combobox])
    
    # Display the actual selected unit using DisplayValueController
    status_ucombo = DisplayValueController(c_ucombo.distinct_single_value_hook, parent=page_ucombo)
    lay_ucombo.addWidget(status_ucombo.widget_label)
    
    print("DEBUG: Adding UnitComboBoxController tab...")
    tabs.addTab(page_ucombo, "Unit Combo")
    print("DEBUG: UnitComboBoxController tab added successfully")

    # --- DoubleListSelectionController tab ---
    page_dlist = QWidget()
    lay_dlist = QVBoxLayout(page_dlist)
    # Use raw sets instead of ObservableMultiSelectionOption
    c_dlist = DoubleListSelectionController(selected_options={"A"}, available_options={"A", "B", "C", "D"}, parent=page_dlist)
    _add_row(lay_dlist, "available:", [c_dlist.widget_left_list])
    _add_row(lay_dlist, "move:", [c_dlist.widget_to_right_button, c_dlist.widget_to_left_button])
    _add_row(lay_dlist, "selected:", [c_dlist.widget_right_list])
    
    # Display the actual selected options using DisplayValueController
    status_dlist = DisplayValueController(c_dlist.distinct_selected_options_hook, parent=page_dlist)
    lay_dlist.addWidget(status_dlist.widget_label)
    
    tabs.addTab(page_dlist, "Double List")

    # --- DisplayValueController tab ---
    page_display = QWidget()
    lay_display = QVBoxLayout(page_display)
    
    # Create a display controller for a simple string value
    c_display_value = DisplayValueController("Hello, World!", parent=page_display)
    _add_row(lay_display, "Display Value:", [c_display_value.widget_label])
    
    # Display the actual value using DisplayValueController
    status_display = DisplayValueController(c_display_value.distinct_single_value_hook, parent=page_display)
    lay_display.addWidget(status_display.widget_label)
    
    tabs.addTab(page_display, "Display Value")

    window.setLayout(outer)
    window.setWindowTitle("Integrated Widgets Demo")
    window.resize(640, 360)
    return window


def main(argv: list[str] | None = None) -> int:
    app = QApplication.instance() or QApplication(sys.argv if argv is None else argv)
    w = build_demo_window()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


