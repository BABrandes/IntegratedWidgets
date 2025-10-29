"""Controllers for Integrated Widgets.

This module contains all controller classes that manage bidirectional data binding
between observables and Qt widgets.

## Core Base Classes

- **BaseController**: Abstract base for all controllers
- **BaseCompositeController**: For controllers managing multiple related hooks
- **BaseSingletonController**: For controllers managing a single hook

## Singleton Controllers

Controllers that manage a single observable value:

- **CheckBoxController**: Boolean checkbox with label support
- **DisplayValueController**: Read-only value display with formatting
- **FloatEntryController**: Floating-point number entry with validation
- **IntegerEntryController**: Integer number entry with validation
- **OptionalTextEntryController**: Optional text input with clear button
- **PathSelectorController**: File/directory path selection
- **TextEntryController**: Single-line text input with validation

## Composite Controllers

Controllers that manage multiple related observable values:

- **DoubleSetSelectController**: Multiple selection from two sets
- **RangeSliderController**: Two-handle range slider with value displays
- **RealUnitedScalarController**: Unit-aware numeric entry with conversion
- **SingleSetOptionalSelectController**: Optional dropdown selection from options
- **SingleSetSelectController**: Exclusive selection from multiple options
- **UnitOptionalSelectController**: Optional unit selection with dimension validation
- **UnitSelectController**: Unit selection with dimension validation (no None allowed)
"""

# Core base classes
from .core.base_controller import BaseController as ControllerBase
from .core.base_composite_controller import BaseCompositeController as CompositeControllerBase
from .core.base_singleton_controller import BaseSingletonController as SingletonControllerBase

# Singleton controllers
from .singleton.check_box_controller import CheckBoxController
from .singleton.display_value_controller import DisplayValueController
from .singleton.float_entry_controller import FloatEntryController
from .singleton.integer_entry_controller import IntegerEntryController
from .singleton.optional_text_entry_controller import OptionalTextEntryController
from .singleton.path_selector_controller import PathSelectorController
from .singleton.text_entry_controller import TextEntryController

# Composite controllers
from .composite.double_set_select_controller import DoubleSetSelectController
from .composite.range_slider_controller import RangeSliderController
from .composite.real_united_scalar_controller import RealUnitedScalarController
from .composite.single_set_optional_select_controller import SingleSetOptionalSelectController
from .composite.single_set_select_controller import SingleSetSelectController
from .composite.unit_optional_select_controller import UnitOptionalSelectController
from .composite.unit_select_controller import UnitSelectController

__all__ = [
    # Core base classes
    "ControllerBase",
    "CompositeControllerBase",
    "SingletonControllerBase",
    
    # Singleton controllers
    "CheckBoxController",
    "DisplayValueController",
    "FloatEntryController",
    "IntegerEntryController",
    "OptionalTextEntryController",
    "PathSelectorController",
    "TextEntryController",
    
    # Composite controllers
    "DoubleSetSelectController",
    "RangeSliderController",
    "RealUnitedScalarController",
    "SingleSetOptionalSelectController",
    "SingleSetSelectController",
    "UnitOptionalSelectController",
    "UnitSelectController",
]

