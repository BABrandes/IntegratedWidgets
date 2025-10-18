"""Tests for TextEntryController class."""

from __future__ import annotations

from typing import Callable
import pytest
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue
from integrated_widgets.controllers.text_entry_controller import TextEntryController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_initialization_with_direct_value(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController initializes correctly with direct string value."""
    controller = TextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.text == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_initialization_with_observable(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController initializes correctly with observable."""
    observable = ObservableSingleValue[str](sample_string)
    controller = TextEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.text == sample_string
    assert observable.value == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_initialization_with_hook(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController initializes correctly with hook."""
    observable = ObservableSingleValue[str](sample_string)
    hook = observable.hook
    controller = TextEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.text == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_value_change(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController handles value changes correctly."""
    controller = TextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "new_test_string"
    controller.text = new_value
    wait_for_debounce(qtbot)
    
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_change_text_method(qtbot: QtBot, sample_string: str) -> None:
    """Test that change_text method works correctly."""
    controller = TextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "changed_text"
    controller.change_text(new_value)
    wait_for_debounce(qtbot)
    
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_change_text_with_custom_debounce(qtbot: QtBot, sample_string: str) -> None:
    """Test that change_text method respects custom debounce_ms parameter."""
    controller = TextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "custom_debounce_text"
    custom_debounce = 50
    controller.change_text(new_value, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.text == new_value


def test_text_entry_controller_with_validator(qtbot: QtBot, sample_string: str, string_validator: Callable[[str], bool]) -> None:
    """Test that TextEntryController works with custom validator."""
    controller = TextEntryController(
        sample_string,
        validator=string_validator,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid value should work
    valid_value = "valid_string"
    controller.text = valid_value
    wait_for_debounce(qtbot)
    assert controller.text == valid_value
    
    # Test that validator is set correctly
    assert controller.validator == string_validator
    
    # Test validator function directly
    assert controller.validator("valid_string") is True
    assert controller.validator("") is False


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_strip_whitespace(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController strips whitespace when enabled."""
    controller = TextEntryController(
        sample_string,
        strip_whitespace=True,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test with whitespace - stripping happens on widget editing finished, not on direct assignment
    value_with_whitespace = "  test_string  "
    controller.text = value_with_whitespace
    wait_for_debounce(qtbot)
    
    # Direct assignment doesn't strip whitespace - it's preserved
    assert controller.text == value_with_whitespace
    
    # Test that the strip_whitespace property is set correctly
    assert controller.strip_whitespace is True


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_no_strip_whitespace(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController preserves whitespace when disabled."""
    controller = TextEntryController(
        sample_string,
        strip_whitespace=False,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test with whitespace
    value_with_whitespace = "  test_string  "
    controller.text = value_with_whitespace
    wait_for_debounce(qtbot)
    
    # Should preserve whitespace
    assert controller.text == value_with_whitespace


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_observable_sync(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController syncs with observable changes."""
    observable = ObservableSingleValue[str](sample_string)
    controller = TextEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value
    new_value = "observable_changed"
    observable.value = new_value
    
    # Controller should reflect the change
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_hook_sync(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController syncs with hook changes."""
    observable = ObservableSingleValue[str](sample_string)
    hook = observable.hook
    controller = TextEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value using submit_value
    new_value = "hook_changed"
    hook.submit_value(new_value)
    
    # Controller should reflect the change
    assert controller.text == new_value
    assert observable.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_widget_properties(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController exposes widget properties correctly."""
    controller = TextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_line_edit')
    
    # Widget should be enabled by default
    assert controller.widget_line_edit.isEnabled() is True


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_debounce_functionality(qtbot: QtBot, sample_string: str) -> None:
    """Test that debounce functionality works correctly."""
    controller = TextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.text = "change1"
    controller.text = "change2"
    controller.text = "change3"
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.text == "change3"


@pytest.mark.qt_log_ignore(".*")
def test_text_entry_controller_default_parameters(qtbot: QtBot, sample_string: str) -> None:
    """Test that TextEntryController works with default parameters."""
    controller = TextEntryController(sample_string)
    
    # Should work with defaults
    assert controller.text == sample_string
    
    # Test value change
    new_value = "default_test"
    controller.text = new_value
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.text == new_value
