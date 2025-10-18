"""Tests for DictOptionalSelectionController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot
from typing import Any

from observables import ObservableSingleValue, ObservableOptionalSelectionDict, Hook
from integrated_widgets.controllers.dict_optional_selection_controller import DictOptionalSelectionController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.fixture
def sample_dict() -> dict[str, str]:
    """Sample dictionary for testing."""
    return {
        "apple": "red",
        "banana": "yellow", 
        "orange": "orange",
        "grape": "purple"
    }


@pytest.fixture
def sample_dict_int() -> dict[int, str]:
    """Sample dictionary with integer keys for testing."""
    return {
        1: "one",
        2: "two",
        3: "three"
    }


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_initialization_with_direct_value(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that DictOptionalSelectionController initializes correctly with direct dictionary value."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.dict_value == sample_dict
    assert controller.selected_key == "apple"
    assert controller.selected_value == "red"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_initialization_with_none_selection(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that DictOptionalSelectionController initializes correctly with None selection."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key=None,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.dict_value == sample_dict
    assert controller.selected_key is None
    assert controller.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_initialization_with_observable(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that DictOptionalSelectionController initializes correctly with observable."""
    observable = ObservableOptionalSelectionDict[str, str](sample_dict, "banana")
    controller = DictOptionalSelectionController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.dict_value == sample_dict
    assert controller.selected_key == "banana"
    assert controller.selected_value == "yellow"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_initialization_with_hook(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that DictOptionalSelectionController initializes correctly with hook."""
    observable = ObservableSingleValue[str | None]("orange")
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key=observable.hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial values
    assert controller.dict_value == sample_dict
    assert controller.selected_key == "orange"
    assert controller.selected_value == "orange"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_selected_key_setter(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that selected_key setter works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test setting to different key
    controller.selected_key = "banana"
    wait_for_debounce(qtbot)
    
    assert controller.selected_key == "banana"
    assert controller.selected_value == "yellow"
    
    # Test setting to None
    controller.selected_key = None
    wait_for_debounce(qtbot)
    
    assert controller.selected_key is None
    assert controller.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_change_selected_key(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that change_selected_key method works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test changing to different key
    controller.change_selected_key("grape")
    wait_for_debounce(qtbot)
    
    assert controller.selected_key == "grape"
    assert controller.selected_value == "purple"
    
    # Test changing to None
    controller.change_selected_key(None)
    wait_for_debounce(qtbot)
    
    assert controller.selected_key is None
    assert controller.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_dict_like_interface(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that dict-like interface works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test __getitem__
    assert controller["apple"] == "red"
    assert controller["banana"] == "yellow"
    
    # Test __setitem__
    controller["kiwi"] = "green"
    wait_for_debounce(qtbot)
    assert controller["kiwi"] == "green"
    assert "kiwi" in controller.dict_value
    
    # Test __contains__
    assert "apple" in controller
    assert "kiwi" in controller
    assert "mango" not in controller
    
    # Test __len__
    assert len(controller) == 5  # Original 4 + kiwi
    
    # Test keys(), values(), items()
    keys = controller.keys()
    values = controller.values()
    items = controller.items()
    
    assert "kiwi" in keys
    assert "green" in values
    assert ("kiwi", "green") in items
    
    # Test get()
    assert controller.get("apple") == "red"
    assert controller.get("mango") is None
    assert controller.get("mango", "default") == "default"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_dict_modification(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that dictionary modification works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test adding new key-value pair
    controller["mango"] = "yellow"
    wait_for_debounce(qtbot)
    
    assert controller["mango"] == "yellow"
    assert "mango" in controller.dict_value
    
    # Test updating existing key
    controller["apple"] = "green"
    wait_for_debounce(qtbot)
    
    assert controller["apple"] == "green"
    assert controller.selected_value == "green"  # Should update selected value
    
    # Test pop()
    value = controller.pop("mango")
    wait_for_debounce(qtbot)
    
    assert value == "yellow"
    assert "mango" not in controller.dict_value
    
    # Test update()
    controller.update({"pear": "brown", "cherry": "red"})
    wait_for_debounce(qtbot)
    
    assert controller["pear"] == "brown"
    assert controller["cherry"] == "red"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_delete_key(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that deleting keys works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test deleting non-selected key
    del controller["banana"]
    wait_for_debounce(qtbot)
    
    assert "banana" not in controller.dict_value
    assert controller.selected_key == "apple"  # Selection should remain
    
    # Test deleting selected key (should raise error)
    with pytest.raises(ValueError, match="Cannot delete key 'apple' because it is currently selected"):
        del controller["apple"]


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_clear_selection(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that clear_selection works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    controller.clear_selection()
    wait_for_debounce(qtbot)
    
    assert controller.selected_key is None
    assert controller.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_change_dict_value(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that changing dictionary value works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test changing to a dict that contains the current selected key
    new_dict = {"apple": "green", "kiwi": "green", "mango": "yellow"}
    controller.dict_value = new_dict
    wait_for_debounce(qtbot)
    
    assert controller.dict_value == new_dict
    assert controller.selected_key == "apple"  # Should remain the same
    assert controller.selected_value == "green"  # Should update to new value


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_change_dict_and_key(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that change_dict_and_key works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_dict = {"kiwi": "green", "mango": "yellow"}
    controller.change_dict_and_key(new_dict, "kiwi")
    wait_for_debounce(qtbot)
    
    assert controller.dict_value == new_dict
    assert controller.selected_key == "kiwi"
    assert controller.selected_value == "green"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_change_all(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that change_all works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_dict = {"kiwi": "green", "mango": "yellow"}
    controller.change_all(new_dict, "mango", "yellow")
    wait_for_debounce(qtbot)
    
    assert controller.dict_value == new_dict
    assert controller.selected_key == "mango"
    assert controller.selected_value == "yellow"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_formatter(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that formatter works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        formatter=lambda key: f"Key: {key.upper()}",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.formatter("apple") == "Key: APPLE"
    
    # Test changing formatter
    controller.formatter = lambda key: f"Item: {key}"
    assert controller.formatter("banana") == "Item: banana"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_none_option_text(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that none_option_text works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        none_option_text="No Selection",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.none_option_text == "No Selection"
    
    # Test changing none_option_text
    controller.none_option_text = "Empty"
    assert controller.none_option_text == "Empty"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_hooks(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that hooks work correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test that hooks are accessible
    assert controller.dict_hook is not None
    assert controller.selected_key_hook is not None
    assert controller.selected_value_hook is not None
    
    # Test hook values
    assert controller.dict_hook.value == sample_dict
    assert controller.selected_key_hook.value == "apple"
    assert controller.selected_value_hook.value == "red"


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_copy(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that copy works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test copy
    dict_copy = controller.copy()
    assert dict_copy == sample_dict
    assert dict_copy is not sample_dict  # Should be a different object


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_integer_keys(qtbot: QtBot, sample_dict_int: dict[int, str]) -> None:
    """Test that controller works with integer keys."""
    controller = DictOptionalSelectionController(
        sample_dict_int,
        selected_key=1,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.selected_key == 1
    assert controller.selected_value == "one"
    
    # Test dict operations with integer keys
    controller[4] = "four"
    wait_for_debounce(qtbot)
    
    assert controller[4] == "four"
    assert 4 in controller


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_error_handling(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that error handling works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test getting invalid key
    with pytest.raises(KeyError):
        _ = controller["invalid_key"]
    
    # Test deleting invalid key
    with pytest.raises(KeyError):
        del controller["invalid_key"]


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_add_values_callback(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that add_values_to_be_updated_callback works correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=0  # No debounce for immediate testing
    )
    
    # Test submitting only selected_key - should complete selected_value
    controller.submit_value("selected_key", "banana")
    wait_for_debounce(qtbot)
    
    assert controller.selected_key == "banana"
    assert controller.selected_value == "yellow"
    
    # Test submitting only selected_key as None - should complete selected_value as None
    controller.submit_value("selected_key", None)
    wait_for_debounce(qtbot)
    
    assert controller.selected_key is None
    assert controller.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_dict_optional_selection_controller_widget_creation(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that widgets are created correctly."""
    controller = DictOptionalSelectionController(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test that widgets are accessible
    assert controller.widget_combobox is not None
    assert controller.widget_label is not None
    
    # Wait for widget initialization
    wait_for_debounce(qtbot)
    
    # Test that combobox has correct number of items (None option + dict keys)
    assert controller.widget_combobox.count() == len(sample_dict) + 1  # +1 for None option
