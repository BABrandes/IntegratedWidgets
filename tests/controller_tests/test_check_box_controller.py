"""Tests for CheckBoxController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from nexpy import XValue, Hook
from integrated_widgets.controllers.check_box_controller import CheckBoxController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_initialization_with_direct_value(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController initializes correctly with direct boolean value."""
    controller = CheckBoxController(
        sample_bool,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_bool


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_initialization_with_observable(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController initializes correctly with observable."""
    observable = XValue[bool](sample_bool)
    controller = CheckBoxController(
        observable,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_bool
    assert observable.value == sample_bool


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_initialization_with_hook(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController initializes correctly with hook."""
    observable = XValue[bool](sample_bool)
    hook = observable.hook
    controller = CheckBoxController(
        hook,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.value == sample_bool


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_value_change(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController handles value changes correctly."""
    controller = CheckBoxController(
        sample_bool,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = not sample_bool
    controller.value = new_value
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_text_property(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController text parameter works correctly."""
    text = "Custom Checkbox Text"
    controller = CheckBoxController(
        sample_bool,
        text=text,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check that text was set correctly (stored internally, not as a property)
    # The text is used internally by the widget
    assert controller.widget_check_box.text() == text


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_default_text(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController uses default text when not provided."""
    controller = CheckBoxController(
        sample_bool,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should have empty text by default
    assert controller.widget_check_box.text() == ""


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_observable_sync(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController syncs with observable changes."""
    observable = XValue[bool](sample_bool)
    controller = CheckBoxController(
        observable,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value
    new_value = not sample_bool
    observable.value = new_value
    
    # Controller should reflect the change
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_hook_sync(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController syncs with hook changes."""
    observable = XValue[bool](sample_bool)
    hook = observable.hook
    controller = CheckBoxController(
        hook,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value using submit_value
    new_value = not sample_bool
    hook.submit_value(new_value)
    
    # Controller should reflect the change
    assert controller.value == new_value
    assert observable.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_widget_properties(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController exposes widget properties correctly."""
    controller = CheckBoxController(
        sample_bool,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_check_box')
    
    # Widget should be enabled by default
    assert controller.widget_check_box.isEnabled() is True


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_debounce_functionality(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that debounce functionality works correctly."""
    controller = CheckBoxController(
        sample_bool,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.value = True
    controller.value = False
    controller.value = True
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.value is True


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_boolean_values(qtbot: QtBot) -> None:
    """Test that CheckBoxController handles different boolean values correctly."""
    # Test with True
    controller_true = CheckBoxController(
        True,
        text="True Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_true.value is True
    
    # Test with False
    controller_false = CheckBoxController(
        False,
        text="False Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    assert controller_false.value is False


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_default_parameters(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController works with default parameters."""
    controller = CheckBoxController(sample_bool)
    
    # Should work with defaults
    assert controller.value == sample_bool
    assert controller.widget_check_box.text() == ""
    
    # Test value change
    new_value = not sample_bool
    controller.value = new_value
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_submit_method(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController submit method works correctly."""
    controller = CheckBoxController(
        sample_bool,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = not sample_bool
    controller.submit(new_value)
    wait_for_debounce(qtbot)
    
    assert controller.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_check_box_controller_submit_with_debounce(qtbot: QtBot, sample_bool: bool) -> None:
    """Test that CheckBoxController submit method respects debounce_ms parameter."""
    controller = CheckBoxController(
        sample_bool,
        text="Test Checkbox",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = not sample_bool
    custom_debounce = 50
    controller.submit(new_value, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.value == new_value
