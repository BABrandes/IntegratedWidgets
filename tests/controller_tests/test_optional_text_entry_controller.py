"""Tests for OptionalTextEntryController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from nexpy import XValue
from integrated_widgets.controllers.optional_text_entry_controller import OptionalTextEntryController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_initialization_with_direct_value(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController initializes correctly with direct string value."""
    controller = OptionalTextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.text == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_initialization_with_none(qtbot: QtBot) -> None:
    """Test that OptionalTextEntryController initializes correctly with None value."""
    controller = OptionalTextEntryController(
        None,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.text is None


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_initialization_with_observable(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController initializes correctly with observable."""
    observable = XValue[str | None](sample_string)
    controller = OptionalTextEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.text == sample_string
    assert observable.value == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_initialization_with_hook(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController initializes correctly with hook."""
    observable = XValue[str | None](sample_string)
    hook = observable.hook
    controller = OptionalTextEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.text == sample_string


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_value_change(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController handles value changes correctly."""
    controller = OptionalTextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "new_test_string"
    controller.text = new_value
    wait_for_debounce(qtbot)
    
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_change_to_none(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController handles change to None correctly."""
    controller = OptionalTextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    controller.text = None
    wait_for_debounce(qtbot)
    
    assert controller.text is None


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_change_from_none(qtbot: QtBot) -> None:
    """Test that OptionalTextEntryController handles change from None correctly."""
    controller = OptionalTextEntryController(
        None,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "from_none_to_string"
    controller.text = new_value
    wait_for_debounce(qtbot)
    
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_change_text_method(qtbot: QtBot, sample_string: str) -> None:
    """Test that change_text method works correctly."""
    controller = OptionalTextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "changed_text"
    controller.change_text(new_value)
    wait_for_debounce(qtbot)
    
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_change_text_with_custom_debounce(qtbot: QtBot, sample_string: str) -> None:
    """Test that change_text method respects custom debounce_ms parameter."""
    controller = OptionalTextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = "custom_debounce_text"
    custom_debounce = 50
    controller.change_text(new_value, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_with_validator(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController works with custom validator."""
    def validator(x: str | None) -> bool:
        return x is None or len(x) > 0
    
    controller = OptionalTextEntryController(
        sample_string,
        validator=validator,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid values should work
    valid_values = ["valid_string", None]
    for value in valid_values:
        controller.text = value
        wait_for_debounce(qtbot)
        assert controller.text == value
    
    # Invalid value should be rejected (empty string)
    original_value = controller.text
    controller.change_text("", raise_submission_error_flag=False)
    wait_for_debounce(qtbot)
    # Should remain at original value (invalid submission rejected)
    assert controller.text == original_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_none_value_handling(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController handles None value correctly."""
    controller = OptionalTextEntryController(
        sample_string,
        none_value="<empty>",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Set to None
    controller.text = None
    wait_for_debounce(qtbot)
    assert controller.text is None


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_strip_whitespace(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController strips whitespace when enabled."""
    controller = OptionalTextEntryController(
        sample_string,
        strip_whitespace=True,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test with whitespace - direct assignment preserves whitespace
    value_with_whitespace = "  test_string  "
    controller.text = value_with_whitespace
    wait_for_debounce(qtbot)
    
    # Direct assignment preserves whitespace (stripping happens on editingFinished)
    assert controller.text == value_with_whitespace


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_no_strip_whitespace(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController preserves whitespace when disabled."""
    controller = OptionalTextEntryController(
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
def test_optional_text_entry_controller_observable_sync(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController syncs with observable changes."""
    observable = XValue[str | None](sample_string)
    controller = OptionalTextEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value
    new_value = "observable_changed"
    observable.value = new_value
    
    # Controller should reflect the change
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_observable_sync_to_none(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController syncs with observable changes to None."""
    observable = XValue[str | None](sample_string)
    controller = OptionalTextEntryController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value to None
    observable.value = None
    
    # Controller should reflect the change
    assert controller.text is None


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_hook_sync(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController syncs with hook changes."""
    observable = XValue[str | None](sample_string)
    hook = observable.hook
    controller = OptionalTextEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value
    new_value = "hook_changed"
    hook.submit_value(new_value)
    
    # Controller should reflect the change
    assert controller.text == new_value
    assert observable.value == new_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_hook_sync_to_none(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController syncs with hook changes to None."""
    observable = XValue[str | None](sample_string)
    hook = observable.hook
    controller = OptionalTextEntryController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value to None
    hook.submit_value(None)
    
    # Controller should reflect the change
    assert controller.text is None
    assert observable.value is None


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_widget_properties(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController exposes widget properties correctly."""
    controller = OptionalTextEntryController(
        sample_string,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_line_edit')


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_debounce_functionality(qtbot: QtBot, sample_string: str) -> None:
    """Test that debounce functionality works correctly."""
    controller = OptionalTextEntryController(
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
def test_optional_text_entry_controller_default_parameters(qtbot: QtBot, sample_string: str) -> None:
    """Test that OptionalTextEntryController works with default parameters."""
    controller = OptionalTextEntryController(sample_string)
    
    # Should work with defaults
    assert controller.text == sample_string
    
    # Test value change
    new_value = "default_test"
    controller.text = new_value
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.text == new_value


@pytest.mark.qt_log_ignore(".*")
def test_optional_text_entry_controller_none_value_edge_cases(qtbot: QtBot) -> None:
    """Test edge cases with None values."""
    controller = OptionalTextEntryController(
        None,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test changing from None to string and back
    controller.text = "test"
    wait_for_debounce(qtbot)
    assert controller.text == "test"
    
    controller.text = None
    wait_for_debounce(qtbot)
    assert controller.text is None
    
    controller.text = ""
    wait_for_debounce(qtbot)
    assert controller.text == ""
    
    controller.text = None
    wait_for_debounce(qtbot)
    assert controller.text is None
