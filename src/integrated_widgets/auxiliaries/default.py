



"""Global default configuration for integrated_widgets."""

from typing import Callable

# Global default debounce time in milliseconds
_DEFAULT_DEBOUNCE_MS: int = 50


def get_default_debounce_ms() -> int:
    """Get the current global default debounce time."""
    return _DEFAULT_DEBOUNCE_MS


def set_default_debounce_ms(value: int) -> None:
    """Set the global default debounce time."""
    global _DEFAULT_DEBOUNCE_MS
    _DEFAULT_DEBOUNCE_MS = value # type: ignore
 

# Create the callable that returns the current value
default_debounce_ms: Callable[[], int] = get_default_debounce_ms


class DefaultConfig:
    """Configuration object that allows setting DEFAULT_DEBOUNCE_MS.
    
    Usage:
        from integrated_widgets import default
        
        default.DEFAULT_DEBOUNCE_MS = 50
    """
    
    @property
    def DEFAULT_DEBOUNCE_MS(self) -> int:
        """Get the current default debounce time."""
        return get_default_debounce_ms()
    
    @DEFAULT_DEBOUNCE_MS.setter
    def DEFAULT_DEBOUNCE_MS(self, value: int) -> None:
        """Set the default debounce time."""
        set_default_debounce_ms(value)


# Create the default instance for easy access
default = DefaultConfig()