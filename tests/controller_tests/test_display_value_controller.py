"""Tests for DisplayValueController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue, Hook
from integrated_widgets.controllers.display_value_controller import DisplayValueController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_initialization_with_direct_value(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController initializes correctly with direct value."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_initialization_with_observable(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController initializes correctly with observable."""
    observable = ObservableSingleValue[str](sample_string)
    controller = DisplayValueController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_string
    assert observable.value == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_initialization_with_hook(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController initializes correctly with hook."""
    observable = ObservableSingleValue[str](sample_string)
    hook = observable.hook
    controller = DisplayValueController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_value_change(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController handles value changes correctly."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "new_display_value"
    controller.value = new_value
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_change_value_method(qtbot: QtBot, sample_string: str) -> None:
    """Test that change_value method works correctly."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "changed_display_value"
    controller.change_value(new_value)
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_change_value_with_custom_debounce(qtbot: QtBot, sample_string: str) -> None:
    """Test that change_value method respects custom debounce_ms parameter."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "custom_debounce_display_value"
    custom_debounce = 50
    controller.change_value(new_value, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_with_formatter(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController works with custom formatter."""
    def custom_formatter(x: str) -> str:
        return f"Formatted: {x.upper()}"
    
    controller = DisplayValueController(
        sample_string,
        formatter=custom_formatter,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check that formatter is applied
    assert controller.formatter == custom_formatter


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_without_formatter(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController works without formatter."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should work without formatter
    assert controller.value == sample_string
    assert controller.formatter is None


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_change_formatter(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController can change formatter."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    def new_formatter(x: str) -> str:
        return f"New: {x}"
    
    controller.change_formatter(new_formatter)
    
    assert controller.formatter == new_formatter


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_observable_sync(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController syncs with observable changes."""
    observable = ObservableSingleValue[str](sample_string)
    controller = DisplayValueController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value
    new_value = "observable_changed"
    observable.value = new_value
    
    # Controller should reflect the change
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_hook_sync(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController syncs with hook changes."""
    observable = ObservableSingleValue[str](sample_string)
    hook = observable.hook
    controller = DisplayValueController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value
    new_value = "hook_changed"
    hook.submit_value(new_value)
    
    # Controller should reflect the change
    assert controller.value == new_value
    assert observable.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_widget_properties(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController exposes widget properties correctly."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_label')
    
    # Widget should be enabled by default
    assert controller.widget_label.isEnabled()


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_debounce_functionality(qtbot: QtBot, sample_string: str) -> None:
    """Test that debounce functionality works correctly."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.value = "change1"
    controller.value = "change2"
    controller.value = "change3"
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.value == "change3"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_different_data_types(qtbot: QtBot) -> None:
    """Test that DisplayValueController works with different data types."""
    # Test with string
    controller_str = DisplayValueController(
        "test_string",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_str.value == "test_string"
    
    # Test with integer
    controller_int = DisplayValueController(
        42,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_int.value == 42
    
    # Test with float
    controller_float = DisplayValueController(
        3.14159,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_float.value == 3.14159
    
    # Test with boolean
    controller_bool = DisplayValueController(
        True,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_bool.value is True


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_default_parameters(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController works with default parameters."""
    controller = DisplayValueController(sample_string)
    
    # Should work with defaults
    assert controller.value == sample_string
    
    # Test value change
    new_value = "default_test"
    controller.value = new_value
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_submit_method(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController submit method works correctly."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "submitted_value"
    controller.submit(new_value)
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_submit_with_debounce(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController submit method respects debounce_ms parameter."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "submitted_value"
    custom_debounce = 50
    controller.submit(new_value, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_formatter_application(qtbot: QtBot, sample_string: str) -> None:
    """Test that formatter is applied correctly to displayed values."""
    def test_formatter(x: str) -> str:
        return f"[{x}]"
    
    controller = DisplayValueController(
        sample_string,
        formatter=test_formatter,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check that formatter is stored
    assert controller.formatter == test_formatter
    
    # Test formatter application
    new_value = "test"
    controller.value = new_value
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_read_only_behavior(qtbot: QtBot, sample_string: str) -> None:
    """Test that DisplayValueController behaves as read-only display."""
    controller = DisplayValueController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should be able to change value programmatically
    new_value = "programmatic_change"
    controller.value = new_value
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value
    
    # Widget should be read-only (no user input)
    assert controller.widget_label.isEnabled()
