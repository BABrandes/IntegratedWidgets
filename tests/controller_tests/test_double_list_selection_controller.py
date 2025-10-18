"""Tests for DoubleListSelectionController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from observables import ObservableSet
from integrated_widgets.controllers.double_list_selection_controller import DoubleListSelectionController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_initialization_with_direct_values(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController initializes correctly with direct values."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0], sample_string_list[1]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_initialization_with_empty_selected(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController initializes correctly with empty selected options."""
    available_options = set(sample_string_list)
    selected_options = set[str]()
    
    controller = DoubleListSelectionController[str](
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_initialization_with_observables(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController initializes correctly with observables."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0], sample_string_list[1]}
    
    selected_observable = ObservableSet[str](selected_options)
    available_observable = ObservableSet[str](available_options)
    
    controller = DoubleListSelectionController(
        selected_observable,
        available_observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options
    assert selected_observable.value == selected_options
    assert available_observable.value == available_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_initialization_with_hooks(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController initializes correctly with hooks."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0], sample_string_list[1]}
    
    selected_observable = ObservableSet[str](selected_options)
    available_observable = ObservableSet[str](available_options)
    
    selected_hook = selected_observable.value_hook
    available_hook = available_observable.value_hook
    
    controller = DoubleListSelectionController(
        selected_hook,
        available_hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_selected_options_change(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController handles selected options changes correctly."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_selected = {sample_string_list[1], sample_string_list[2]}
    controller.selected_options = new_selected
    wait_for_debounce(qtbot)
    
    assert controller.selected_options == new_selected


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_available_options_change(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController handles available options changes correctly."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_available = set(sample_string_list + ["new_option"])
    controller.available_options = new_available
    wait_for_debounce(qtbot)
    
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_change_selected_options_method(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change_selected_options method works correctly."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_selected = {sample_string_list[1], sample_string_list[2]}
    controller.change_selected_options(new_selected)
    wait_for_debounce(qtbot)
    
    assert controller.selected_options == new_selected


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_change_available_options_method(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change_available_options method works correctly."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_available = set(sample_string_list + ["new_option"])
    controller.change_available_options(new_available)
    wait_for_debounce(qtbot)
    
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_change_both_method(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change_selected_options_and_available_options method works correctly."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_selected = {sample_string_list[1], sample_string_list[2]}
    new_available = set(sample_string_list + ["new_option"])
    
    controller.change_selected_options_and_available_options(new_selected, new_available)
    wait_for_debounce(qtbot)
    
    assert controller.selected_options == new_selected
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_change_methods_with_custom_debounce(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that change methods respect custom debounce_ms parameter."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    custom_debounce = 50
    
    # Test change_selected_options with custom debounce
    new_selected = {sample_string_list[1], sample_string_list[2]}
    controller.change_selected_options(new_selected, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)
    assert controller.selected_options == new_selected
    
    # Test change_available_options with custom debounce
    new_available = set(sample_string_list + ["new_option"])
    controller.change_available_options(new_available, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_with_order_by_callable(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController works with custom order_by_callable."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    def custom_order(x: str) -> str:
        return x[::-1]  # Reverse string for ordering
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        order_by_callable=custom_order,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_observable_sync(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController syncs with observable changes."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    selected_observable = ObservableSet[str](selected_options)
    available_observable = ObservableSet[str](available_options)
    
    controller = DoubleListSelectionController(
        selected_observable,
        available_observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable values
    new_selected = {sample_string_list[1], sample_string_list[2]}
    new_available = set(sample_string_list + ["new_option"])
    
    selected_observable.value = new_selected
    available_observable.value = new_available
    
    # Controller should reflect the changes
    assert controller.selected_options == new_selected
    assert controller.available_options == new_available


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_hook_sync(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController syncs with hook changes."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    selected_observable = ObservableSet[str](selected_options)
    available_observable = ObservableSet[str](available_options)
    
    selected_hook = selected_observable.value_hook
    available_hook = available_observable.value_hook
    
    controller = DoubleListSelectionController(
        selected_hook,
        available_hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook values
    new_selected = {sample_string_list[1], sample_string_list[2]}
    new_available = set(sample_string_list + ["new_option"])
    
    selected_hook.submit_value(new_selected)
    available_hook.submit_value(new_available)
    
    # Controller should reflect the changes
    assert controller.selected_options == new_selected
    assert controller.available_options == new_available
    assert selected_observable.value == new_selected
    assert available_observable.value == new_available


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_widget_properties(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController exposes widget properties correctly."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_selected_list')
    assert hasattr(controller, 'widget_available_list')
    assert hasattr(controller, 'widget_button_move_to_selected')
    assert hasattr(controller, 'widget_button_remove_from_selected')
    assert hasattr(controller, 'selected_options_hook')
    assert hasattr(controller, 'available_options_hook')
    
    # Widgets should be enabled by default
    assert controller.widget_selected_list.isEnabled()
    assert controller.widget_available_list.isEnabled()


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_debounce_functionality(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that debounce functionality works correctly."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.selected_options = {sample_string_list[1]}
    controller.selected_options = {sample_string_list[2]}
    controller.selected_options = {sample_string_list[0], sample_string_list[1]}
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.selected_options == {sample_string_list[0], sample_string_list[1]}


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_default_parameters(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController works with default parameters."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0]}
    
    controller = DoubleListSelectionController(selected_options, available_options)
    
    # Should work with defaults
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options
    
    # Test value change
    new_selected = {sample_string_list[1], sample_string_list[2]}
    controller.selected_options = new_selected
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.selected_options == new_selected


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_empty_sets(qtbot: QtBot) -> None:
    """Test that DoubleListSelectionController handles empty sets correctly."""
    controller = DoubleListSelectionController[str](
        set(),
        set(),
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.selected_options == set()
    assert controller.available_options == set()
    
    # Should handle adding options
    new_options = {"option1", "option2", "option3"}
    controller.available_options = new_options
    wait_for_debounce(qtbot)
    
    assert controller.available_options == new_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_selected_not_in_available(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController handles selected options not in available options."""
    available_options = set(sample_string_list)
    selected_options = {"not_in_available1", "not_in_available2"}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should still work
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_intersection_handling(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController handles intersection between selected and available options."""
    available_options = set(sample_string_list)
    selected_options = {sample_string_list[0], sample_string_list[1]}
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should work with intersection
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options
    
    # Test removing from selected (moving back to available)
    new_selected = {sample_string_list[0]}  # Remove sample_string_list[1]
    controller.selected_options = new_selected
    wait_for_debounce(qtbot)
    
    assert controller.selected_options == new_selected
    assert sample_string_list[1] in controller.available_options


@pytest.mark.qt_log_ignore(".*")
def test_double_list_selection_controller_all_selected(qtbot: QtBot, sample_string_list: list[str]) -> None:
    """Test that DoubleListSelectionController handles all options being selected."""
    available_options = set(sample_string_list)
    selected_options = set(sample_string_list)  # All options selected
    
    controller = DoubleListSelectionController(
        selected_options,
        available_options,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Should work with all selected
    assert controller.selected_options == selected_options
    assert controller.available_options == available_options
    
    # Available options should remain unchanged (not automatically filtered)
    assert controller.available_options == available_options
