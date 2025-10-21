# Integrated Widgets Architecture

This document provides a detailed overview of the Integrated Widgets architecture, design principles, and implementation details.

## Table of Contents

- [Overview](#overview)
- [Three-Layer Architecture](#three-layer-architecture)
- [Data Flow](#data-flow)
- [Component Details](#component-details)
- [Design Principles](#design-principles)
- [Implementation Patterns](#implementation-patterns)
- [Thread Safety](#thread-safety)
- [Lifecycle Management](#lifecycle-management)
- [Performance Considerations](#performance-considerations)

## Overview

Integrated Widgets implements a three-layer architecture designed to provide maximum flexibility while maintaining simplicity for common use cases. The architecture separates concerns between data binding, widget management, and user interface components.

## Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│           IQT Widgets                   │  ← High-level API
│  (Ready-to-use, layout strategies)      │
├─────────────────────────────────────────┤
│           Controllers                   │  ← Mid-level API
│  (Bidirectional binding, lifecycle)     │
├─────────────────────────────────────────┤
│        Controlled Widgets              │  ← Low-level API
│  (Qt widgets, feedback prevention)      │
└─────────────────────────────────────────┘
```

### Layer 1: IQT Widgets (High-level API)

**Purpose**: Provide ready-to-use widgets with automatic data binding and customizable layouts.

**Key Features**:
- Simple API accepting values, hooks, or nexpys
- Automatic bidirectional synchronization
- Layout strategies for customizable composition
- Unit awareness for physical quantities
- Built-in validation and error handling

**Example**:
```python
from integrated_widgets import IQtCheckBox
from nexpy import XValue

enabled = XValue( True)
checkbox = IQtCheckBox(enabled, text="Enable Feature")
```

### Layer 2: Controllers (Mid-level API)

**Purpose**: Manage bidirectional data binding between nexpys and Qt widgets.

**Key Features**:
- Automatic synchronization between nexpys and widgets
- Signal handling and event processing
- Debounced input for smooth user experience
- Validation and error handling
- Lifecycle management and cleanup
- Feedback loop prevention

**Example**:
```python
from integrated_widgets.controllers import CheckBoxController
from nexpy import XValue

enabled = XValue( True)
controller = CheckBoxController(enabled, text="Enable Feature")
widget = controller.widget_check_box
```

### Layer 3: Controlled Widgets (Low-level API)

**Purpose**: Provide specialized Qt widgets with feedback loop prevention.

**Key Features**:
- Prevent accidental feedback loops
- Block direct programmatic modification
- Maintain controlled state
- Integrate with controller system

**Example**:
```python
from integrated_widgets.controlled_widgets import ControlledCheckBox

checkbox = ControlledCheckBox()
# Widget state is managed by controllers
```

## Data Flow

```
Observable ←→ Controller ←→ Qt Widget
     ↑           ↑             ↑
   Interface  Interface     Display
     ↓           ↓           Layer
    ┌─────────────┐
    │    Nexus    │
    │(Shared Data)│
    └─────────────┘
```

### Bidirectional Data Flow

1. **Observable ↔ Nexus**: Observables interface directly with the nexus
2. **Controller ↔ Nexus**: Controllers interface directly with the nexus  
3. **Widget ↔ Controller**: Widgets communicate with controllers, which interface with the nexus
4. **Feedback Prevention**: Internal update contexts prevent infinite loops
5. **Shared State**: Observables and controllers share the same nexus data through their interfaces

### Update Mechanisms

- **Nexus Updates**: Changes propagate through the shared nexus to all connected interfaces
- **Observable Interface**: Observables read/write nexus data through their interface
- **Controller Interface**: Controllers read/write nexus data through their interface
- **Widget Updates**: Widgets communicate with controllers, which handle nexus interactions
- **Feedback Prevention**: Internal update contexts prevent infinite loops
- **Debouncing**: Configurable debouncing for smooth user experience

## Component Details

### Controllers

Controllers are the heart of the architecture, managing the relationship between data and UI.

#### Base Controller Classes

- **BaseController**: Abstract base providing common functionality
- **BaseSingleHookController**: For controllers managing a single nexpy
- **BaseComplexHookController**: For controllers managing multiple nexpys

#### Controller Responsibilities

1. **Data Synchronization**: Keep nexpys and widgets in sync
2. **Signal Handling**: Process Qt signals and update nexpys
3. **Validation**: Validate input and handle errors
4. **Debouncing**: Provide smooth user experience
5. **Lifecycle**: Manage initialization and cleanup

#### Controller Lifecycle

```python
class MyController(BaseSingleHookController):
    def __init__(self, value: XValue, **kwargs):
        # 1. Initialize Qt widgets
        self._widget = QWidget()
        
        # 2. Call parent constructor
        super().__init__(hook_source=value, **kwargs)
        
        # 3. Connect signals
        self._widget.signal.connect(self._on_signal)
    
    def _invalidate_widgets_impl(self) -> None:
        # 4. Update widget from nexpy
        with self._internal_widget_update():
            self._widget.setValue(self.get_value())
    
    def _on_signal(self, new_value) -> None:
        # 5. Update nexpy from widget
        self.submit(new_value)
    
    def dispose(self) -> None:
        # 6. Cleanup
        super().dispose()
```

### Controlled Widgets

Controlled widgets are specialized Qt widgets that prevent accidental feedback loops.

#### Key Features

- **State Control**: Widget state is managed by controllers
- **Feedback Prevention**: Block direct programmatic modification
- **Signal Management**: Controlled signal emission
- **Integration**: Seamless integration with controller system

#### Example Implementation

```python
class ControlledCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_internal_update = False
    
    def setChecked(self, checked: bool) -> None:
        if self._is_internal_update:
            super().setChecked(checked)
        else:
            # Block direct modification
            pass
    
    def _internal_set_checked(self, checked: bool) -> None:
        self._is_internal_update = True
        super().setChecked(checked)
        self._is_internal_update = False
```

### IQT Widgets

IQT widgets provide the high-level API for most users.

#### Key Features

- **Simple API**: Easy-to-use interface
- **Automatic Binding**: Automatic data binding setup
- **Layout Strategies**: Customizable widget composition
- **Hook System**: Flexible connection points
- **Unit Awareness**: Built-in unit support

#### Widget Composition

```python
class IQtCheckBox:
    def __init__(self, value, text=None, layout_strategy=None, **kwargs):
        # 1. Create controller
        self._controller = CheckBoxController(value, text=text, **kwargs)
        
        # 2. Apply layout strategy
        if layout_strategy:
            self._widget = layout_strategy(self, self._controller.payload)
        else:
            self._widget = self._controller.widget_check_box
    
    def get_hook(self, name: str):
        return self._controller.get_hook(name)
    
    def dispose(self) -> None:
        self._controller.dispose()
```

## Design Principles

### 1. Separation of Concerns

Each layer has a specific responsibility:
- **IQT Widgets**: User interface and layout
- **Controllers**: Data binding and business logic
- **Controlled Widgets**: Qt widget implementation

### 2. Feedback Loop Prevention

The architecture prevents infinite loops through:
- Internal update contexts
- Controlled widget state management
- Signal/slot queued connections

### 3. Thread Safety

All components are thread-safe through:
- Qt's signal/slot mechanism
- Queued connections for cross-thread updates
- Proper synchronization

### 4. Resource Management

Automatic resource management through:
- Controller lifecycle management
- Automatic cleanup and disposal
- Proper observer removal

### 5. Extensibility

The architecture supports extension through:
- Custom layout strategies
- Custom controllers
- Custom controlled widgets

## Implementation Patterns

### Observer Pattern

Controllers implement the observer pattern to watch nexpys:

```python
class BaseController:
    def _on_nexpy_changed(self, nexpy, value):
        # Update widget when nexpy changes
        self._invalidate_widgets()
```

### Command Pattern

Widget interactions are handled through commands:

```python
class BaseController:
    def _on_widget_changed(self, new_value):
        # Submit new value to nexpy
        self.submit(new_value)
```

### Strategy Pattern

Layout strategies allow customizable widget composition:

```python
def custom_layout(parent, payload):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(payload.label)
    return widget

display = IQtDisplayValue(value, layout_strategy=custom_layout)
```

### Template Method Pattern

Base controllers define the template for widget management:

```python
class BaseController:
    def _invalidate_widgets(self):
        # Template method
        if not self._is_internal_update:
            self._invalidate_widgets_impl()
    
    def _invalidate_widgets_impl(self):
        # Override in subclasses
        raise NotImplementedError
```

## Thread Safety

### Qt Signal/Slot Mechanism

All cross-thread updates use Qt's signal/slot mechanism:

```python
# Observable changes from any thread
nexpy.submit_value("value", new_value)

# Automatically marshaled to GUI thread
def _on_nexpy_changed(self, nexpy, value):
    # This runs on the GUI thread
    self._invalidate_widgets()
```

### Queued Connections

Signal connections use queued connections for thread safety:

```python
# Cross-thread signal connection
signal.connect(slot, Qt.QueuedConnection)
```

### Synchronization

Proper synchronization prevents race conditions:

```python
class BaseController:
    def _invalidate_widgets(self):
        if not self._is_internal_update:
            # Thread-safe widget update
            QMetaObject.invokeMethod(
                self, "_invalidate_widgets_impl", 
                Qt.QueuedConnection
            )
```

## Lifecycle Management

### Initialization Phase

1. **Widget Creation**: Create Qt widgets
2. **Controller Setup**: Initialize controller with nexpys
3. **Signal Connection**: Connect widget signals to controller
4. **Observer Registration**: Register with nexpys
5. **Layout Application**: Apply layout strategy

### Active Phase

1. **Data Synchronization**: Keep nexpys and widgets in sync
2. **Event Handling**: Process user interactions
3. **Validation**: Validate input and handle errors
4. **Debouncing**: Provide smooth user experience

### Disposal Phase

1. **Signal Disconnection**: Disconnect all signals
2. **Observer Removal**: Remove from nexpys
3. **Resource Cleanup**: Clean up resources
4. **Widget Destruction**: Destroy Qt widgets

### Example Lifecycle

```python
class MyController(BaseSingleHookController):
    def __init__(self, value: XValue, **kwargs):
        # 1. Create widget
        self._widget = QWidget()
        
        # 2. Initialize controller
        super().__init__(hook_source=value, **kwargs)
        
        # 3. Connect signals
        self._widget.signal.connect(self._on_signal)
        
        # 4. Register observer
        self._nexpy.add_observer(self._on_nexpy_changed)
    
    def dispose(self) -> None:
        # 5. Disconnect signals
        self._widget.signal.disconnect(self._on_signal)
        
        # 6. Remove observer
        self._nexpy.remove_observer(self._on_nexpy_changed)
        
        # 7. Call parent dispose
        super().dispose()
```

## Performance Considerations

### Debouncing

Debouncing prevents excessive updates during rapid user input:

```python
class BaseController:
    def __init__(self, debounce_ms: int = 100, **kwargs):
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._commit_staged_value)
```

### Lazy Updates

Widgets are updated lazily to avoid unnecessary work:

```python
class BaseController:
    def _invalidate_widgets(self):
        if not self._is_internal_update:
            # Only update if not already updating
            self._invalidate_widgets_impl()
```

### Memory Management

Proper memory management prevents leaks:

```python
class BaseController:
    def dispose(self) -> None:
        # Clean up all resources
        self._nexpy = None
        self._widget = None
        super().dispose()
```

### Update Batching

Multiple updates are batched for efficiency:

```python
class BaseController:
    def _batch_updates(self, updates):
        # Batch multiple updates into single operation
        with self._internal_widget_update():
            for update in updates:
                update()
```

## Conclusion

The Integrated Widgets architecture provides a robust, flexible, and performant foundation for building reactive Qt applications. The three-layer design separates concerns while maintaining simplicity for common use cases and flexibility for advanced scenarios.

The architecture's key strengths are:

- **Simplicity**: Easy-to-use high-level API
- **Flexibility**: Customizable at every layer
- **Performance**: Optimized for smooth user experience
- **Thread Safety**: Robust cross-thread operation
- **Extensibility**: Easy to add new widgets and features

For more information, see the [API Reference](README.md) and [Demo Applications](../README.md#demo-applications).
