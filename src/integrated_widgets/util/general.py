
"""General small helpers and defaults."""

# Default formatter for RealUnitedScalar value display
DEFAULT_FLOAT_FORMAT_VALUE = lambda value: f"{value.value():.3f} {value.unit}"