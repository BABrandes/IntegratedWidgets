"""Observable contracts and convenience imports.

Moved from `widgets/observable_protocols.py`.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Optional, Protocol, TypeVar, runtime_checkable
from enum import Enum

T = TypeVar("T")
E = TypeVar("E", bound=Enum)

@runtime_checkable
class ObservableLike(Protocol):
    """
    A protocol to mimic the Observable interface from the `observables` package.
    This is used to ensure that the widget can be used with any Observable-like object.
    """
    def add_listeners(self, callback: Callable[[], Any]) -> Any: ...
    def remove_listeners(self, callback: Callable[[], Any]) -> Any: ...

@runtime_checkable
class ObservableSingleValueLike(ObservableLike, Protocol[T]):
    """
    A protocol to mimic the ObservableSingleValue interface from the `observables` package.
    This is used to ensure that the widget can be used with any ObservableSingleValue-like object.
    """
    @property
    def value(self) -> T: ...
    def set_value(self, new_value: T) -> None: ...
    def add_listeners(self, callback: Callable[[], Any]) -> Any: ...
    def remove_listeners(self, callback: Callable[[], Any]) -> Any: ...


@runtime_checkable
class ObservableSelectionOptionLike(ObservableLike, Protocol[T]):
    """
    A protocol to mimic the ObservableSelectionOption interface from the `observables` package.
    This is used to ensure that the widget can be used with any ObservableSelectionOption-like object.
    """
    @property
    def options(self) -> set[T]: ...
    @property
    def selected_option(self) -> Optional[T]: ...
    @selected_option.setter
    def selected_option(self, value: Optional[T]) -> None: ...
    @property
    def is_none_selection_allowed(self) -> bool: ...

@runtime_checkable
class ObservableEnumLike(ObservableLike, Protocol[E]):
    """Enum observable: provides current selection and available options."""
    @property
    def enum_value(self) -> E: ...
    def set_enum_value(self, new_value: E) -> None: ...
    @property
    def enum_options(self) -> set[E]: ...

@runtime_checkable
class ObservableMultiSelectionOptionLike(ObservableLike, Protocol[T]):
    """
    A protocol to mimic the ObservableMultiSelectionOption interface from the `observables` package.
    This is used to ensure that the widget can be used with any ObservableMultiSelectionOption-like object.
    """
    ...
    @property
    def options(self) -> set[T]: ...
    @property
    def selected_options(self) -> set[T]: ...
    @selected_options.setter
    def selected_options(self, value: set[T]) -> None: ...

try:
    from observables import ObservableSingleValue as ObservableSingleValue  # type: ignore
except Exception:
    try:
        from observables.examples.demo import ObservableSingleValue as ObservableSingleValue  # type: ignore
    except Exception:
        class ObservableSingleValue(Generic[T]):  # type: ignore
            ...

try:
    from observables import ObservableSelectionOption as ObservableSelectionOption  # type: ignore
except Exception:
    try:
        from observables.examples.demo import ObservableSelectionOption as ObservableSelectionOption  # type: ignore
    except Exception:
        class ObservableSelectionOption(Generic[T]):  # type: ignore
            ...


