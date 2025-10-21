"""Tests for FloatEntryController class."""

from __future__ import annotations

from typing import Callable
import pytest
from pytestqt.qtbot import QtBot

from nexpy import XValue
from integrated_widgets.controllers.float_entry_controller import FloatEntryController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_initialization_with_direct_value(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController initializes correctly with direct float value."""
    controller = FloatEntryController(
        sample_float,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_float


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_initialization_with_observable(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController initializes correctly with observable."""
    observable = XValue[float](sample_float)
    controller = FloatEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_float
    assert observable.value == sample_float


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_initialization_with_hook(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController initializes correctly with hook."""
    observable = XValue[float](sample_float)
    hook = observable.hook
    controller = FloatEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_float


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_value_change(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController handles value changes correctly."""
    controller = FloatEntryController(
        sample_float,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = 2.71828
    controller.value = new_value
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


def test_float_entry_controller_with_validator(qtbot: QtBot, sample_float: float, float_validator: Callable[[float], bool]) -> None:
    """Test that FloatEntryController works with custom validator."""
    controller = FloatEntryController(
        sample_float,
        validator=float_validator,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid value should work
    valid_value = 1.5
    controller.value = valid_value
    wait_for_debounce(qtbot)
    assert controller.value == valid_value
    
    # Test validator function directly
    assert float_validator(1.5) is True
    assert float_validator(-1.0) is False


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_without_validator(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController works without validator."""
    controller = FloatEntryController(
        sample_float,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Any float value should work
    test_values = [0.0, -1.5, 100.0, -999.99]
    for value in test_values:
        controller.value = value
        wait_for_debounce(qtbot)
        assert controller.value == value


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_observable_sync(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController syncs with observable changes."""
    observable = XValue[float](sample_float)
    controller = FloatEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value
    new_value = 2.71828
    observable.value = new_value
    
    # Controller should reflect the change
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_hook_sync(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController syncs with hook changes."""
    observable = XValue[float](sample_float)
    hook = observable.hook
    controller = FloatEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value using submit_value
    new_value = 2.71828
    hook.submit_value(new_value)
    
    # Controller should reflect the change
    assert controller.value == new_value
    assert observable.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_widget_properties(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController exposes widget properties correctly."""
    controller = FloatEntryController(
        sample_float,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_line_edit')
    
    # Widget should be enabled by default
    assert controller.widget_line_edit.isEnabled() is True


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_debounce_functionality(qtbot: QtBot, sample_float: float) -> None:
    """Test that debounce functionality works correctly."""
    controller = FloatEntryController(
        sample_float,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.value = 1.0
    controller.value = 2.0
    controller.value = 3.0
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.value == 3.0


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_special_float_values(qtbot: QtBot) -> None:
    """Test that FloatEntryController handles special float values correctly."""
    # Test with infinity
    controller_inf = FloatEntryController(
        float('inf'),
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_inf.value == float('inf')
    
    # Test with negative infinity
    controller_neg_inf = FloatEntryController(
        float('-inf'),
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_neg_inf.value == float('-inf')
    
    # Test with NaN
    controller_nan = FloatEntryController(
        float('nan'),
        debounce_ms=TEST_DEBOUNCE_MS
    )
    import math
    assert math.isnan(controller_nan.value)


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_default_parameters(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController works with default parameters."""
    controller = FloatEntryController(sample_float)
    
    # Should work with defaults
    assert controller.value == sample_float
    
    # Test value change
    new_value = 2.71828
    controller.value = new_value
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_submit_method(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController submit method works correctly."""
    controller = FloatEntryController(
        sample_float,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = 2.71828
    controller.submit(new_value)
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_float_entry_controller_submit_with_debounce(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController submit method respects debounce_ms parameter."""
    controller = FloatEntryController(
        sample_float,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = 2.71828
    custom_debounce = 50
    controller.submit(new_value, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.value == new_value


def test_float_entry_controller_validation_error_handling(qtbot: QtBot, sample_float: float) -> None:
    """Test that FloatEntryController handles validation errors gracefully."""
    def strict_validator(x: float) -> bool:
        return x > 0 and x < 10
    
    controller = FloatEntryController(
        sample_float,
        validator=strict_validator,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid value
    controller.value = 5.0
    wait_for_debounce(qtbot)
    assert controller.value == 5.0
    
    # Test validator function directly
    assert strict_validator(5.0) is True
    assert strict_validator(15.0) is False
    assert strict_validator(-5.0) is False
