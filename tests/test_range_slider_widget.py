from __future__ import annotations

from PySide6.QtWidgets import QApplication

from integrated_widgets.guarded_widgets.guarded_range_slider import GuardedRangeSlider


def test_range_slider_min_gap_and_no_crossing(qtbot):
    app = QApplication.instance() or QApplication([])
    from PySide6.QtWidgets import QWidget
    w = GuardedRangeSlider(QWidget())
    qtbot.addWidget(w)
    w.setRange(0, 100)
    w.setMinimumGap(10)
    w.setValue(20, 30)
    # Drag min beyond max should clamp
    w._active_handle = "min"
    w.setValue(40, 45)
    lo, hi = w.getRange()
    assert hi - lo >= 10


def test_range_slider_keyboard_nudge_center(qtbot):
    app = QApplication.instance() or QApplication([])
    from PySide6.QtWidgets import QWidget
    w = GuardedRangeSlider(QWidget())
    qtbot.addWidget(w)
    w.setRange(0, 100)
    w.setMinimumGap(10)
    w.setValue(20, 40)
    w._active_handle = "center"
    # Simulate nudge by calling private helper
    w._nudge_active(5)
    lo, hi = w.getRange()
    assert lo == 25 and hi == 45

