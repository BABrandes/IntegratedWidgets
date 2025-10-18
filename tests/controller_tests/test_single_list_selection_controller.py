"""Tests for SingleListSelectionController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue, ObservableSet
from integrated_widgets.controllers.single_list_selection_controller import SingleListSelectionController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_initialization_with_direct_values(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController initializes correctly with direct values."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_option == selected_option
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_initialization_with_none_selected(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController initializes correctly with None selected."""
    available_options = set(sample_string_list)
    
    controller = SingleListSelectionController(
        None,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_option is None
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_initialization_with_observables(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController initializes correctly with observables."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    selected_observable = ObservableSingleValue[str | None](selected_option)
    available_observable = ObservableSet[str](available_options)
    
    controller = SingleListSelectionController(
        selected_observable,
        available_observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_option == selected_option
    assert controller.available_options == available_options
    assert selected_observable.value == selected_option
    assert available_observable.value == available_options


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_initialization_with_hooks(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController initializes correctly with hooks."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    selected_observable = ObservableSingleValue[str | None](selected_option)
    available_observable = ObservableSet[str](available_options)
    
    selected_hook = selected_observable.hook
    available_hook = available_observable.value_hook
    
    controller = SingleListSelectionController(
        selected_hook,
        available_hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_option == selected_option
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_selected_option_change(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController handles selected option changes correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_selected = sample_string_list[1]
    controller.selected_option = new_selected
    wait_for_debounce(qtbot)
    
    assert controller.selected_option == new_selected


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_available_options_change(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController handles available options changes correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_available = set(sample_string_list + ["new_option"])
    controller.available_options = new_available
    wait_for_debounce(qtbot)
    
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_change_selected_option_method(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change_selected_option method works correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_selected = sample_string_list[1]
    controller.change_selected_option(new_selected)
    wait_for_debounce(qtbot)
    
    assert controller.selected_option == new_selected


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_change_available_options_method(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change_available_options method works correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_available = set(sample_string_list + ["new_option"])
    controller.change_available_options(new_available)
    wait_for_debounce(qtbot)
    
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_change_both_method(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change_selected_option_and_available_options method works correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_selected = sample_string_list[1]
    new_available = set(sample_string_list + ["new_option"])
    
    controller.change_selected_option_and_available_options(new_selected, new_available)
    wait_for_debounce(qtbot)
    
    assert controller.selected_option == new_selected
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_change_methods_with_custom_debounce(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change methods respect custom debounce_ms parameter."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    custom_debounce = 50
    
    # Test change_selected_option with custom debounce
    new_selected = sample_string_list[1]
    controller.change_selected_option(new_selected, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)
    assert controller.selected_option == new_selected
    
    # Test change_available_options with custom debounce
    new_available = set(sample_string_list + ["new_option"])
    controller.change_available_options(new_available, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_with_formatter(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController works with custom formatter."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    def custom_formatter(x: str) -> str:
        return f"Item: {x.upper()}"
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        formatter=custom_formatter,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.selected_option == selected_option
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_with_order_by_callable(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController works with custom order_by_callable."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    def custom_order(x: str) -> str:
        return x[::-1]  # Reverse string for ordering
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        order_by_callable=custom_order,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.selected_option == selected_option
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_allow_deselection(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController handles allow_deselection correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    # Test with allow_deselection=True (default)
    controller_allow = SingleListSelectionController(
        selected_option,
        available_options,
        allow_deselection=True,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    controller_allow.selected_option = None
    wait_for_debounce(qtbot)
    assert controller_allow.selected_option is None
    
    # Test with allow_deselection=False
    controller_disallow = SingleListSelectionController(
        selected_option,
        available_options,
        allow_deselection=False,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should not allow None when deselection is disabled
    original_selected = controller_disallow.selected_option
    controller_disallow.selected_option = None
    wait_for_debounce(qtbot)
    # Should revert to original value
    assert controller_disallow.selected_option == original_selected


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_observable_sync(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController syncs with observable changes."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    selected_observable = ObservableSingleValue[str | None](selected_option)
    available_observable = ObservableSet[str](available_options)
    
    controller = SingleListSelectionController(
        selected_observable,
        available_observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable values
    new_selected = sample_string_list[1]
    new_available = set(sample_string_list + ["new_option"])
    
    selected_observable.value = new_selected
    available_observable.value = new_available
    
    # Controller should reflect the changes
    assert controller.selected_option == new_selected
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_hook_sync(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController syncs with hook changes."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    selected_observable = ObservableSingleValue[str | None](selected_option)
    available_observable = ObservableSet[str](available_options)
    
    selected_hook = selected_observable.hook
    available_hook = available_observable.value_hook
    
    controller = SingleListSelectionController(
        selected_hook,
        available_hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook values
    new_selected = sample_string_list[1]
    new_available = set(sample_string_list + ["new_option"])
    
    selected_hook.submit_value(new_selected)
    available_hook.submit_value(new_available)
    
    # Controller should reflect the changes
    assert controller.selected_option == new_selected
    assert controller.available_options == new_available
    assert selected_observable.value == new_selected
    assert available_observable.value == new_available


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_widget_properties(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController exposes widget properties correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_list')
    assert hasattr(controller, 'selected_option_hook')
    assert hasattr(controller, 'available_options_hook')

@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_debounce_functionality(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that debounce functionality works correctly."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.selected_option = sample_string_list[1]
    controller.selected_option = sample_string_list[2]
    controller.selected_option = sample_string_list[0]
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.selected_option == sample_string_list[0]


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_default_parameters(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController works with default parameters."""
    available_options = set(sample_string_list)
    selected_option = sample_string_list[0]
    
    controller = SingleListSelectionController(selected_option, available_options)
    
    # Should work with defaults
    assert controller.selected_option == selected_option
    assert controller.available_options == available_options
    
    # Test value change
    new_selected = sample_string_list[1]
    controller.selected_option = new_selected
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.selected_option == new_selected


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_empty_available_options(qtbot: QtBot) -> None:
    """Test that SingleListSelectionController handles empty available options."""
    controller = SingleListSelectionController[str](
        None,
        set(),
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.selected_option is None
    assert controller.available_options == set()
    
    # Should handle adding options
    new_options = {"option1", "option2"}
    controller.available_options = new_options
    wait_for_debounce(qtbot)
    
    assert controller.available_options == new_options


@pytest.mark.qt_log_ignore(".*")
def test_single_list_selection_controller_selected_not_in_available(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that SingleListSelectionController handles selected option not in available options."""
    available_options = set(sample_string_list)
    selected_option = "not_in_available"
    
    controller = SingleListSelectionController(
        selected_option,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should still work
    assert controller.selected_option == selected_option
    assert controller.available_options == available_options
