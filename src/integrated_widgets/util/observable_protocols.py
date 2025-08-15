"""Observable contracts and convenience imports.

Moved from `widgets/observable_protocols.py`.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Protocol, TypeVar, runtime_checkable
from enum import Enum

T = TypeVar("T")
E = TypeVar("E", bound=Enum)

@runtime_checkable
class ObservableLike(Protocol):
    """
    A protocol to mimic the Observable interface from the `observables` package.
    This is used to ensure that the widget can be used with any Observable-like object.
    """
    def add_listeners(self, *callbacks: Callable[[], Any]) -> None: ...
    def remove_listeners(self, callback: Callable[[], Any]) -> None: ...

@runtime_checkable
class ObservableSingleValueLike(ObservableLike, Protocol[T]):
    """
    A protocol to mimic the ObservableSingleValue interface from the `observables` package.
    This is used to ensure that the widget can be used with any ObservableSingleValue-like object.
    """
    @property
    def single_value(self) -> T: ...
    @single_value.setter
    def single_value(self, value: T) -> None: ...

@runtime_checkable
class ObservableSelectionOptionLike(ObservableLike, Protocol[T]):
    """
    A protocol to mimic the ObservableSelectionOption interface from the `observables` package.
    This is used to ensure that the widget can be used with any ObservableSelectionOption-like object.
    """
    @property
    def available_options(self) -> set[T]: ...
    @available_options.setter
    def available_options(self, value: set[T]) -> None: ...
    @property
    def selected_option(self) -> Optional[T]: ...
    @selected_option.setter
    def selected_option(self, value: Optional[T]) -> None: ...
    @property
    def is_none_selection_allowed(self) -> bool: ...
    @is_none_selection_allowed.setter
    def is_none_selection_allowed(self, value: bool) -> None: ...

@runtime_checkable
class ObservableEnumLike(ObservableLike, Protocol[E]):
    """Enum observable: provides current selection and available options."""
    @property
    def enum_value(self) -> E: ...
    @enum_value.setter
    def enum_value(self, value: E) -> None: ...
    @property
    def enum_options(self) -> set[E]: ...
    @enum_options.setter
    def enum_options(self, value: set[E]) -> None: ...

@runtime_checkable
class ObservableMultiSelectionOptionLike(ObservableLike, Protocol[T]):
    """
    A protocol to mimic the ObservableMultiSelectionOption interface from the `observables` package.
    This is used to ensure that the widget can be used with any ObservableMultiSelectionOption-like object.
    """
    @property
    def available_options(self) -> set[T]: ...
    @available_options.setter
    def available_options(self, value: set[T]) -> None: ...
    @property
    def selected_options(self) -> set[T]: ...
    @selected_options.setter
    def selected_options(self, value: set[T]) -> None: ...