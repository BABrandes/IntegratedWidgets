from typing import Generic, Callable, TypeVar

T = TypeVar('T')

class FormatterMixin(Generic[T]):
    """Mixin for controllers that have a formatter function."""

    def __init__(
        self,
        formatter: Callable[[T], str] = lambda x: str(x),
        invalidate_widgets: Callable[[], None] = lambda: None):
        self._formatter = formatter
        self._invalidate_widgets = invalidate_widgets

    @property
    def formatter(self) -> Callable[[T], str]:
        """Get the formatter function."""
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function."""
        self._formatter = formatter
        self._invalidate_widgets()

    def change_formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function (alternative method)."""
        self._formatter = formatter
        self._invalidate_widgets()