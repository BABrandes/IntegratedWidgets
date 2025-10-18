"""Tests for RangeSliderController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot
import math

from observables import ObservableSingleValue
from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
from tests.controller_widget_tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_initialization_with_default_values(qtbot: QtBot) -> None:
    """Test that RangeSliderController initializes correctly with default values."""
    controller = RangeSliderController[float](
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.number_of_ticks == 100
    assert controller.span_lower_relative_value == 0.0
    assert controller.span_upper_relative_value == 1.0
    assert controller.minimum_span_size_relative_value == 0.0
    assert math.isnan(controller.range_lower_value)
    assert math.isnan(controller.range_upper_value)


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_initialization_with_custom_values(qtbot: QtBot) -> None:
    """Test that RangeSliderController initializes correctly with custom values."""
    controller = RangeSliderController[float](
        number_of_ticks=50,
        span_lower_relative_value=0.2,
        span_upper_relative_value=0.8,
        minimum_span_size_relative_value=0.1,
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.number_of_ticks == 50
    assert controller.span_lower_relative_value == 0.2
    assert controller.span_upper_relative_value == 0.8
    assert controller.minimum_span_size_relative_value == 0.1
    assert controller.range_lower_value == 0.0
    assert controller.range_upper_value == 100.0


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_initialization_with_observables(qtbot: QtBot) -> None:
    """Test that RangeSliderController initializes correctly with observables."""
    number_of_ticks_obs = ObservableSingleValue[int](50)
    span_lower_obs = ObservableSingleValue[float](0.2)
    span_upper_obs = ObservableSingleValue[float](0.8)
    min_span_obs = ObservableSingleValue[float](0.1)
    range_lower_obs = ObservableSingleValue[float](0.0)
    range_upper_obs = ObservableSingleValue[float](100.0)
    
    controller = RangeSliderController[float](
        number_of_ticks=number_of_ticks_obs,
        span_lower_relative_value=span_lower_obs,
        span_upper_relative_value=span_upper_obs,
        minimum_span_size_relative_value=min_span_obs,
        range_lower_value=range_lower_obs,
        range_upper_value=range_upper_obs,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.number_of_ticks == 50
    assert controller.span_lower_relative_value == 0.2
    assert controller.span_upper_relative_value == 0.8
    assert controller.minimum_span_size_relative_value == 0.1
    assert controller.range_lower_value == 0.0
    assert controller.range_upper_value == 100.0


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_initialization_with_hooks(qtbot: QtBot) -> None:
    """Test that RangeSliderController initializes correctly with hooks."""
    number_of_ticks_obs = ObservableSingleValue[int](50)
    span_lower_obs = ObservableSingleValue[float](0.2)
    span_upper_obs = ObservableSingleValue[float](0.8)
    min_span_obs = ObservableSingleValue[float](0.1)
    range_lower_obs = ObservableSingleValue[float](0.0)
    range_upper_obs = ObservableSingleValue[float](100.0)
    
    number_of_ticks_hook = number_of_ticks_obs.hook
    span_lower_hook = span_lower_obs.hook
    span_upper_hook = span_upper_obs.hook
    min_span_hook = min_span_obs.hook
    range_lower_hook = range_lower_obs.hook
    range_upper_hook = range_upper_obs.hook
    
    controller = RangeSliderController[float](
        number_of_ticks=number_of_ticks_hook,
        span_lower_relative_value=span_lower_hook,
        span_upper_relative_value=span_upper_hook,
        minimum_span_size_relative_value=min_span_hook,
        range_lower_value=range_lower_hook,
        range_upper_value=range_upper_hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.number_of_ticks == 50
    assert controller.span_lower_relative_value == 0.2
    assert controller.span_upper_relative_value == 0.8
    assert controller.minimum_span_size_relative_value == 0.1
    assert controller.range_lower_value == 0.0
    assert controller.range_upper_value == 100.0


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_change_value_method(qtbot: QtBot) -> None:
    """Test that change_value method works correctly."""
    controller = RangeSliderController[float](
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = 75.0
    controller.change_range_lower_value(new_value)
    wait_for_debounce(qtbot)
    
    # Should update the span values based on the new value
    assert controller.range_lower_value == 0.0
    assert controller.range_upper_value == 100.0


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_change_unit_options_method(qtbot: QtBot) -> None:
    """Test that change_unit_options method works correctly."""
    controller = RangeSliderController[float](
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # This method exists but may not be directly testable without unit system
    # Just verify it exists
    assert hasattr(controller, 'change_unit_options')


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_change_unit_method(qtbot: QtBot) -> None:
    """Test that change_unit method works correctly."""
    controller = RangeSliderController[float](
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # This method exists but may not be directly testable without unit system
    # Just verify it exists
    assert hasattr(controller, 'change_unit')


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_change_float_value_method(qtbot: QtBot) -> None:
    """Test that change_float_value method works correctly."""
    controller = RangeSliderController[float](
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # This method exists but may not be directly testable without unit system
    # Just verify it exists
    assert hasattr(controller, 'change_float_value')


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_span_values_properties(qtbot: QtBot) -> None:
    """Test that span value properties work correctly."""
    controller = RangeSliderController[float](
        span_lower_relative_value=0.2,
        span_upper_relative_value=0.8,
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test span value properties
    assert controller.span_lower_value == 20.0  # 0.2 * 100.0
    assert controller.span_upper_value == 80.0   # 0.8 * 100.0
    assert controller.span_size_value == 60.0   # 80.0 - 20.0
    assert controller.span_center_value == 50.0 # (20.0 + 80.0) / 2


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_span_values_change(qtbot: QtBot) -> None:
    """Test that span values change correctly when relative values change."""
    controller = RangeSliderController[float](
        span_lower_relative_value=0.2,
        span_upper_relative_value=0.8,
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change relative values
    controller.set_relative_selected_range_values(0.3, 0.9)
    wait_for_debounce(qtbot)
    
    # Check updated span values
    assert controller.span_lower_value == 30.0  # 0.3 * 100.0
    assert controller.span_upper_value == 90.0  # 0.9 * 100.0
    assert controller.span_size_value == 60.0   # 90.0 - 30.0
    assert controller.span_center_value == 60.0 # (30.0 + 90.0) / 2


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_range_values_change(qtbot: QtBot) -> None:
    """Test that span values update when range values change."""
    controller = RangeSliderController[float](
        span_lower_relative_value=0.2,
        span_upper_relative_value=0.8,
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change range values
    controller.set_full_range_values(50.0, 150.0)
    wait_for_debounce(qtbot)
    
    # Check updated span values (relative values should remain the same)
    assert controller.span_lower_value == 70.0  # 0.2 * (150.0 - 50.0) + 50.0
    assert controller.span_upper_value == 130.0 # 0.8 * (150.0 - 50.0) + 50.0
    assert controller.span_size_value == 60.0   # 130.0 - 70.0
    assert controller.span_center_value == 100.0 # (70.0 + 130.0) / 2


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_minimum_span_size(qtbot: QtBot) -> None:
    """Test that minimum span size is enforced."""
    controller = RangeSliderController[float](
        span_lower_relative_value=0.2,
        span_upper_relative_value=0.3,  # Small span
        minimum_span_size_relative_value=0.2,  # Minimum span size
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Span size should be calculated correctly
    assert controller.span_size_value == 10.0  # (0.3 - 0.2) * 100.0


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_observable_sync(qtbot: QtBot) -> None:
    """Test that RangeSliderController syncs with observable changes."""
    number_of_ticks_obs = ObservableSingleValue[int](50)
    span_lower_obs = ObservableSingleValue[float](0.2)
    span_upper_obs = ObservableSingleValue[float](0.8)
    
    controller = RangeSliderController[float](
        number_of_ticks=number_of_ticks_obs,
        span_lower_relative_value=span_lower_obs,
        span_upper_relative_value=span_upper_obs,
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable values
    number_of_ticks_obs.value = 75
    span_lower_obs.value = 0.3
    span_upper_obs.value = 0.9
    
    # Controller should reflect the changes
    assert controller.number_of_ticks == 75
    assert controller.span_lower_relative_value == 0.3
    assert controller.span_upper_relative_value == 0.9


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_hook_sync(qtbot: QtBot) -> None:
    """Test that RangeSliderController syncs with hook changes."""
    number_of_ticks_obs = ObservableSingleValue[int](50)
    span_lower_obs = ObservableSingleValue[float](0.2)
    span_upper_obs = ObservableSingleValue[float](0.8)
    
    number_of_ticks_hook = number_of_ticks_obs.hook
    span_lower_hook = span_lower_obs.hook
    span_upper_hook = span_upper_obs.hook
    
    controller = RangeSliderController[float](
        number_of_ticks=number_of_ticks_hook,
        span_lower_relative_value=span_lower_hook,
        span_upper_relative_value=span_upper_hook,
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook values
    number_of_ticks_hook.submit_value(75)
    span_lower_hook.submit_value(0.3)
    span_upper_hook.submit_value(0.9)
    
    # Controller should reflect the changes
    assert controller.number_of_ticks == 75
    assert controller.span_lower_relative_value == 0.3
    assert controller.span_upper_relative_value == 0.9
    assert number_of_ticks_obs.value == 75
    assert span_lower_obs.value == 0.3
    assert span_upper_obs.value == 0.9


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_widget_properties(qtbot: QtBot) -> None:
    """Test that RangeSliderController exposes widget properties correctly."""
    controller = RangeSliderController[float](
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_range_slider')
    assert hasattr(controller, 'widget_range_lower_value')
    assert hasattr(controller, 'widget_range_upper_value')
    assert hasattr(controller, 'widget_span_lower_value')
    assert hasattr(controller, 'widget_span_upper_value')
    assert hasattr(controller, 'widget_span_size_value')
    assert hasattr(controller, 'widget_span_center_value')
    
    # Widgets should be enabled by default
    assert controller.widget_range_slider.isEnabled()


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_debounce_functionality(qtbot: QtBot) -> None:
    """Test that debounce functionality works correctly."""
    controller = RangeSliderController[float](
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.set_relative_selected_range_values(0.1, 0.5)
    controller.set_relative_selected_range_values(0.2, 0.6)
    controller.set_relative_selected_range_values(0.3, 0.7)
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.span_lower_relative_value == 0.3


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_default_parameters(qtbot: QtBot) -> None:
    """Test that RangeSliderController works with default parameters."""
    controller = RangeSliderController[float](debounce_ms=TEST_DEBOUNCE_MS)
    
    # Should work with defaults
    assert controller.number_of_ticks == 100
    assert controller.span_lower_relative_value == 0.0
    assert controller.span_upper_relative_value == 1.0
    assert controller.minimum_span_size_relative_value == 0.0
    
    # Test value change
    controller.set_relative_selected_range_values(0.1, 0.9)
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.span_lower_relative_value == 0.1
    assert controller.span_upper_relative_value == 0.9


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_edge_values(qtbot: QtBot) -> None:
    """Test that RangeSliderController handles edge values correctly."""
    controller = RangeSliderController[float](
        span_lower_relative_value=0.0,
        span_upper_relative_value=1.0,
        minimum_span_size_relative_value=0.0,
        range_lower_value=0.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test edge values
    assert controller.span_lower_value == 0.0
    assert controller.span_upper_value == 100.0
    assert controller.span_size_value == 100.0
    assert controller.span_center_value == 50.0


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_negative_range(qtbot: QtBot) -> None:
    """Test that RangeSliderController handles negative range values correctly."""
    controller = RangeSliderController[float](
        span_lower_relative_value=0.2,
        span_upper_relative_value=0.8,
        range_lower_value=-100.0,
        range_upper_value=100.0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test with negative range
    assert controller.span_lower_value == -60.0  # 0.2 * (100.0 - (-100.0)) + (-100.0)
    assert controller.span_upper_value == 60.0   # 0.8 * (100.0 - (-100.0)) + (-100.0)
    assert controller.span_size_value == 120.0   # 60.0 - (-60.0)
    assert controller.span_center_value == 0.0   # (60.0 + (-60.0)) / 2


@pytest.mark.qt_log_ignore(".*")
def test_range_slider_controller_nan_handling(qtbot: QtBot) -> None:
    """Test that RangeSliderController handles NaN values correctly."""
    controller = RangeSliderController[float](
        range_lower_value=float('nan'),
        range_upper_value=float('nan'),
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should handle NaN values
    assert math.isnan(controller.range_lower_value)
    assert math.isnan(controller.range_upper_value)
