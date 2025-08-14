from __future__ import annotations

import sys
from typing import Any, List, Sequence, cast

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
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
)
from observables import ObservableSingleValue, ObservableSelectionOption
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike
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
    length = ObservableSingleValue(RealUnitedScalar(10, Unit("m")))
    c_display = DisplayRealUnitedScalarController(length, parent=page_disp)
    _add_row(lay_disp, "value:", [c_display.widget_value_label])
    _add_row(lay_disp, "unit:", [c_display.widget_unit_combo])
    # Status
    status_disp = QLabel()
    lay_disp.addWidget(status_disp)
    def _update_length_label() -> None:
        val = length.value
        try:
            status_disp.setText(f"{val.value():.3f} {val.unit} (canonical={val.canonical_value} {val.dimension.canonical_unit})")
        except Exception:
            status_disp.setText(str(val))
    length.add_listeners(_update_length_label)
    _update_length_label()
    tabs.addTab(page_disp, "Display RealUnited")

    # --- EditRealUnitedScalarController tab ---
    page_edit = QWidget()
    lay_edit = QVBoxLayout(page_edit)
    c_edit = EditRealUnitedScalarController(length, parent=page_edit)
    _add_row(lay_edit, "display:", [c_edit.display_label])
    _add_row(lay_edit, "value:", [c_edit.value_line_edit])
    _add_row(lay_edit, "unit:", [c_edit.unit_line_edit])
    _add_row(lay_edit, "value with unit:", [c_edit.value_with_unit_line_edit])
    status_edit = QLabel()
    lay_edit.addWidget(status_edit)
    def _update_length_label_edit() -> None:
        val = length.value
        try:
            status_edit.setText(f"{val.value():.3f} {val.unit} (canonical={val.canonical_value} {val.dimension.canonical_unit})")
        except Exception:
            status_edit.setText(str(val))
    length.add_listeners(_update_length_label_edit)
    _update_length_label_edit()
    tabs.addTab(page_edit, "Edit RealUnited")

    # --- ComboBoxController tab ---
    page_combo = QWidget()
    lay_combo = QVBoxLayout(page_combo)
    selection = ObservableSelectionOption(selected_option="A", options={"A", "B", "C"}, allow_none=True)
    c_combo = ComboBoxController(selection, parent=page_combo)
    _add_row(lay_combo, "combo:", [c_combo.widget_combobox])
    status_combo = QLabel()
    lay_combo.addWidget(status_combo)
    def _update_sel_label() -> None:
        try:
            status_combo.setText(f"selected={selection.selected_option} options={sorted(selection.options)}")
        except Exception as e:
            status_combo.setText(f"error: {e}")
    selection.add_listeners(_update_sel_label)
    _update_sel_label()
    tabs.addTab(page_combo, "ComboBox")

    # --- RadioButtonsController tab ---
    page_radio = QWidget()
    lay_radio = QVBoxLayout(page_radio)
    c_radio = RadioButtonsController(selection, parent=page_radio)
    # Add all exposed radio buttons
    btns = c_radio.widgets_radio_buttons
    if btns:
        _add_row(lay_radio, "options:", btns)
    status_radio = QLabel()
    lay_radio.addWidget(status_radio)
    def _update_sel_label_radio() -> None:
        try:
            status_radio.setText(f"selected={selection.selected_option} options={sorted(selection.options)}")
        except Exception as e:
            status_radio.setText(f"error: {e}")
    selection.add_listeners(_update_sel_label_radio)
    _update_sel_label_radio()
    tabs.addTab(page_radio, "Radio Buttons")

    # --- IntegerEntryController tab ---
    page_int = QWidget()
    lay_int = QVBoxLayout(page_int)
    c_int = IntegerEntryController(42, parent=page_int)
    _add_row(lay_int, "value:", [c_int.widget_line_edit])
    status_int = QLabel()
    lay_int.addWidget(status_int)
    def _update_int_label() -> None:
        try:
            status_int.setText(f"value={int(c_int.observable.value)}")
        except Exception as e:
            status_int.setText(f"error: {e}")
    c_int.observable.add_listeners(_update_int_label)
    _update_int_label()
    tabs.addTab(page_int, "Integer Entry")

    # --- CheckBoxController tab ---
    page_chk = QWidget()
    lay_chk = QVBoxLayout(page_chk)
    c_chk = CheckBoxController(True, text="Enable feature", parent=page_chk)
    _add_row(lay_chk, "check:", [c_chk.widget_check_box])
    status_chk = QLabel()
    lay_chk.addWidget(status_chk)
    def _update_chk_label() -> None:
        try:
            status_chk.setText(f"checked={bool(c_chk.observable.value)}")
        except Exception as e:
            status_chk.setText(f"error: {e}")
    c_chk.observable.add_listeners(_update_chk_label)
    _update_chk_label()
    tabs.addTab(page_chk, "Check Box")

    # --- PathSelectorController tab ---
    page_path = QWidget()
    lay_path = QVBoxLayout(page_path)
    c_path = PathSelectorController(None, parent=page_path)
    _add_row(lay_path, "path:", [c_path.path_line_edit, c_path.browse_button, c_path.clear_button])
    _add_row(lay_path, "label:", [c_path.path_label])
    status_path = QLabel()
    lay_path.addWidget(status_path)
    def _update_path_label() -> None:
        try:
            p = c_path.observable.value
            status_path.setText("path=None" if p is None else f"path={p}")
        except Exception as e:
            status_path.setText(f"error: {e}")
    c_path.observable.add_listeners(_update_path_label)
    _update_path_label()
    tabs.addTab(page_path, "Path Selector")

    # --- RangeSliderController tab ---
    page_range = QWidget()
    lay_range = QVBoxLayout(page_range)
    # Use floats compatible with controller's default min/max (0.0..1.0)
    range_value: tuple[float, float] = (0.2, 0.5)
    range_obs = ObservableSingleValue(range_value)
    c_range = RangeSliderController(cast(ObservableSingleValueLike[tuple[float, float]], range_obs), minimum=0.0, maximum=1.0, parent=page_range)
    _add_row(lay_range, "range:", [c_range.widget_range_slider])
    status_range = QLabel()
    lay_range.addWidget(status_range)
    def _update_range_label() -> None:
        try:
            lo, hi = c_range.observable.value
            status_range.setText(f"range=({lo:.3f}, {hi:.3f})")
        except Exception as e:
            status_range.setText(f"error: {e}")
    c_range.observable.add_listeners(_update_range_label)
    _update_range_label()
    # Config info
    info_range = QLabel()
    lay_range.addWidget(info_range)
    try:
        min_f = c_range._min_float_value  # type: ignore[attr-defined]
        max_f = c_range._max_float_value  # type: ignore[attr-defined]
    except Exception:
        # Fallback using step_size and number_of_steps
        min_f = 0.0
        max_f = c_range.step_size * c_range.number_of_steps
    info_range.setText(
        f"min={min_f:.3f}, max={max_f:.3f}, steps={c_range.number_of_steps}, step_size={c_range.step_size:.6f}, minimum_range={c_range.minimum_range:.3f}"
    )
    tabs.addTab(page_range, "Range Slider")

    # --- UnitComboBoxController tab ---
    page_ucombo = QWidget()
    lay_ucombo = QVBoxLayout(page_ucombo)
    # Start with canonical unit of volts
    from integrated_widgets.util.observable_protocols import ObservableSelectionOption as _ObsSelOpt  # local import to avoid top clutter
    u_obs = _ObsSelOpt(selected_option=Unit("V"), options={Unit("V"), Unit("mV")}, allow_none=False)
    c_ucombo = UnitComboBoxController(u_obs, parent=page_ucombo)
    _add_row(lay_ucombo, "unit:", [c_ucombo.widget_combobox])
    status_ucombo = QLabel()
    lay_ucombo.addWidget(status_ucombo)
    def _update_ucombo_label() -> None:
        try:
            sel = c_ucombo.observable.selected_option
            opts = sorted([str(u) for u in c_ucombo.observable.options])
            status_ucombo.setText(f"selected={sel} options={opts}")
        except Exception as e:
            status_ucombo.setText(f"error: {e}")
    c_ucombo.observable.add_listeners(_update_ucombo_label)
    _update_ucombo_label()
    tabs.addTab(page_ucombo, "Unit Combo")

    # --- DoubleListSelectionController tab ---
    page_dlist = QWidget()
    lay_dlist = QVBoxLayout(page_dlist)
    from observables import ObservableMultiSelectionOption as _ObsMulti  # local import to use installed API
    d_obs = _ObsMulti(selected_options={"A"}, available_options={"A", "B", "C", "D"})
    c_dlist = DoubleListSelectionController(d_obs, parent=page_dlist)
    _add_row(lay_dlist, "available:", [c_dlist.widget_left_list])
    _add_row(lay_dlist, "move:", [c_dlist.widget_to_right_button, c_dlist.widget_to_left_button])
    _add_row(lay_dlist, "selected:", [c_dlist.widget_right_list])
    status_dlist = QLabel()
    lay_dlist.addWidget(status_dlist)
    def _update_dlist_label() -> None:
        try:
            status_dlist.setText(f"selected={sorted(d_obs.selected_options)} available={sorted(d_obs.available_options)}")
        except Exception as e:
            status_dlist.setText(f"error: {e}")
    d_obs.add_listeners(_update_dlist_label)
    _update_dlist_label()
    tabs.addTab(page_dlist, "Double List")

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


