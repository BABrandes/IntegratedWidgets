"""Auxiliary modules for integrated_widgets configuration."""

from .default import DefaultConfig, get_default_debounce_ms, set_default_debounce_ms, default_debounce_ms

# Create and export the default instance
default = DefaultConfig()

__all__ = ["default"]

