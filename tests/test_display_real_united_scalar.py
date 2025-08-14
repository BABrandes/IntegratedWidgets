from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Protocol, TypeVar

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QComboBox
from PySide6.QtCore import QTimer

from integrated_widgets import DisplayRealUnitedScalarController
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit

T = TypeVar("T")

class DummyObservable(Generic[T]):
    pass

@dataclass
class DummyUnited:
    magnitude: float
    units: str


@pytest.mark.qt_log_ignore(".*")
def test_unit_value_display_updates(qtbot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(RealUnitedScalar(10, Unit("m")))
    c = DisplayRealUnitedScalarController(osv)
    qtbot.addWidget(c.owner_widget)
    # Initially shows 10 m
    label = c.widget_value_label
    assert label.text().startswith("10.000 m")
    # Switch to km (if present)
    combo = c.widget_unit_combo
    idx_km = combo.findText("km")
    if idx_km != -1:
        combo.setCurrentIndex(idx_km)
        qtbot.waitUntil(lambda: "km" in label.text(), timeout=1000)
        assert label.text().startswith("0.010 km")


def test_manual_demo_can_launch(qtbot):
    app = QApplication.instance() or QApplication([])
    # Minimal launch of the example window for manual play
    import importlib.util, os, sys
    # Import the demo file via path to avoid requiring a package
    demo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples', 'demo_qt_app.py')
    spec = importlib.util.spec_from_file_location('demo_qt_app', demo_path)
    assert spec and spec.loader
    demo = importlib.util.module_from_spec(spec)
    sys.modules['demo_qt_app'] = demo
    spec.loader.exec_module(demo)
    build_demo_window = demo.build_demo_window
    w = build_demo_window()
    qtbot.addWidget(w)
    w.show()
    # Close soon to avoid hanging CI
    QTimer.singleShot(100, w.close)


