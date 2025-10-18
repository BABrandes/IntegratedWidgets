"""Tests for IQtDictOptionalSelection widget."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from observables import ObservableOptionalSelectionDict
from integrated_widgets import IQtDictOptionalSelection
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


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_initialization_with_direct_value(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that IQtDictOptionalSelection initializes correctly with direct dictionary value."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Check initial values
    assert widget.dict_value == sample_dict
    assert widget.selected_key == "apple"
    assert widget.selected_value == "red"


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_initialization_with_none_selection(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that IQtDictOptionalSelection initializes correctly with None selection."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key=None,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Check initial values
    assert widget.dict_value == sample_dict
    assert widget.selected_key is None
    assert widget.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_initialization_with_observable(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that IQtDictOptionalSelection initializes correctly with observable."""
    observable = ObservableOptionalSelectionDict[str, str](sample_dict, "banana")
    widget = IQtDictOptionalSelection(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Check initial values
    assert widget.dict_value == sample_dict
    assert widget.selected_key == "banana"
    assert widget.selected_value == "yellow"


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_selected_key_setter(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that selected_key setter works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test setting to different key
    widget.selected_key = "banana"
    wait_for_debounce(qtbot)
    
    assert widget.selected_key == "banana"
    assert widget.selected_value == "yellow"
    
    # Test setting to None
    widget.selected_key = None
    wait_for_debounce(qtbot)
    
    assert widget.selected_key is None
    assert widget.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_dict_like_interface(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that dict-like interface works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test __getitem__
    assert widget["apple"] == "red"
    assert widget["banana"] == "yellow"
    
    # Test __setitem__
    widget["kiwi"] = "green"
    wait_for_debounce(qtbot)
    assert widget["kiwi"] == "green"
    assert "kiwi" in widget.dict_value
    
    # Test __contains__
    assert "apple" in widget
    assert "kiwi" in widget
    assert "mango" not in widget
    
    # Test __len__
    assert len(widget) == 5  # Original 4 + kiwi
    
    # Test keys(), values(), items()
    keys = widget.keys()
    values = widget.values()
    items = widget.items()
    
    assert "kiwi" in keys
    assert "green" in values
    assert ("kiwi", "green") in items
    
    # Test get()
    assert widget.get("apple") == "red"
    assert widget.get("mango") is None
    assert widget.get("mango", "default") == "default"


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_dict_modification(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that dictionary modification works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test adding new key-value pair
    widget["mango"] = "yellow"
    wait_for_debounce(qtbot)
    
    assert widget["mango"] == "yellow"
    assert "mango" in widget.dict_value
    
    # Test updating existing key
    widget["apple"] = "green"
    wait_for_debounce(qtbot)
    
    assert widget["apple"] == "green"
    assert widget.selected_value == "green"  # Should update selected value
    
    # Test pop()
    value = widget.pop("mango")
    wait_for_debounce(qtbot)
    
    assert value == "yellow"
    assert "mango" not in widget.dict_value
    
    # Test update() through controller
    widget.controller.update({"pear": "brown", "cherry": "red"})
    wait_for_debounce(qtbot)
    
    assert widget["pear"] == "brown"
    assert widget["cherry"] == "red"


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_delete_key(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that deleting keys works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test deleting non-selected key
    del widget["banana"]
    wait_for_debounce(qtbot)
    
    assert "banana" not in widget.dict_value
    assert widget.selected_key == "apple"  # Selection should remain
    
    # Test deleting selected key (should raise error)
    with pytest.raises(ValueError, match="Cannot delete key 'apple' because it is currently selected"):
        del widget["apple"]


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_clear_selection(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that clear_selection works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    widget.controller.clear_selection()
    wait_for_debounce(qtbot)
    
    assert widget.selected_key is None
    assert widget.selected_value is None


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_change_dict_value(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that changing dictionary value works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test changing to a dict that contains the current selected key
    new_dict = {"apple": "green", "kiwi": "green", "mango": "yellow"}
    widget.dict_value = new_dict
    wait_for_debounce(qtbot)
    
    assert widget.dict_value == new_dict
    assert widget.selected_key == "apple"  # Should remain the same
    assert widget.selected_value == "green"  # Should update to new value


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_formatter(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that formatter works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        formatter=lambda key: f"Key: {key.upper()}",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    assert widget.controller.formatter("apple") == "Key: APPLE"
    
    # Test changing formatter
    widget.controller.formatter = lambda key: f"Item: {key}" # type: ignore
    assert widget.controller.formatter("banana") == "Item: banana" # type: ignore


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_none_option_text(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that none_option_text works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        none_option_text="No Selection",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    assert widget.controller.none_option_text == "No Selection"
    
    # Test changing none_option_text
    widget.controller.none_option_text = "Empty"
    assert widget.controller.none_option_text == "Empty"


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_hooks(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that hooks work correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test that hooks are accessible
    assert widget.dict_hook is not None
    assert widget.selected_key_hook is not None
    assert widget.selected_value_hook is not None
    
    # Test hook values
    assert widget.dict_hook.value == sample_dict
    assert widget.selected_key_hook.value == "apple"
    assert widget.selected_value_hook.value == "red"


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_copy(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that copy works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test copy
    dict_copy = widget.copy()
    assert dict_copy == sample_dict
    assert dict_copy is not sample_dict  # Should be a different object


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_integer_keys(qtbot: QtBot) -> None:
    """Test that widget works with integer keys."""
    sample_dict_int = {1: "one", 2: "two", 3: "three"}
    
    widget = IQtDictOptionalSelection(
        sample_dict_int,
        selected_key=1,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    assert widget.selected_key == 1
    assert widget.selected_value == "one"
    
    # Test dict operations with integer keys
    widget[4] = "four"
    wait_for_debounce(qtbot)
    
    assert widget[4] == "four"
    assert 4 in widget


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_error_handling(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that error handling works correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test getting invalid key
    with pytest.raises(KeyError):
        _ = widget["invalid_key"]
    
    # Test deleting invalid key
    with pytest.raises(KeyError):
        del widget["invalid_key"]


@pytest.mark.qt_log_ignore(".*")
def test_iqt_dict_optional_selection_widget_creation(qtbot: QtBot, sample_dict: dict[str, str]) -> None:
    """Test that widgets are created correctly."""
    widget = IQtDictOptionalSelection(
        sample_dict,
        selected_key="apple",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    qtbot.addWidget(widget)
    
    # Test that widgets are accessible through controller
    assert widget.controller.widget_combobox is not None
    assert widget.controller.widget_label is not None
    
    # Wait for widget initialization
    wait_for_debounce(qtbot)
    
    # Test that combobox has correct number of items (None option + dict keys)
    assert widget.controller.widget_combobox.count() == len(sample_dict) + 1  # +1 for None option
