"""Tests for IQtSignalHook class."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject
from pytestqt.qtbot import QtBot

from integrated_widgets.util.iqt_signal_hook import IQtSignalHook
from observables import Hook


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_initialization_with_value(qtbot: QtBot) -> None:
    """Test that IQtSignalHook initializes correctly with an initial value."""
    app = QApplication.instance() or QApplication([])
    
    # Create a signal hook with initial value
    hook = IQtSignalHook[int](initial_value_or_hook=42)
    
    # Check initial value
    assert hook.value == 42


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_initialization_with_hook(qtbot: QtBot) -> None:
    """Test that IQtSignalHook initializes correctly with another hook."""
    app = QApplication.instance() or QApplication([])
    
    # Create a source hook
    source_hook = Hook[int](value=100)
    
    # Create a signal hook connected to the source
    signal_hook = IQtSignalHook[int](initial_value_or_hook=source_hook)
    
    # Check initial value synced from source
    assert signal_hook.value == 100


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_emits_on_value_change(qtbot: QtBot) -> None:
    """Test that IQtSignalHook emits Qt signal when value changes."""
    app = QApplication.instance() or QApplication([])
    
    # Create a signal hook
    hook = IQtSignalHook[int](initial_value_or_hook=42)
    
    # Track signal emissions
    emitted_values: list[int] = []
    
    def on_value_changed(value: int) -> None:
        emitted_values.append(value)
    
    hook.value_changed.connect(on_value_changed)
    
    # Change the value
    hook.submit_value(100)
    
    # Check that the Qt signal was emitted
    assert len(emitted_values) == 1
    assert emitted_values[0] == 100
    assert hook.value == 100


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_reacts_to_connected_hook(qtbot: QtBot) -> None:
    """Test that IQtSignalHook reacts when connected hook changes."""
    app = QApplication.instance() or QApplication([])
    
    # Create source hook
    source_hook = Hook[int](value=42)
    
    # Create signal hook connected to source
    signal_hook = IQtSignalHook[int](initial_value_or_hook=source_hook)
    
    # Track signal emissions
    emitted_values: list[int] = []
    signal_hook.value_changed.connect(lambda v: emitted_values.append(v))
    
    # Change the source hook value
    source_hook.submit_value(200)
    
    # Signal hook should react and emit
    assert signal_hook.value == 200
    assert len(emitted_values) == 1
    assert emitted_values[0] == 200


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_multiple_emissions(qtbot: QtBot) -> None:
    """Test that IQtSignalHook handles multiple value changes correctly."""
    app = QApplication.instance() or QApplication([])
    
    # Create a signal hook
    hook = IQtSignalHook[int](initial_value_or_hook=0)
    
    # Track all emitted values
    emitted_values: list[int] = []
    hook.value_changed.connect(lambda v: emitted_values.append(v))
    
    # Change value multiple times
    hook.submit_value(10)
    hook.submit_value(20)
    hook.submit_value(30)
    
    # Check all values were emitted
    assert hook.value == 30
    assert emitted_values == [10, 20, 30]


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_with_string_type(qtbot: QtBot) -> None:
    """Test IQtSignalHook with string type."""
    app = QApplication.instance() or QApplication([])
    
    # Create signal hook with string type
    hook = IQtSignalHook[str](initial_value_or_hook="initial")
    
    # Track emissions
    emitted_values: list[str] = []
    hook.value_changed.connect(lambda v: emitted_values.append(v))
    
    # Change value
    hook.submit_value("updated")
    
    assert hook.value == "updated"
    assert emitted_values == ["updated"]


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_with_logger(qtbot: QtBot) -> None:
    """Test IQtSignalHook initialization with a logger."""
    app = QApplication.instance() or QApplication([])
    
    import logging
    logger = logging.getLogger("test_logger")
    
    # Create a signal hook with logger
    hook = IQtSignalHook[int](
        initial_value_or_hook=42,
        logger=logger
    )
    
    # Should initialize without error
    assert hook.value == 42


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_dispose(qtbot: QtBot) -> None:
    """Test that IQtSignalHook disposes correctly."""
    app = QApplication.instance() or QApplication([])
    
    # Create a signal hook
    hook = IQtSignalHook[int](initial_value_or_hook=42)
    
    # Dispose should not raise
    hook.dispose()
    
    # Second dispose should also be safe (idempotent)
    hook.dispose()


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_connect_after_initialization(qtbot: QtBot) -> None:
    """Test connecting to another hook after initialization."""
    app = QApplication.instance() or QApplication([])
    
    # Create signal hook with initial value
    signal_hook = IQtSignalHook[int](initial_value_or_hook=42)
    
    # Track emissions
    emitted_values: list[int] = []
    signal_hook.value_changed.connect(lambda v: emitted_values.append(v))
    
    # Create and connect to another hook
    source_hook = Hook[int](value=100)
    signal_hook.connect_hook(source_hook, initial_sync_mode="use_target_value")
    
    # Should sync to source value
    assert signal_hook.value == 100
    assert 100 in emitted_values
    
    # Changes to source should propagate
    source_hook.submit_value(200)
    assert signal_hook.value == 200
    assert 200 in emitted_values


@pytest.mark.qt_log_ignore(".*")
def test_iqt_signal_hook_bidirectional_connection(qtbot: QtBot) -> None:
    """Test that changes propagate between connected hooks."""
    app = QApplication.instance() or QApplication([])
    
    # Create two hooks
    hook_a = Hook[int](value=10)
    signal_hook = IQtSignalHook[int](initial_value_or_hook=hook_a)
    
    # Track emissions
    emitted_values: list[int] = []
    signal_hook.value_changed.connect(lambda v: emitted_values.append(v))
    
    # Change hook_a
    hook_a.submit_value(50)
    assert signal_hook.value == 50
    assert 50 in emitted_values
    
    # Change signal_hook
    signal_hook.submit_value(75)
    assert hook_a.value == 75
    assert 75 in emitted_values
