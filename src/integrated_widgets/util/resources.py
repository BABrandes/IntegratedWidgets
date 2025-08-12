"""Resource loading helpers compatible with wheels.

Uses importlib.resources to resolve files packaged inside the wheel, avoiding
assumptions about working directories.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Union

from PySide6.QtCore import QUrl


def resource_path(relative_path: Union[str, Path]) -> str:
    """Return an absolute filesystem path for a packaged resource.

    The path is resolved relative to `integrated_widgets.resources`.
    """

    rel = Path(relative_path)
    package = "integrated_widgets.resources"
    base = resources.files(package)
    return str(base.joinpath(rel))


def qml_url_for(qml_filename: Union[str, Path]) -> QUrl:
    """Return a QUrl for a packaged QML file.

    Example::
        engine.load(qml_url_for("qml/placeholder.qml"))
    """

    path = resource_path(Path("qml") / Path(qml_filename).name if Path(qml_filename).parent == Path() else qml_filename)
    return QUrl.fromLocalFile(path)


