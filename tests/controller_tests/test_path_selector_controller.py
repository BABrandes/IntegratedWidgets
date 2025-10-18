"""Tests for PathSelectorController class."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot
from pathlib import Path
import tempfile
import os

from observables import ObservableSingleValue
from integrated_widgets.controllers.path_selector_controller import PathSelectorController
from tests.conftest import wait_for_debounce, TEST_DEBOUNCE_MS


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test content")
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        os.unlink(temp_path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        import shutil
        shutil.rmtree(temp_path)


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_initialization_with_direct_path(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController initializes correctly with direct Path value."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.path == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_initialization_with_none(qtbot: QtBot) -> None:
    """Test that PathSelectorController initializes correctly with None value."""
    controller = PathSelectorController(
        None,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.path is None


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_initialization_with_observable(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController initializes correctly with observable."""
    observable = ObservableSingleValue[Path | None](temp_file)
    controller = PathSelectorController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.path == temp_file
    assert observable.value == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_initialization_with_hook(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController initializes correctly with hook."""
    observable = ObservableSingleValue[Path | None](temp_file)
    hook = observable.hook
    controller = PathSelectorController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Check initial value
    assert controller.path == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_value_change(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that PathSelectorController handles value changes correctly."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    new_value = temp_dir
    controller.path = new_value
    wait_for_debounce(qtbot)
    
    assert controller.path == new_value


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_change_to_none(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController handles change to None correctly."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    controller.path = None
    wait_for_debounce(qtbot)
    
    assert controller.path is None


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_change_from_none(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController handles change from None correctly."""
    controller = PathSelectorController(
        None,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    controller.path = temp_file
    wait_for_debounce(qtbot)
    
    assert controller.path == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_change_path_method(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that change_path method works correctly."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    controller.change_path(temp_dir)
    wait_for_debounce(qtbot)
    
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_change_path_with_custom_debounce(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that change_path method respects custom debounce_ms parameter."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    custom_debounce = 50
    controller.change_path(temp_dir, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_file_mode(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController works in file mode."""
    controller = PathSelectorController(
        temp_file,
        mode="file",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.path == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_directory_mode(qtbot: QtBot, temp_dir: Path) -> None:
    """Test that PathSelectorController works in directory mode."""
    controller = PathSelectorController(
        temp_dir,
        mode="directory",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_dialog_title(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController uses custom dialog title."""
    dialog_title = "Custom File Selector"
    controller = PathSelectorController(
        temp_file,
        dialog_title=dialog_title,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.path == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_suggested_file_title(qtbot: QtBot, temp_dir: Path) -> None:
    """Test that PathSelectorController uses suggested file title."""
    controller = PathSelectorController(
        temp_dir,
        suggested_file_title_without_extension="test_file",
        suggested_file_extension="txt",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_allowed_extensions(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController uses allowed file extensions."""
    controller = PathSelectorController(
        temp_file,
        allowed_file_extensions="txt",
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.path == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_multiple_allowed_extensions(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController uses multiple allowed file extensions."""
    controller = PathSelectorController(
        temp_file,
        allowed_file_extensions={"txt", "py", "md"},
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    assert controller.path == temp_file


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_observable_sync(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that PathSelectorController syncs with observable changes."""
    observable = ObservableSingleValue[Path | None](temp_file)
    controller = PathSelectorController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value
    observable.value = temp_dir
    
    # Controller should reflect the change
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_observable_sync_to_none(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController syncs with observable changes to None."""
    observable = ObservableSingleValue[Path | None](temp_file)
    controller = PathSelectorController(
        observable,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change observable value to None
    observable.value = None
    
    # Controller should reflect the change
    assert controller.path is None


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_hook_sync(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that PathSelectorController syncs with hook changes."""
    observable = ObservableSingleValue[Path | None](temp_file)
    hook = observable.hook
    controller = PathSelectorController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value
    hook.submit_value(temp_dir)
    
    # Controller should reflect the change
    assert controller.path == temp_dir
    assert observable.value == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_hook_sync_to_none(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController syncs with hook changes to None."""
    observable = ObservableSingleValue[Path | None](temp_file)
    hook = observable.hook
    controller = PathSelectorController(
        hook,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Change hook value to None
    hook.submit_value(None)
    
    # Controller should reflect the change
    assert controller.path is None
    assert observable.value is None


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_widget_properties(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController exposes widget properties correctly."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Test widget properties
    assert hasattr(controller, 'widget_line_edit')
    assert hasattr(controller, 'widget_button')
    
    # Widget should be enabled by default
    assert controller.widget_line_edit.isEnabled()
    assert controller.widget_button.isEnabled()


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_debounce_functionality(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that debounce functionality works correctly."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Make rapid changes
    controller.path = temp_dir
    controller.path = temp_file
    controller.path = temp_dir
    
    # Wait for debounce
    wait_for_debounce(qtbot)
    
    # Should have the final value
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_default_parameters(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController works with default parameters."""
    controller = PathSelectorController(temp_file)
    
    # Should work with defaults
    assert controller.path == temp_file
    
    # Test value change
    controller.path = None
    qtbot.wait(200)  # Wait longer for default debounce
    
    assert controller.path is None


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_submit_method(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that PathSelectorController submit method works correctly."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    controller.submit(temp_dir)
    wait_for_debounce(qtbot)
    
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_submit_with_debounce(qtbot: QtBot, temp_file: Path, temp_dir: Path) -> None:
    """Test that PathSelectorController submit method respects debounce_ms parameter."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    custom_debounce = 50
    controller.submit(temp_dir, debounce_ms=custom_debounce)
    qtbot.wait(custom_debounce * 2)  # Wait for custom debounce
    
    assert controller.path == temp_dir


@pytest.mark.qt_log_ignore(".*")
def test_path_selector_controller_path_validation(qtbot: QtBot, temp_file: Path) -> None:
    """Test that PathSelectorController validates Path types correctly."""
    controller = PathSelectorController(
        temp_file,
        debounce_ms=TEST_DEBOUNCE_MS
    )
    
    # Valid Path values
    valid_values = [temp_file, None]
    for value in valid_values:
        controller.path = value
        wait_for_debounce(qtbot)
        assert controller.path == value
        if value is not None:
            assert isinstance(controller.path, Path)
