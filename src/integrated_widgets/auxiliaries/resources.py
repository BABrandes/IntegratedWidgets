"""Resource loading helpers compatible with wheels.

Uses importlib.resources to resolve files packaged inside the wheel, avoiding
assumptions about working directories.
"""

from __future__ import annotations

from typing import Union, Optional, Any
from types import TracebackType

from importlib import resources
from pathlib import Path

from logging import Logger

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QComboBox, QListWidget
from PySide6.QtCore import Qt

from united_system import RealUnitedScalar


def resource_path(relative_path: Union[str, Path]) -> str:
    """Return an absolute filesystem path for a packaged resource.

    The path is resolved relative to `integrated_widgets.resources`.
    """

    rel = Path(relative_path)
    package = "integrated_widgets.resources"
    base = resources.files(package)
    return str(base.joinpath(rel)) # type: ignore


def qml_url_for(qml_filename: Union[str, Path]) -> QUrl:
    """Return a QUrl for a packaged QML file.

    Example::
        engine.load(qml_url_for("qml/placeholder.qml"))
    """

    path = resource_path(Path("qml") / Path(qml_filename).name if Path(qml_filename).parent == Path() else qml_filename)
    return QUrl.fromLocalFile(path)

def log_msg(subject: Any, action: str, logger: Optional[Logger], message: str) -> None:
    if logger is None:
        return
    logger.debug(f"{subject}: Action {action}: {message}")

def combo_box_find_data(combo_box: QComboBox, data: Any) -> int:
    # findData() doesn't work reliably with custom Python objects in PySide6
    # Do manual search using Python's == operator instead
    current_index = -1
    for i in range(combo_box.count()):
        if combo_box.itemData(i) == data:
            current_index = i
            break
    return current_index

def list_widget_find_data(list_widget: QListWidget, data: Any) -> int:
    # findItems() doesn't work reliably with custom Python objects in PySide6
    # Do manual search using Python's == operator instead
    current_index = -1
    for i in range(list_widget.count()):
        if list_widget.item(i).data(Qt.ItemDataRole.UserRole) == data:
            current_index = i
            break
    return current_index

# Default formatter for RealUnitedScalar value display
def format_real_united_scalar(value: RealUnitedScalar) -> str:
    return f"{value.value():.3f} {value.unit}"
DEFAULT_FLOAT_FORMAT_VALUE = format_real_united_scalar

class InternalUpdateHelper:
    """Shared helper to mark an owner with an internal update flag.

    Controllers can mix this in, or widgets can instantiate and use it to set
    the attribute ``_internal_widget_update`` on the owner during programmatic
    UI updates. Guarded widgets check this flag to allow model mutations.
    """

    def __init__(self, owner: object) -> None:
        self._owner = owner

    def context(self):
        class _Ctx:
            def __init__(self, owner: object) -> None:
                self._owner = owner
            def __enter__(self) -> None:
                setattr(self._owner, "_internal_widget_update", True)
            def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
                setattr(self._owner, "_internal_widget_update", False)
        return _Ctx(self._owner)