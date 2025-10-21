# Demo Guide - Integrated Widgets

This guide provides a comprehensive walkthrough of all demo applications included with Integrated Widgets. Each demo showcases specific widgets and features, helping you understand how to use them in your own applications.

## Table of Contents

- [Getting Started](#getting-started)
- [Featured Demos](#featured-demos)
- [Basic Widget Demos](#basic-widget-demos)
- [Selection Widget Demos](#selection-widget-demos)
- [Advanced Widget Demos](#advanced-widget-demos)
- [Display Widget Demos](#display-widget-demos)
- [Demo Tour Script](#demo-tour-script)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

1. **Install Dependencies**: Ensure you have all required dependencies installed
2. **Activate Environment**: Activate your virtual environment
3. **Navigate to Demos**: Change to the demos directory

```bash
# Install dependencies
pip install -e .[test]

# Activate virtual environment
source venv/bin/activate  # On Unix/macOS
# or
venv\Scripts\activate     # On Windows

# Navigate to demos
cd demos
```

### Running Demos

Each demo is a standalone Python script that can be run directly:

```bash
# Run a specific demo
python demo_check_box.py

# Run all demos in sequence
for demo in *.py; do
    echo "Running $demo..."
    python "$demo"
    echo "Press Enter to continue..."
    read
done
```

## Featured Demos

These demos showcase the most impressive and complex widgets. Start here to see the full capabilities of Integrated Widgets.

### 🎚️ Dynamic Range Slider (`demo_range_slider.py`)

**What it demonstrates**: Interactive range slider with real-time value updates and customizable bounds.

**Key Features**:
- Two-handle range selection
- Real-time value display
- Configurable range bounds
- Smooth dragging experience
- Observable synchronization

**How to run**:
```bash
python demo_range_slider.py
```

**What you'll see**:
- A range slider with two handles
- Real-time value displays showing current range
- Smooth dragging with immediate feedback
- Observable values updating in real-time

**Code highlights**:
```python
# Define range bounds
range_lower = XValue( 0.0)
range_upper = XValue( 100.0)

# Define selected span
span_lower = XValue( 20.0)
span_upper = XValue( 80.0)

# Create widget
slider = IQtRangeSlider(
    number_of_ticks=100,
    span_lower_relative_value=span_lower,
    span_upper_relative_value=span_upper,
    range_lower_value=range_lower,
    range_upper_value=range_upper
)
```

### 🔬 Real United Scalar Widget (`demo_real_united_scalar.py`)

**What it demonstrates**: Advanced unit-aware numeric entry with automatic unit conversion.

**Key Features**:
- Physical unit support (length, mass, time, etc.)
- Automatic unit conversion
- Dimension validation
- Real-time unit switching
- Scientific notation support

**How to run**:
```bash
python demo_real_united_scalar.py
```

**What you'll see**:
- Unit-aware numeric entry fields
- Automatic unit conversion
- Unit selection dropdowns
- Real-time value updates
- Dimension validation

**Code highlights**:
```python
# Create nexpy with a united value
distance = XValue( RealUnitedScalar(100.0, Unit("m")))

# Define available units
unit_options = {
    Dimension("L"): {Unit("m"), Unit("km"), Unit("cm"), Unit("mm")}
}
units_nexpy = XValue( unit_options)

# Create widget
widget = IQtRealUnitedScalar(
    value=distance,
    display_unit_options=units_nexpy
)
```

## Basic Widget Demos

These demos showcase the fundamental input widgets.

### Checkbox (`demo_check_box.py`)

**What it demonstrates**: Boolean checkbox with label support and nexpy binding.

**Key Features**:
- Boolean state management
- Label support
- Observable synchronization
- Real-time updates

**How to run**:
```bash
python demo_check_box.py
```

**What you'll see**:
- A checkbox with a label
- Real-time state updates
- Observable value changes

### Float Entry (`demo_float_entry.py`)

**What it demonstrates**: Floating-point number entry with validation.

**Key Features**:
- Numeric input validation
- Error handling
- Observable synchronization
- Custom validation rules

**How to run**:
```bash
python demo_float_entry.py
```

**What you'll see**:
- Numeric input field
- Validation feedback
- Error messages for invalid input

### Integer Entry (`demo_integer_entry.py`)

**What it demonstrates**: Integer number entry with validation.

**Key Features**:
- Integer input validation
- Range validation
- Error handling
- Observable synchronization

**How to run**:
```bash
python demo_integer_entry.py
```

**What you'll see**:
- Integer input field
- Validation feedback
- Error messages for invalid input

### Text Entry (`demo_text_entry.py`)

**What it demonstrates**: Single-line text input with validation and formatting.

**Key Features**:
- Text input validation
- Whitespace handling
- Custom validation rules
- Observable synchronization

**How to run**:
```bash
python demo_text_entry.py
```

**What you'll see**:
- Text input field
- Validation feedback
- Whitespace handling options

## Selection Widget Demos

These demos showcase various selection mechanisms.

### Radio Buttons (`demo_radio_buttons.py`)

**What it demonstrates**: Exclusive selection from multiple options using radio buttons.

**Key Features**:
- Exclusive selection
- Multiple options
- Custom formatting
- Observable synchronization

**How to run**:
```bash
python demo_radio_buttons.py
```

**What you'll see**:
- Radio button group
- Exclusive selection behavior
- Real-time updates

### Selection Option (`demo_selection_option.py`)

**What it demonstrates**: Dropdown selection from a set of options.

**Key Features**:
- Dropdown selection
- Option management
- Custom formatting
- Observable synchronization

**How to run**:
```bash
python demo_selection_option.py
```

**What you'll see**:
- Dropdown menu
- Option selection
- Real-time updates

### Selection Optional Option (`demo_selection_optional_option.py`)

**What it demonstrates**: Dropdown selection with optional "None" selection.

**Key Features**:
- Optional selection
- "None" option support
- Custom none text
- Observable synchronization

**How to run**:
```bash
python demo_selection_optional_option.py
```

**What you'll see**:
- Dropdown with "None" option
- Optional selection behavior
- Real-time updates

### Single List Selection (`demo_single_list_selection.py`)

**What it demonstrates**: Single selection from a list with custom formatting.

**Key Features**:
- List-based selection
- Custom formatting
- Option management
- Observable synchronization

**How to run**:
```bash
python demo_single_list_selection.py
```

**What you'll see**:
- List widget
- Single selection behavior
- Custom formatting

### Dictionary Optional Selection (`demo_dict_optional_selection.py`)

**What it demonstrates**: Dictionary-based optional selection with dynamic updates.

**Key Features**:
- Dictionary-based selection
- Optional selection
- Dynamic dictionary updates
- Custom formatting

**How to run**:
```bash
python demo_dict_optional_selection.py
```

**What you'll see**:
- Dictionary-based selection
- Dynamic updates
- Optional selection behavior

## Advanced Widget Demos

These demos showcase complex widgets with advanced features.

### Unit Combo Box (`demo_unit_combo_box.py`)

**What it demonstrates**: Unit selection with dimension validation.

**Key Features**:
- Unit selection
- Dimension validation
- Auto-add functionality
- Observable synchronization

**How to run**:
```bash
python demo_unit_combo_box.py
```

**What you'll see**:
- Unit selection dropdown
- Dimension validation
- Auto-add behavior

## Display Widget Demos

These demos showcase read-only display widgets.

### Display Value (`demo_display_value.py`)

**What it demonstrates**: Read-only value display with custom formatting.

**Key Features**:
- Read-only display
- Custom formatting
- Unit support
- Observable synchronization

**How to run**:
```bash
python demo_display_value.py
```

**What you'll see**:
- Read-only value display
- Custom formatting
- Unit-aware display

## Demo Tour Script

For a guided tour of all demos, use this script:

```bash
#!/bin/bash
# demo_tour.sh - Guided tour of all Integrated Widgets demos

echo "🎬 Integrated Widgets Demo Tour"
echo "=============================="
echo ""

# Featured demos first
echo "🎯 Featured Demos (Try These First!)"
echo "====================================="
echo ""

echo "🎚️ Running Dynamic Range Slider Demo..."
python demo_range_slider.py
echo "Press Enter to continue..."
read

echo "🔬 Running Real United Scalar Demo..."
python demo_real_united_scalar.py
echo "Press Enter to continue..."
read

echo ""
echo "📋 Complete Demo List"
echo "===================="
echo ""

# Basic widgets
echo "📝 Basic Input Widgets"
echo "---------------------"
for demo in demo_check_box.py demo_float_entry.py demo_integer_entry.py demo_text_entry.py; do
    if [ -f "$demo" ]; then
        echo "Running $demo..."
        python "$demo"
        echo "Press Enter to continue..."
        read
    fi
done

# Selection widgets
echo "🎯 Selection Widgets"
echo "-------------------"
for demo in demo_radio_buttons.py demo_selection_option.py demo_selection_optional_option.py demo_single_list_selection.py demo_dict_optional_selection.py; do
    if [ -f "$demo" ]; then
        echo "Running $demo..."
        python "$demo"
        echo "Press Enter to continue..."
        read
    fi
done

# Advanced widgets
echo "🚀 Advanced Widgets"
echo "------------------"
for demo in demo_unit_combo_box.py; do
    if [ -f "$demo" ]; then
        echo "Running $demo..."
        python "$demo"
        echo "Press Enter to continue..."
        read
    fi
done

# Display widgets
echo "📊 Display Widgets"
echo "-----------------"
for demo in demo_display_value.py; do
    if [ -f "$demo" ]; then
        echo "Running $demo..."
        python "$demo"
        echo "Press Enter to continue..."
        read
    fi
done

echo ""
echo "🎉 Demo Tour Complete!"
echo "====================="
echo ""
echo "You've seen all the Integrated Widgets demos!"
echo "Check out the documentation for more details:"
echo "- README.md - Main documentation"
echo "- docs/README.md - Comprehensive guide"
echo "- docs/ARCHITECTURE.md - Architecture details"
```

## Troubleshooting

### Common Issues

#### Demo won't start
- **Check dependencies**: Ensure all required packages are installed
- **Check Python version**: Requires Python 3.12+
- **Check virtual environment**: Ensure you're in the correct environment

#### Widgets not updating
- **Check nexpys**: Ensure nexpys are properly initialized
- **Check connections**: Verify widget-nexpy connections
- **Check threading**: Ensure updates happen on the GUI thread

#### Import errors
- **Check installation**: Ensure Integrated Widgets is properly installed
- **Check Python path**: Ensure the package is on Python path
- **Check dependencies**: Ensure all dependencies are installed

### Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in the console
2. **Check the documentation**: See `docs/README.md` for detailed information
3. **Check the tests**: Run `python tests/run_tests.py` to verify installation
4. **Check the examples**: Look at the demo code for usage patterns

### Performance Tips

- **Use debouncing**: Configure appropriate debounce timing
- **Limit updates**: Avoid excessive nexpy updates
- **Use appropriate widgets**: Choose the right widget for your use case
- **Clean up resources**: Ensure proper disposal of widgets

## Next Steps

After exploring the demos:

1. **Read the documentation**: Check `docs/README.md` for comprehensive information
2. **Study the architecture**: See `docs/ARCHITECTURE.md` for design details
3. **Run the tests**: Use `python tests/run_tests.py` to verify everything works
4. **Build your own**: Start creating your own applications with Integrated Widgets

## Conclusion

The Integrated Widgets demo suite provides a comprehensive showcase of all available widgets and features. Each demo demonstrates specific capabilities and provides working examples you can use as a starting point for your own applications.

The featured demos (Dynamic Range Slider and Real United Scalar) showcase the most advanced capabilities, while the basic demos provide a solid foundation for understanding the core concepts.

Start with the featured demos to see the full potential, then explore the basic demos to understand the fundamentals, and finally use the advanced demos to see complex use cases in action.
