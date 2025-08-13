#!/usr/bin/env python3
"""Utility to bump the project version.

This script increments the version number in both `pyproject.toml` and
`src/integrated_widgets/_version.py` to keep them in sync.

Behavior:
- By default, increments the PATCH version (x.y.z -> x.y.(z+1)).
- You can control the bump type using the IW_BUMP environment variable:
  - IW_BUMP=major | minor | patch

This script is intended to be used from a Git pre-commit hook so that every
commit advances the version consistently.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
VERSION_MODULE_PATH = REPO_ROOT / "src" / "integrated_widgets" / "_version.py"


_VERSION_RE = re.compile(r"^version\s*=\s*\"(?P<ver>[0-9]+\.[0-9]+\.[0-9]+)\"\s*$")
_PY_VERSION_LINE_RE = re.compile(
    r"^__version__\s*:\s*str\s*=\s*\"(?P<ver>[0-9]+\.[0-9]+\.[0-9]+)\"\s*$"
)


@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "SemVer":
        parts = value.strip().split(".")
        if len(parts) != 3:
            raise ValueError(f"Unsupported version format: {value!r}")
        return cls(*(int(p) for p in parts))

    def bump(self, kind: str) -> "SemVer":
        kind = kind.lower()
        if kind == "major":
            return SemVer(self.major + 1, 0, 0)
        if kind == "minor":
            return SemVer(self.major, self.minor + 1, 0)
        if kind == "patch":
            return SemVer(self.major, self.minor, self.patch + 1)
        raise ValueError(f"Unknown bump kind: {kind!r}")

    def __str__(self) -> str:  # noqa: D401
        """Return the version as x.y.z."""
        return f"{self.major}.{self.minor}.{self.patch}"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _extract_pyproject_version(pyproject_text: str) -> Tuple[SemVer, int]:
    """Return version and the index of the matching line in pyproject.

    Searches inside the [project] section for a `version = "x.y.z"` line.
    """
    in_project = False
    lines = pyproject_text.splitlines()
    match_index = -1
    version_str = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("[project]"):
            in_project = True
            continue
        if in_project and line.strip().startswith("[") and not line.strip().startswith("[project]"):
            # left the [project] block
            in_project = False
        if in_project:
            m = _VERSION_RE.match(line.strip())
            if m:
                match_index = idx
                version_str = m.group("ver")
                break
    if match_index == -1 or version_str is None:
        raise RuntimeError("Could not find version in [project] section of pyproject.toml")
    return SemVer.parse(version_str), match_index


def _replace_pyproject_version(pyproject_text: str, new_version: SemVer, index: int) -> str:
    lines = pyproject_text.splitlines()
    # Preserve original indentation and formatting of the version line
    original_line = lines[index]
    leading_ws = original_line[: len(original_line) - len(original_line.lstrip())]
    lines[index] = f'{leading_ws}version = "{new_version}"'
    return "\n".join(lines) + ("\n" if pyproject_text.endswith("\n") else "")


def _extract_module_version(version_text: str) -> Tuple[SemVer, int]:
    lines = version_text.splitlines()
    for idx, line in enumerate(lines):
        m = _PY_VERSION_LINE_RE.match(line.strip())
        if m:
            return SemVer.parse(m.group("ver")), idx
    raise RuntimeError("Could not find __version__ line in _version.py")


def _replace_module_version(version_text: str, new_version: SemVer, index: int) -> str:
    lines = version_text.splitlines()
    original_line = lines[index]
    leading_ws = original_line[: len(original_line) - len(original_line.lstrip())]
    lines[index] = f'{leading_ws}__version__: str = "{new_version}"'
    return "\n".join(lines) + ("\n" if version_text.endswith("\n") else "")


def main() -> int:
    bump_kind = os.environ.get("IW_BUMP", "patch").lower()

    pyproject_text = _read_text(PYPROJECT_PATH)
    current_py_ver, py_line_index = _extract_pyproject_version(pyproject_text)

    version_text = _read_text(VERSION_MODULE_PATH)
    current_mod_ver, mod_line_index = _extract_module_version(version_text)

    if str(current_py_ver) != str(current_mod_ver):
        print(
            "warning: version mismatch between pyproject.toml and _version.py:"
            f" {current_py_ver} != {current_mod_ver}",
            file=sys.stderr,
        )

    new_version = current_py_ver.bump(bump_kind)

    new_py_text = _replace_pyproject_version(pyproject_text, new_version, py_line_index)
    new_mod_text = _replace_module_version(version_text, new_version, mod_line_index)

    if new_py_text == pyproject_text and new_mod_text == version_text:
        print("No changes made.")
        return 0

    _write_text(PYPROJECT_PATH, new_py_text)
    _write_text(VERSION_MODULE_PATH, new_mod_text)

    print(f"Bumped version: {current_py_ver} -> {new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


