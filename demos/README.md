# IQtWidgets Demos

This folder contains demonstration applications showcasing the IQtWidgets framework.

## Running Demos

Make sure you have the package installed or add it to your Python path:

```bash
# From the project root
cd demos
python demo_check_box.py
```

## Available Demos

### Simple Entry Widgets

- **`demo_check_box.py`** - Boolean checkboxes with observable binding
  - Multiple checkboxes bound to observables
  - Display widgets showing current values
  - Programmatic toggle functionality

- **`demo_float_entry.py`** - Float input with validation
  - Temperature range validation (-50 to 150°C)
  - Percentage validation (0-100%)
  - Price validation (positive values)
  - Random value generation

- **`demo_integer_entry.py`** - Integer input with validation
  - Age validation (0-120)
  - Count validation (non-negative)
  - Score validation (0-100) with grade display
  - Increment/decrement buttons

- **`demo_text_entry.py`** - Text input with validation
  - Name (required, non-empty)
  - Email (must contain @)
  - Username (3-20 chars, no spaces)
  - Optional nickname field

### Selection Widgets

- **`demo_selection_option.py`** - Mandatory single selection
  - Color selection with uppercase formatting
  - Operating mode selection
  - Priority level with custom formatting
  - Programmatic value cycling

- **`demo_selection_optional_option.py`** - Optional single selection
  - Optional color preference
  - T-shirt size selection
  - Country selection with custom "None" text
  - Clear all selections button

- **`demo_radio_buttons.py`** - Radio button groups
  - Pizza size selection
  - Game difficulty levels
  - Transport mode with emojis
  - UI theme selection

- **`demo_single_list_selection.py`** - List-based single selection
  - Programming language selection
  - City selection with custom formatting
  - Optional deselection support
  - Dynamic option management

### Complex Widgets

- **`demo_range_slider.py`** - Two-handle range sliders
  - Simple relative range (0.0-1.0)
  - Temperature range with physical units
  - Price range slider
  - Minimum span size enforcement

- **`demo_unit_combo_box.py`** - Unit selection with dimensions
  - Length unit selection
  - Temperature unit selection
  - Mass unit selection (editable)
  - Dynamic unit addition

- **`demo_real_united_scalar.py`** - Full unit-aware numeric entry
  - Distance measurement with conversions
  - Temperature with automatic unit conversion
  - Mass with dynamic unit options
  - Programmatic value manipulation

## Features Demonstrated

All demos showcase:

✅ **Observable Binding** - Widgets automatically sync with observable values  
✅ **Validation** - Input validation with visual feedback  
✅ **Two-way Binding** - Changes propagate in both directions  
✅ **Custom Formatting** - Display values with custom formatters  
✅ **Type Safety** - Full type annotations throughout  
✅ **Clean API** - Simple, intuitive widget creation

## Tips

- Try editing values in the widgets - displays update automatically
- Invalid inputs are rejected and revert to last valid value
- Observable values can be changed programmatically via buttons
- Each demo is self-contained and can be run independently

## Architecture

These demos use the high-level **IQtWidgets** API:

```python
from integrated_widgets import IQtFloatEntry, IQtCheckBox, IQtDisplayValue

# Simple widget creation with observable binding
temperature = ObservableSingleValue(25.0)
widget = IQtFloatEntry(temperature, validator=lambda x: -50 <= x <= 150)
```

For advanced use cases, see the low-level controller API in `integrated_widgets.core`.

