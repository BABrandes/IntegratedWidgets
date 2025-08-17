from __future__ import annotations

from PySide6.QtWidgets import QApplication
import pytest

from integrated_widgets.guarded_widgets.guarded_range_slider import GuardedRangeSlider
from pytestqt.qtbot import QtBot

def test_range_slider_min_gap_and_no_crossing(qtbot: QtBot):
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


def test_range_slider_keyboard_nudge_center(qtbot: QtBot):
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


# Tests for RangeSliderController
def test_range_slider_controller_float_construction(qtbot: QtBot):
    """Test RangeSliderController with float values."""
    app = QApplication.instance() or QApplication([])
    from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
    
    # Test with float values
    controller = RangeSliderController(
        selected_range_values=(0.2, 0.8),
        full_range_values=(0.0, 1.0),
        minimum_range_value=0.1,
        number_of_steps=100
    )
    
    assert controller.selected_range_values == (0.2, 0.8)
    assert controller.full_range_values == (0.0, 1.0)
    assert controller.minimum_range_value == 0.1
    assert controller.number_of_steps == 100
    assert controller.range_size == pytest.approx(0.6)
    assert controller.center_of_range == pytest.approx(0.5)
    assert controller.unit is None


def test_range_slider_controller_real_united_scalar_construction(qtbot: QtBot):
    """Test RangeSliderController with RealUnitedScalar values."""
    app = QApplication.instance() or QApplication([])
    from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
    from united_system import RealUnitedScalar, Unit
    
    # Test with RealUnitedScalar values
    unit = Unit("m")
    controller = RangeSliderController(
        selected_range_values=(RealUnitedScalar(0.2, unit), RealUnitedScalar(0.8, unit)),
        full_range_values=(RealUnitedScalar(0.0, unit), RealUnitedScalar(1.0, unit)),
        minimum_range_value=RealUnitedScalar(0.1, unit),
        number_of_steps=100
    )
    
    assert controller.selected_range_values == (RealUnitedScalar(0.2, unit), RealUnitedScalar(0.8, unit))
    assert controller.full_range_values == (RealUnitedScalar(0.0, unit), RealUnitedScalar(1.0, unit))
    assert controller.minimum_range_value == RealUnitedScalar(0.1, unit)
    assert controller.number_of_steps == 100
    assert controller.unit == unit


def test_range_slider_controller_widget_initialization(qtbot: QtBot):
    """Test that RangeSliderController properly initializes widgets."""
    app = QApplication.instance() or QApplication([])
    from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
    
    controller = RangeSliderController(
        selected_range_values=(0.2, 0.8),
        full_range_values=(0.0, 1.0),
        minimum_range_value=0.1,
        number_of_steps=100
    )
    
    # Check that the range slider widget was created
    range_slider = controller.widget_range_slider
    assert range_slider is not None
    
    # Check that the range is set correctly (should be the selected range converted to slider positions)
    lo, hi = range_slider.getRange()
    # selected_range_values (0.2, 0.8) with full_range (0.0, 1.0) and 100 steps
    # should give slider positions: 0.2 * 100 = 20, 0.8 * 100 = 80
    assert lo == 20
    assert hi == 80


def test_range_slider_controller_property_setters(qtbot: QtBot):
    """Test that RangeSliderController property setters work correctly."""
    app = QApplication.instance() or QApplication([])
    from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
    
    controller = RangeSliderController(
        selected_range_values=(0.2, 0.8),
        full_range_values=(0.0, 1.0),
        minimum_range_value=0.1,
        number_of_steps=100
    )
    
    # Test setting selected range values
    controller.selected_range_values = (0.3, 0.7)
    assert controller.selected_range_values == (0.3, 0.7)
    
    # Test setting full range values
    controller.full_range_values = (0.0, 2.0)
    assert controller.full_range_values == (0.0, 2.0)
    
    # Test setting minimum range value
    controller.minimum_range_value = 0.2
    assert controller.minimum_range_value == 0.2
    
    # Test setting number of steps
    controller.number_of_steps = 200
    assert controller.number_of_steps == 200


def test_range_slider_controller_nan_values(qtbot: QtBot):
    """Test RangeSliderController with NaN values."""
    app = QApplication.instance() or QApplication([])
    from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
    import math
    
    # Test with NaN values
    controller = RangeSliderController(
        selected_range_values=(0.2, 0.8),
        full_range_values=(float('nan'), 1.0),  # NaN in full range
        minimum_range_value=0.1,
        number_of_steps=100
    )
    
    # Check that the range slider widget was created
    range_slider = controller.widget_range_slider
    assert range_slider is not None
    
    # Check that handles are hidden when NaN is present
    assert not range_slider._show_handles
    
    # Check that the slider still has the correct number of steps
    lo, hi = range_slider.getRange()
    assert lo == 0
    assert hi == 100
    
    # Check that values are set to NaN
    assert math.isnan(controller.selected_range_values[0])
    assert math.isnan(controller.selected_range_values[1])
    assert math.isnan(controller.full_range_values[0])
    assert math.isnan(controller.full_range_values[1])
    assert math.isnan(controller.minimum_range_value)
    assert math.isnan(controller.range_size)
    assert math.isnan(controller.center_of_range)

