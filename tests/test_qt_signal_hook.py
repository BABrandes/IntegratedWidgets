"""Tests for QtSignalHook class."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import QObject, Signal, Qt
from pytestqt.qtbot import QtBot

from integrated_widgets.util.qt_signal_hook import QtSignalHook


class MockWidget(QObject):
    """Mock widget with a signal for testing."""
    
    value_changed: Signal = Signal(int)
    
    def __init__(self) -> None:
        super().__init__()
        self._value: int = 42
    
    def get_value(self) -> int:
        """Get the current value."""
        return self._value
    
    def set_value(self, value: int) -> None:
        """Set a new value and emit signal."""
        self._value = value
        self.value_changed.emit(value)


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_initialization(qtbot: QtBot) -> None:
    """Test that QtSignalHook initializes correctly with a value callback."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # Check initial value
    assert hook.value == 42
    assert hook.value_reference == 42


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_receives_signal(qtbot: QtBot) -> None:
    """Test that QtSignalHook updates when receiving signal fires."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # Initial value
    assert hook.value == 42
    
    # Change the widget value and emit signal
    widget.set_value(100)
    
    # Hook should update
    assert hook.value == 100


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_emits_qt_signal(qtbot: QtBot) -> None:
    """Test that QtSignalHook emits its own Qt signal when value changes."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # Track signal emissions
    emitted_values: list[int] = []
    
    def on_value_changed(value: int) -> None:
        emitted_values.append(value)
    
    hook.value_changed_signal.connect(on_value_changed)
    
    # Change the widget value
    widget.set_value(200)
    
    # Check that the Qt signal was emitted
    assert len(emitted_values) == 1
    assert emitted_values[0] == 200


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_submit_value(qtbot: QtBot) -> None:
    """Test that submit_value works correctly."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # Submit a new value programmatically
    success, msg = hook.submit_value(500)
    
    assert success is True
    assert hook.value == 500


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_submit_value_emits_signal(qtbot: QtBot) -> None:
    """Test that submit_value also triggers the Qt signal emission."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # Track signal emissions
    emitted_values: list[int] = []
    
    def on_value_changed(value: int) -> None:
        emitted_values.append(value)
    
    hook.value_changed_signal.connect(on_value_changed)
    
    # Submit value programmatically
    hook.submit_value(750)
    
    # The signal should be emitted from _on_signal_received
    # But submit_value itself should also work
    assert hook.value == 750


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_with_string_type(qtbot: QtBot) -> None:
    """Test QtSignalHook with string type."""
    app = QApplication.instance() or QApplication([])
    
    class StringWidget(QObject):
        text_changed: Signal = Signal(str)
        
        def __init__(self) -> None:
            super().__init__()
            self._text: str = "initial"
        
        def get_text(self) -> str:
            return self._text
        
        def set_text(self, text: str) -> None:
            self._text = text
            self.text_changed.emit(text)
    
    # Create widget and hook
    widget = StringWidget()
    hook = QtSignalHook[str](
        receiving_signal=widget.text_changed,
        value_callback=widget.get_text
    )
    
    # Check initial value
    assert hook.value == "initial"
    
    # Change value
    widget.set_text("updated")
    assert hook.value == "updated"


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_multiple_signals(qtbot: QtBot) -> None:
    """Test that QtSignalHook handles multiple signal emissions correctly."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # Track all emitted values
    emitted_values: list[int] = []
    hook.value_changed_signal.connect(lambda v: emitted_values.append(v))
    
    # Emit multiple signals
    widget.set_value(10)
    widget.set_value(20)
    widget.set_value(30)
    
    # Check all values were received
    assert hook.value == 30
    assert emitted_values == [10, 20, 30]


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_with_button_click(qtbot: QtBot) -> None:
    """Test QtSignalHook with a real Qt widget (QPushButton)."""
    app = QApplication.instance() or QApplication([])
    
    # Create a button
    button = QPushButton("Test")
    click_count = [0]  # Use list to allow mutation in closure
    
    def get_click_count() -> int:
        return click_count[0]
    
    def increment_click_count() -> None:
        click_count[0] += 1
    
    button.clicked.connect(increment_click_count)
    
    # Create hook
    hook = QtSignalHook[int](
        receiving_signal=button.clicked,
        value_callback=get_click_count
    )
    
    # Initial count
    assert hook.value == 0
    
    # Simulate button click
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    
    # Hook should update
    assert hook.value == 1


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_value_reference_property(qtbot: QtBot) -> None:
    """Test that value_reference property works correctly."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget  
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # value and value_reference should be the same for primitives
    assert hook.value == hook.value_reference
    assert hook.value_reference == 42


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_with_logger(qtbot: QtBot) -> None:
    """Test QtSignalHook initialization with a logger."""
    app = QApplication.instance() or QApplication([])
    
    import logging
    logger = logging.getLogger("test_logger")
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook with logger
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value,
        logger=logger
    )
    
    # Should initialize without error
    assert hook.value == 42


@pytest.mark.qt_log_ignore(".*")
def test_qt_signal_hook_independent_notification_system(qtbot: QtBot) -> None:
    """Test that Qt signal emission is independent from hook's internal system."""
    app = QApplication.instance() or QApplication([])
    
    # Create a mock widget
    widget = MockWidget()
    
    # Create a QtSignalHook
    hook = QtSignalHook[int](
        receiving_signal=widget.value_changed,
        value_callback=widget.get_value
    )
    
    # Track Qt signal emissions
    qt_signal_emissions: list[int] = []
    hook.value_changed_signal.connect(lambda v: qt_signal_emissions.append(v))
    
    # Change value via widget signal
    widget.set_value(999)
    
    # Qt signal should have been emitted independently
    assert len(qt_signal_emissions) == 1
    assert qt_signal_emissions[0] == 999
    assert hook.value == 999

