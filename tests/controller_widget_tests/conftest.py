"""Shared fixtures and utilities for controller widget tests."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

# Central debounce configuration for tests
TEST_DEBOUNCE_MS = 10


# Use pytest-qt's built-in qtbot fixture

@pytest.fixture(autouse=True)
def cleanup_qt_state():
    """Clean up Qt state between tests to prevent crashes."""
    yield
    # Process any pending events to clean up state
    app = QApplication.instance()
    if app is not None:
        app.processEvents()
        # Force garbage collection to clean up Qt objects
        import gc
        gc.collect()


def wait_for_debounce(qtbot: QtBot, timeout: int | None = None) -> None:
    """Wait for debounced operations to complete."""
    if timeout is None:
        timeout = TEST_DEBOUNCE_MS * 2  # Wait 2x the debounce time
    qtbot.wait(timeout)


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    import logging
    from logging import Logger
    logger: Logger = logging.getLogger("test_controller")
    logger.setLevel(logging.DEBUG)
    return logger


# Common test data
@pytest.fixture
def sample_string():
    """Sample string for testing."""
    return "test_string"


@pytest.fixture
def sample_float():
    """Sample float for testing."""
    return 3.14159


@pytest.fixture
def sample_int():
    """Sample integer for testing."""
    return 42


@pytest.fixture
def sample_bool():
    """Sample boolean for testing."""
    return True


@pytest.fixture
def sample_string_list():
    """Sample list of strings for testing."""
    return ["apple", "banana", "cherry", "date"]


@pytest.fixture
def sample_int_list():
    """Sample list of integers for testing."""
    return [1, 2, 3, 4, 5]


# Validator functions for testing
@pytest.fixture
def string_validator():
    """Validator that accepts non-empty strings."""
    from typing import Callable, Any
    validator: Callable[[Any], bool] = lambda x: isinstance(x, str) and len(x) > 0
    return validator


@pytest.fixture
def float_validator():
    """Validator that accepts positive floats."""
    from typing import Callable, Any
    validator: Callable[[Any], bool] = lambda x: isinstance(x, float) and x > 0
    return validator


@pytest.fixture
def int_validator():
    """Validator that accepts positive integers."""
    from typing import Callable, Any
    validator: Callable[[Any], bool] = lambda x: isinstance(x, int) and x > 0
    return validator


@pytest.fixture
def bool_validator():
    """Validator that accepts any boolean."""
    from typing import Callable, Any
    validator: Callable[[Any], bool] = lambda x: isinstance(x, bool)
    return validator
