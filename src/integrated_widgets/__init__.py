"""Integrated Widgets - Reactive PySide6/Qt Widget Framework

A comprehensive PySide6/Qt widget framework that integrates with `observables` and 
`united_system` to create reactive, unit-aware UI components with bidirectional data binding.

**⚠️ DEVELOPMENT STATUS**: This library is in active development and is NOT production-ready.
The API may change without notice. Use in production environments at your own risk.

## 🎯 Key Features

- **🔄 Reactive Data Binding**: Automatic bidirectional synchronization with observables
- **📏 Unit Awareness**: Built-in support for physical units and dimensions via `united_system`
- **🎨 Flexible Layouts**: Customizable layout strategies for widget composition
- **⚡ Debounced Input**: Smooth user experience with configurable debouncing
- **🛡️ Type Safety**: Full type hints and validation support
- **🧹 Clean Lifecycle**: Automatic resource management and cleanup
- **🔗 Hook System**: Flexible connection points for data binding

## 🚀 Quick Start

Import the IQT widgets you need:

    from integrated_widgets import (
        IQtCheckBox,
        IQtFloatEntry,
        IQtTextEntry,
        IQtSelectionOption,
        IQtRangeSlider,        # 🎚️ Featured: Dynamic range slider
        IQtRealUnitedScalar,   # 🔬 Featured: Unit-aware numeric entry
    )

## 🎮 Demo Applications

Explore the comprehensive demo suite:

    # Featured demos - try these first!
    python demos/demo_range_slider.py        # 🎚️ Dynamic range slider
    python demos/demo_real_united_scalar.py  # 🔬 Unit-aware numeric entry
    
    # Complete demo list
    python demos/demo_check_box.py
    python demos/demo_float_entry.py
    python demos/demo_selection_option.py
    # ... and many more!

## 🏗️ Architecture

Three-layer architecture for maximum flexibility:

1. **IQT Widgets** (High-level API) - Ready-to-use widgets with layout strategies
2. **Controllers** (Mid-level API) - Manage bidirectional data binding
3. **Controlled Widgets** (Low-level API) - Specialized Qt widgets with feedback prevention

## 📚 Documentation

- **Full Documentation**: See `docs/README.md` for comprehensive documentation
- **API Reference**: Complete API reference with examples
- **Demo Guide**: Step-by-step demo walkthrough
- **Architecture Guide**: Deep dive into the three-layer design

## 🔧 Advanced Usage

For advanced use cases, low-level controllers and widgets are available:

    from integrated_widgets.controllers import (
        CheckBoxController,
        FloatEntryController,
        RangeSliderController,
    )
    
    from integrated_widgets.controlled_widgets import (
        ControlledCheckBox,
        ControlledLineEdit,
        ControlledRangeSlider,
    )

## 🧪 Testing

Comprehensive test suite with enhanced visualization:

    python tests/run_tests.py  # Run all tests with progress visualization
    python tests/run_tests.py tests/controller_tests/  # Controller tests
    python tests/run_tests.py tests/iqt_widget_tests/  # Widget tests

## 📦 Dependencies

- **PySide6**: Qt6 Python bindings (>=6.7)
- **observables**: Reactive observable pattern implementation (>=4.0.2)
- **united-system**: Physical units and dimensions system (>=0.2.2)

## 🤝 Contributing

This library is in active development. Contributions are welcome!

See `docs/README.md` for detailed contribution guidelines and development setup.
"""

from ._version import __version__

# IQT Widgets - Primary API
from .iqt_widgets.iqt_check_box import IQtCheckBox
from .iqt_widgets.iqt_display_value import IQtDisplayValue
from .iqt_widgets.iqt_double_list_selection import IQtDoubleListSelection
from .iqt_widgets.iqt_float_entry import IQtFloatEntry
from .iqt_widgets.iqt_integer_entry import IQtIntegerEntry
from .iqt_widgets.iqt_optional_text_entry import IQtOptionalTextEntry
from .iqt_widgets.iqt_path_selector import IQtPathSelector
from .iqt_widgets.iqt_radio_buttons_select import IQtRadioButtonsSelect
from .iqt_widgets.iqt_range_slider import IQtRangeSlider
from .iqt_widgets.iqt_real_united_scalar_entry import IQtRealUnitedScalarEntry
from .iqt_widgets.iqt_listview_single_optional_select import IQtListviewSingleOptionalSelect
from .iqt_widgets.iqt_combobox_optional_select import IQtComboboxOptionalSelect
from .iqt_widgets.iqt_combobox_select import IQtComboboxSelect
from .iqt_widgets.iqt_text_entry import IQtTextEntry
from .iqt_widgets.iqt_unit_entry import IQtUnitEntry
from .auxiliaries.iqt_signal_hook import IQtSignalHook
from .iqt_widgets.core.layout_strategy_base import LayoutStrategyBase
from .iqt_widgets.core.layout_payload_base import LayoutPayloadBase

from .auxiliaries.default import get_default_debounce_ms
DEFAULT_DEBOUNCE_MS = get_default_debounce_ms()

# Configuration module
from .auxiliaries.default import default

# Other - TODO: Re-enable once signal hook is restored

__all__ = [
    "__version__",

    # Simple entry widgets
    "IQtCheckBox",
    "IQtFloatEntry",
    "IQtIntegerEntry",
    "IQtTextEntry",
    "IQtOptionalTextEntry",
    
    # Display widgets
    "IQtDisplayValue",
    
    # Selection widgets
    "IQtRadioButtonsSelect",
    "IQtComboboxOptionalSelect",
    "IQtComboboxSelect",
    "IQtListviewSingleOptionalSelect",
    "IQtDoubleListSelection",
    
    # File/path widgets
    "IQtPathSelector",
    
    # Complex widgets
    "IQtRangeSlider",
    "IQtRealUnitedScalarEntry",
    "IQtUnitEntry",
    
    # Constants
    "DEFAULT_DEBOUNCE_MS",

    # Auxiliaries
    "IQtSignalHook",
    "default",
    "DEFAULT_DEBOUNCE_MS",
    "LayoutStrategyBase",
    "LayoutPayloadBase",
]
