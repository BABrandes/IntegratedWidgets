"""Tests for IntegerEntryController class."""

from __future__ import annotations

from typing import Callable
import pytest
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue
from integrated_widgets.controllers.integer_entry_controller import IntegerEntryController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_initialization_with_direct_value(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController initializes correctly with direct integer value."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_int


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_initialization_with_observable(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController initializes correctly with observable."""
    observable = ObservableSingleValue[int](sample_int)
    controller = IntegerEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_int
    assert observable.value == sample_int


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_initialization_with_hook(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController initializes correctly with hook."""
    observable = ObservableSingleValue[int](sample_int)
    hook = observable.hook
    controller = IntegerEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_int


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_value_change(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController handles value changes correctly."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = 100
    controller.value = new_value
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


def test_integer_entry_controller_with_validator(qtbot: QtBot, sample_int: int, int_validator: Callable[[int], bool]) -> None:
    """Test that IntegerEntryController works with custom validator."""
    controller = IntegerEntryController(
        sample_int,
        validator=int_validator,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid value should work
    valid_value = 50
    controller.value = valid_value
    wait_for_debounce(qtbot)
    assert controller.value == valid_value
    
    # Test validator function directly
    assert int_validator(50) is True
    assert int_validator(-10) is False


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_without_validator(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController works without validator."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Any integer value should work
    test_values = [0, -1, 100, -999, 999999]
    for value in test_values:
        controller.value = value
        wait_for_debounce(qtbot)
        assert controller.value == value


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_observable_sync(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController syncs with observable changes."""
    observable = ObservableSingleValue[int](sample_int)
    controller = IntegerEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value
    new_value = 200
    observable.value = new_value
    
    # Controller should reflect the change
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_hook_sync(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController syncs with hook changes."""
    observable = ObservableSingleValue[int](sample_int)
    hook = observable.hook
    controller = IntegerEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value using submit_value
    new_value = 200
    hook.submit_value(new_value)
    
    # Controller should reflect the change
    assert controller.value == new_value
    assert observable.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_widget_properties(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController exposes widget properties correctly."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_line_edit')
    
    # Widget should be enabled by default
    assert controller.widget_line_edit.isEnabled() is True


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_debounce_functionality(qtbot: QtBot, sample_int: int) -> None:
    """Test that debounce functionality works correctly."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.value = 10
    controller.value = 20
    controller.value = 30
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.value == 30


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_edge_values(qtbot: QtBot) -> None:
    """Test that IntegerEntryController handles edge integer values correctly."""
    # Test with zero
    controller_zero = IntegerEntryController(
        0,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_zero.value == 0
    
    # Test with large positive number
    controller_large = IntegerEntryController(
        999999999,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_large.value == 999999999
    
    # Test with large negative number
    controller_negative = IntegerEntryController(
        -999999999,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_negative.value == -999999999


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_default_parameters(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController works with default parameters."""
    controller = IntegerEntryController(sample_int)
    
    # Should work with defaults
    assert controller.value == sample_int
    
    # Test value change
    new_value = 200
    controller.value = new_value
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_submit_method(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController submit method works correctly."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = 200
    controller.submit(new_value)
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_submit_with_debounce(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController submit method respects debounce_ms parameter."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = 200
    custom_debounce = 50
    controller.submit(new_value, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.value == new_value


def test_integer_entry_controller_validation_error_handling(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController handles validation errors gracefully."""
    def strict_validator(x: int) -> bool:
        return x > 0 and x < 100
    
    controller = IntegerEntryController(
        sample_int,
        validator=strict_validator,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid value
    controller.value = 50
    wait_for_debounce(qtbot)
    assert controller.value == 50
    
    # Test validator function directly
    assert strict_validator(50) is True
    assert strict_validator(150) is False
    assert strict_validator(-10) is False


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_controller_type_validation(qtbot: QtBot, sample_int: int) -> None:
    """Test that IntegerEntryController validates integer types correctly."""
    controller = IntegerEntryController(
        sample_int,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid integer values
    valid_values = [0, 1, -1, 100, -100]
    for value in valid_values:
        controller.value = value
        wait_for_debounce(qtbot)
        assert controller.value == value
        assert isinstance(controller.value, int)
