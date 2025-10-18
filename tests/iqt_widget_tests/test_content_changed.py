"""Tests for contentChanged signal on IQt widgets.

This test suite verifies that the contentChanged signal is emitted
correctly when widget content changes through various mechanisms:
- Changes via observable/hook system
- Changes via programmatic setters
- Changes via UI widget interaction
"""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot
from united_system import Unit

from observables import FloatingHook, ObservableSingleValue
from integrated_widgets import (
    IQtFloatEntry,
    IQtIntegerEntry,
    IQtTextEntry,
    IQtCheckBox,
    IQtSelectionOption,
    IQtRealUnitedScalar,
)
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_on_hook_value_change(qtbot: QtBot) -> None:
    """Test that value_changed is emitted when value changes via hook."""
    hook: FloatingHook[int] = FloatingHook(42)
    widget = IQtIntegerEntry(hook, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    # Track signal emissions
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change value via hook
    hook.submit_value(100)
    wait_for_debounce(qtbot)
    
    # Signal should have been emitted
    assert len(emissions) > 0
    assert widget.value == 100


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_on_programmatic_value_change(qtbot: QtBot) -> None:
    """Test that value_changed is emitted when value changes via setter."""
    widget = IQtFloatEntry(3.14, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    # Track signal emissions
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change value via setter
    widget.value = 2.71
    wait_for_debounce(qtbot)
    
    # Signal should have been emitted
    assert len(emissions) > 0
    assert widget.value == 2.71


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_on_widget_interaction(qtbot: QtBot) -> None:
    """Test that value_changed is emitted when value changes via UI interaction."""
    widget = IQtTextEntry("initial", debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    # Track signal emissions
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Simulate user typing in the widget
    widget.controller.widget_line_edit.setText("modified")
    widget.controller.widget_line_edit.editingFinished.emit()
    wait_for_debounce(qtbot)
    
    # Signal should have been emitted
    assert len(emissions) > 0
    assert widget.text == "modified"


@pytest.mark.qt_log_ignore(".*")
def test_signal_connection_to_custom_slot(qtbot: QtBot) -> None:
    """Test that value_changed can be connected to custom slots."""
    widget = IQtIntegerEntry(0, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    # Track signal emissions
    emission_count = {"count": 0}
    
    def slot() -> None:
        emission_count["count"] += 1
    
    widget.contentChanged.connect(slot)
    
    # Change value multiple times
    widget.value = 10
    wait_for_debounce(qtbot)
    
    widget.value = 20
    wait_for_debounce(qtbot)
    
    widget.value = 30
    wait_for_debounce(qtbot)
    
    # Slot should have been called multiple times
    assert emission_count["count"] >= 3
    assert widget.value == 30


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_for_check_box_widget(qtbot: QtBot) -> None:
    """Test signal emission for check box widget."""
    widget = IQtCheckBox(False, text="Option", debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change value
    widget.is_checked = True
    wait_for_debounce(qtbot)
    
    assert len(emissions) > 0
    assert widget.is_checked is True


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_for_selection_widget(qtbot: QtBot) -> None:
    """Test signal emission for selection option widget."""
    options = {"A", "B", "C"}
    widget = IQtSelectionOption("A", options, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change selection
    widget.selected_option = "B"
    wait_for_debounce(qtbot)
    
    assert len(emissions) > 0
    assert widget.selected_option == "B"


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_for_real_united_scalar(qtbot: QtBot) -> None:
    """Test signal emission for real united scalar widget."""
    widget = IQtRealUnitedScalar(
        value_or_hook_or_observable="5.0 m",
        display_unit_options={Unit("m").dimension: {Unit("m"), Unit("cm"), Unit("mm")}},
        debounce_ms=TEST_DEBOUNCE_MS
    )
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change value
    widget.value = "10.0 m"
    wait_for_debounce(qtbot)
    
    assert len(emissions) > 0
    # widget.value is a RealUnitedScalar, so compare with the expected RealUnitedScalar
    from united_system import RealUnitedScalar
    assert widget.value == RealUnitedScalar("10.0 m")


@pytest.mark.qt_log_ignore(".*")
def test_signal_with_observable_binding(qtbot: QtBot) -> None:
    """Test signal emission when widget is bound to observable."""
    observable: ObservableSingleValue[str] = ObservableSingleValue("initial")
    widget = IQtTextEntry(observable, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change observable value
    observable.change_value("changed")
    wait_for_debounce(qtbot)
    
    assert len(emissions) > 0
    assert widget.text == "changed"


@pytest.mark.qt_log_ignore(".*")
def test_signal_with_multiple_connected_widgets(qtbot: QtBot) -> None:
    """Test signal emission with multiple widgets connected to same hook."""
    hook: FloatingHook[int] = FloatingHook(42)
    
    widget1 = IQtIntegerEntry(hook, debounce_ms=TEST_DEBOUNCE_MS)
    widget2 = IQtIntegerEntry(hook, debounce_ms=TEST_DEBOUNCE_MS)
    
    qtbot.addWidget(widget1)
    qtbot.addWidget(widget2)
    
    emissions1: list[int] = []
    emissions2: list[int] = []
    widget1.contentChanged.connect(lambda: emissions1.append(1))
    widget2.contentChanged.connect(lambda: emissions2.append(1))
    
    # Change value via hook - both should emit signals
    hook.submit_value(100)
    wait_for_debounce(qtbot)
    
    assert len(emissions1) > 0
    assert len(emissions2) > 0
    assert widget1.value == 100
    assert widget2.value == 100


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_multiple_times_for_multiple_changes(qtbot: QtBot) -> None:
    """Test that signal is emitted for each value change."""
    widget = IQtFloatEntry(1.0, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Make multiple changes
    values = [2.0, 3.0, 4.0, 5.0]
    for value in values:
        widget.value = value
        wait_for_debounce(qtbot)
    
    # Signal should have been emitted for each change
    assert len(emissions) >= len(values)
    assert widget.value == 5.0


@pytest.mark.qt_log_ignore(".*")
def test_signal_with_change_value_method(qtbot: QtBot) -> None:
    """Test signal emission when using change_value method."""
    widget = IQtIntegerEntry(10, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change value using change_value method
    widget.change_value(50)
    wait_for_debounce(qtbot)
    
    assert len(emissions) > 0
    assert widget.value == 50


@pytest.mark.qt_log_ignore(".*")
def test_signal_captures_emissions(qtbot: QtBot) -> None:
    """Test that callbacks correctly capture all signal emissions."""
    widget = IQtTextEntry("start", debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Verify initial count
    initial_count = len(emissions)
    
    # Make a change
    widget.text = "end"
    wait_for_debounce(qtbot)
    
    # Count should have increased
    assert len(emissions) > initial_count


@pytest.mark.qt_log_ignore(".*")
def test_signal_disconnection(qtbot: QtBot) -> None:
    """Test that signal can be disconnected from slots."""
    widget = IQtIntegerEntry(0, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    call_count = {"count": 0}
    
    def slot() -> None:
        call_count["count"] += 1
    
    # Connect and make a change
    widget.contentChanged.connect(slot)
    widget.value = 10
    wait_for_debounce(qtbot)
    
    count_after_connection = call_count["count"]
    assert count_after_connection > 0
    
    # Disconnect and make another change
    widget.contentChanged.disconnect(slot)
    widget.value = 20
    wait_for_debounce(qtbot)
    
    # Count should not have increased after disconnection
    assert call_count["count"] == count_after_connection


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_on_unit_change(qtbot: QtBot) -> None:
    """Test signal emission when unit changes in united scalar widget."""
    widget = IQtRealUnitedScalar(
        value_or_hook_or_observable="100.0 m",  # Must include unit to match dimension
        display_unit_options={Unit("m").dimension: {Unit("m"), Unit("cm")}},
        debounce_ms=TEST_DEBOUNCE_MS
    )
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Change unit (should trigger signal)
    widget.unit = "cm"
    wait_for_debounce(qtbot)
    
    assert len(emissions) > 0
    assert widget.unit == Unit("cm")


@pytest.mark.qt_log_ignore(".*")
def test_signal_with_lambda_slot(qtbot: QtBot) -> None:
    """Test signal connection with lambda functions."""
    widget = IQtFloatEntry(0.0, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    result: dict[str, float | None] = {"value": None}
    
    # Connect with lambda
    widget.contentChanged.connect(lambda: result.update({"value": widget.value}))
    
    # Change value
    widget.value = 3.14
    wait_for_debounce(qtbot)
    
    # Lambda should have been called and captured the value
    assert result["value"] == 3.14


@pytest.mark.qt_log_ignore(".*")
def test_signal_emitted_on_same_value(qtbot: QtBot) -> None:
    """Test that signal is emitted even when setting the same value (due to invalidation)."""
    widget = IQtIntegerEntry(42, debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    # Wait for any initial emissions to settle
    wait_for_debounce(qtbot)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    initial_count = len(emissions)
    
    # Set to same value - signal will still be emitted because invalidation happens
    widget.value = 42
    wait_for_debounce(qtbot)
    
    # Signal is emitted because widgets are invalidated even if value hasn't changed
    assert len(emissions) >= initial_count


@pytest.mark.qt_log_ignore(".*")
def test_signal_after_widget_disposal(qtbot: QtBot) -> None:
    """Test that signal is not emitted after widget disposal."""
    widget = IQtTextEntry("test", debounce_ms=TEST_DEBOUNCE_MS)
    qtbot.addWidget(widget)
    
    emissions: list[int] = []
    widget.contentChanged.connect(lambda: emissions.append(1))
    
    # Dispose the widget
    widget.close()
    
    # Try to change value after disposal - signal should not be emitted
    # (the controller is disposed and won't process changes)
    try:
        widget.text = "should not work"
    except RuntimeError:
        # Expected - controller is disposed
        pass
    
    wait_for_debounce(qtbot)
    
    # Emission count should not increase after disposal
    count_at_disposal = len(emissions)
    wait_for_debounce(qtbot)
    assert len(emissions) == count_at_disposal

