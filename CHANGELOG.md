# Changelog

All notable changes to this project will be documented in this file.

## [0.1.102] - 2024-12-19

### Added
- **Centralized Debouncing System**: Unified debouncing across all controllers with configurable timing
- **Global Configuration**: `DEFAULT_DEBOUNCE_MS` constant for library-wide debounce configuration
- **Enhanced Error Handling**: Robust exception handling in disposal methods with graceful Qt object cleanup
- **Comprehensive API Documentation**: Complete API reference with type hints and examples
- **Demo Applications**: Comprehensive demo suite showcasing all controller types

### Changed
- **Simplified Signal Blocking**: Replaced complex object tracking with simple boolean `is_blocking_signals` property
- **Streamlined Controller Initialization**: Removed unnecessary `parent_of_widgets` parameters
- **Improved Package Structure**: Moved demos to project root for better organization
- **Enhanced Logging**: Added success/failure logging with detailed error messages
- **Optimized Performance**: Reduced memory overhead and faster signal blocking/unblocking

### Fixed
- **Qt Object Lifecycle**: Fixed QTimer cleanup errors during disposal
- **Dialog Parent Issues**: Fixed QMessageBox and QFileDialog parent widget issues
- **Import Consistency**: Standardized import statements across all demo files
- **Resource Management**: Improved cleanup and disposal of Qt objects

### Removed
- **Redundant Debouncing Logic**: Removed duplicate debouncing from RangeSliderController
- **Complex Blocking Mechanism**: Simplified signal blocking from object set to boolean flag
- **Unnecessary Parameters**: Removed `parent_of_widgets` parameter from all controllers

## [0.1.101] - Previous Version

### Features
- Basic controller architecture with BaseController, BaseSingleHookController, and BaseComplexHookController
- Widget controllers for common UI patterns (checkboxes, text entry, sliders, etc.)
- Controlled widgets that prevent direct modification outside controller context
- Observable integration with bidirectional data binding
- Unit-aware widgets with united_system integration

### Architecture
- Template method pattern for controller lifecycle management
- Signal/slot mechanism for thread-safe updates
- Internal update contexts to prevent feedback loops
- Resource management and cleanup

## Migration Guide

### From 0.1.101 to 0.1.102

#### Controller Initialization
**Before:**
```python
controller = CheckBoxController(
    value=observable,
    parent_of_widgets=parent_widget  # No longer needed
)
```

**After:**
```python
controller = CheckBoxController(
    value=observable,
    debounce_ms=100  # Optional, uses DEFAULT_DEBOUNCE_MS if not specified
)
```

#### Signal Blocking
**Before:**
```python
controller.set_block_signals(controller)
# ... do updates ...
controller.set_unblock_signals(controller)
```

**After:**
```python
controller.is_blocking_signals = True
# ... do updates ...
controller.is_blocking_signals = False
```

#### Debounce Configuration
**Before:**
```python
# No global configuration available
```

**After:**
```python
import integrated_widgets
integrated_widgets.DEFAULT_DEBOUNCE_MS = 250  # Global setting
```

#### Demo Location
**Before:**
```bash
python -m src.integrated_widgets.demos.demo_check_box_controller
```

**After:**
```bash
cd demos
python demo_check_box_controller.py
```

### Breaking Changes
- Removed `parent_of_widgets` parameter from all controller constructors
- Changed signal blocking methods to property-based approach
- Moved demo applications from package to project root

### Deprecations
- None in this release

## Future Plans

### Planned Features
- Context manager support for controllers
- Additional widget controllers (date/time, color picker, etc.)
- Enhanced unit system integration
- Performance monitoring and profiling tools
- Extended demo applications with real-world examples

### Architecture Improvements
- Async/await support for long-running operations
- Plugin system for custom controllers
- Enhanced error reporting and debugging tools
- Memory usage optimization
- Cross-platform testing and validation
