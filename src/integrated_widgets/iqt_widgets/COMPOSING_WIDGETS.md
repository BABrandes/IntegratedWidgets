# Composing Custom Widgets with IQtLayoutedWidget

> **⚠️ Development Status**: This library is in active development and is NOT production-ready. The API may change without notice. This documentation reflects the current state but may be updated as the library evolves.

This guide shows how to create custom composite widgets by combining multiple IQt widgets together. You'll learn how to leverage the hook system for automatic synchronization and create flexible, reusable UI components.

## Table of Contents

1. [Quick Start: Why Compose Widgets?](#quick-start-why-compose-widgets)
2. [The Three Building Blocks](#the-three-building-blocks)
3. [Simple Example: Name and Age Form](#simple-example-name-and-age-form)
4. [The Hook System Advantage](#the-hook-system-advantage)
5. [Dynamic Layouts](#dynamic-layouts)
6. [Real-World Examples](#real-world-examples)
7. [Comparison to Traditional Qt](#comparison-to-traditional-qt)

---

## Quick Start: Why Compose Widgets?

**The Problem:** You want to create a reusable "person info form" with name, age, and email fields.

**Traditional Qt approach:**
```python
class PersonForm(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create widgets
        self.name = QLineEdit()
        self.age = QSpinBox()
        self.email = QLineEdit()
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name)
        layout.addWidget(QLabel("Age:"))
        layout.addWidget(self.age)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email)
        
    def get_data(self):
        """Manually extract data from widgets."""
        return {
            'name': self.name.text(),
            'age': self.age.value(),
            'email': self.email.text()
        }
```

**Problems:**
- ❌ Layout is hardcoded in `__init__`
- ❌ Can't switch between compact/expanded layouts
- ❌ Manual data extraction with `get_data()`
- ❌ No automatic synchronization with models
- ❌ Mixing widget creation with layout logic

**Our approach:**
```python
from dataclasses import dataclass
from integrated_widgets.iqt_widgets.iqt_layouted_widget import IQtLayoutedWidget
from integrated_widgets.iqt_widgets.layout_payload import BaseLayoutPayload
from integrated_widgets import IQtTextEntry, IQtIntegerEntry

@dataclass(frozen=True)
class PersonPayload(BaseLayoutPayload):
    name: QWidget
    age: QWidget
    email: QWidget

def create_person_form(name_hook, age_hook, email_hook):
    payload = PersonPayload(
        name=IQtTextEntry(name_hook),
        age=IQtIntegerEntry(age_hook),
        email=IQtTextEntry(email_hook)
    )
    
    def form_layout(parent, payload):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(payload.name)
        layout.addWidget(payload.age)
        layout.addWidget(payload.email)
        return widget
    
    return IQtLayoutedWidget(payload, form_layout)
```

**Benefits:**
- ✅ Can change layout dynamically
- ✅ Data automatically synchronized via hooks
- ✅ Widget creation separate from layout
- ✅ Type-safe with dataclass validation
- ✅ Widgets automatically validate input

---

## The Three Building Blocks

Every composite widget has three parts:

### 1. **Payload** - What widgets do you have?

A frozen dataclass that holds your IQt widgets.

```python
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget
from integrated_widgets.iqt_widgets.layout_payload import BaseLayoutPayload

@dataclass(frozen=True)
class MyPayload(BaseLayoutPayload):
    widget1: QWidget
    widget2: QWidget
    widget3: QWidget
```

**Think of it as:** Your "parts list" - what components does this composite widget contain?

**Frozen = immutable:** Once created, widgets can't be swapped out (prevents bugs).

### 2. **Strategy** - How should they be arranged?

A function that takes your payload and returns a QWidget with everything laid out.

```python
def my_layout_strategy(parent: QWidget, payload: MyPayload) -> QWidget:
    # Create a container
    container = QWidget()
    
    # Create and attach layout
    layout = QVBoxLayout(container)
    
    # Add payload's widgets
    layout.addWidget(payload.widget1)
    layout.addWidget(payload.widget2)
    layout.addWidget(payload.widget3)
    
    return container
```

**Think of it as:** Your "assembly instructions" - how should the parts be arranged?

**Can use QGroupBox, QFrame, etc.:**
```python
def grouped_strategy(parent, payload):
    group = QGroupBox("Settings")  # Styled container!
    layout = QVBoxLayout(group)
    layout.addWidget(payload.widget1)
    # ...
    return group
```

### 3. **IQtLayoutedWidget** - Put it together

Combines payload + strategy into a functional composite widget.

```python
from integrated_widgets.iqt_widgets.iqt_layouted_widget import IQtLayoutedWidget

composite = IQtLayoutedWidget(payload, my_layout_strategy)
```

**Think of it as:** The "assembly line" that builds your composite widget.

---

## Simple Example: Name and Age Form

Let's build a reusable person info widget step-by-step.

### Step 1: Create the IQt Widgets

```python
from integrated_widgets import IQtTextEntry, IQtIntegerEntry
from nexpy import Hook

# Create hooks for data binding
name_hook: Hook[str] = Hook("John Doe")
age_hook: Hook[int] = Hook(25)

# Create IQt widgets connected to hooks
name_widget = IQtTextEntry(name_hook)
age_widget = IQtIntegerEntry(age_hook)
```

**What this gives you:**
- ✅ Automatic validation (age must be int)
- ✅ Two-way data binding via hooks
- ✅ Change detection

### Step 2: Define the Payload

```python
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget
from integrated_widgets.iqt_widgets.layout_payload import BaseLayoutPayload

@dataclass(frozen=True)
class PersonPayload(BaseLayoutPayload):
    name_entry: QWidget
    age_entry: QWidget
```

**This declares:** "A person form has a name entry and an age entry."

### Step 3: Create the Payload Instance

```python
payload = PersonPayload(
    name_entry=name_widget,
    age_entry=age_widget
)
```

**At this point:** Payload validates that both fields are QWidgets. If not, you get a clear error immediately.

### Step 4: Define Layout Strategy

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

def person_form_layout(parent: QWidget, payload: PersonPayload) -> QWidget:
    # Create container
    container = QWidget()
    layout = QVBoxLayout(container)
    
    # Add labels and widgets
    layout.addWidget(QLabel("Name:"))
    layout.addWidget(payload.name_entry)
    layout.addWidget(QLabel("Age:"))
    layout.addWidget(payload.age_entry)
    
    return container
```

**This function says:** "Here's how to arrange a PersonPayload's widgets."

### Step 5: Create the Composite Widget

```python
from integrated_widgets.iqt_widgets.iqt_layouted_widget import IQtLayoutedWidget

person_form = IQtLayoutedWidget(payload, person_form_layout)
```

**Now you have:** A complete, reusable widget!

### Step 6: Use It Like Any QWidget

```python
# Add to your main window
main_layout = QVBoxLayout()
main_layout.addWidget(person_form)

# The hooks automatically sync data!
print(name_hook.value)  # → "John Doe"
name_hook.value = "Alice"  # Widget updates automatically!
```

---

## The Hook System Advantage

This is where the magic happens! The hook system enables automatic synchronization between widgets.

### Example: Master-Detail Pattern

**Scenario:** You have a person selector and a detail form. When you select a person, the form should update.

```python
from nexpy import Hook
from integrated_widgets import IQtSelectionOption, IQtTextEntry, IQtIntegerEntry

# Data model
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

people = [
    Person("Alice", 30),
    Person("Bob", 25),
    Person("Charlie", 35)
]

# Hooks for the selected person
selected_person: Hook[Person] = Hook(people[0])
name_hook: Hook[str] = Hook("")
age_hook: Hook[int] = Hook(0)

# Connect: when person changes, update name and age hooks
def update_details(person: Person):
    name_hook.value = person.name
    age_hook.value = person.age

selected_person.on_change(update_details)
update_details(people[0])  # Initialize

# Create selector widget
selector = IQtSelectionOption(
    selected_option=selected_person,
    available_options=frozenset(people),
    formatter=lambda p: p.name
)

# Create detail form using IQtLayoutedWidget
@dataclass(frozen=True)
class DetailPayload(BaseLayoutPayload):
    name: QWidget
    age: QWidget

detail_payload = DetailPayload(
    name=IQtTextEntry(name_hook),
    age=IQtIntegerEntry(age_hook)
)

def detail_layout(parent, payload):
    group = QGroupBox("Person Details")
    layout = QVBoxLayout(group)
    layout.addWidget(QLabel("Name:"))
    layout.addWidget(payload.name)
    layout.addWidget(QLabel("Age:"))
    layout.addWidget(payload.age)
    return group

detail_form = IQtLayoutedWidget(detail_payload, detail_layout)

# Compose selector and details
@dataclass(frozen=True)
class MasterDetailPayload(BaseLayoutPayload):
    selector: QWidget
    details: QWidget

master_detail_payload = MasterDetailPayload(selector, detail_form)

def master_detail_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.selector)
    layout.addWidget(payload.details)
    return widget

app_widget = IQtLayoutedWidget(master_detail_payload, master_detail_layout)
```

**What happens automatically:**
1. User selects "Bob" in selector → `selected_person` hook changes
2. `update_details()` runs → updates `name_hook` and `age_hook`
3. Detail form widgets **automatically update** to show Bob's info!

**No manual synchronization code needed!** This is the power of the hook system.

---

## Dynamic Layouts

One unique feature: you can **switch layouts dynamically** without recreating widgets.

### Example: Compact vs Expanded View

```python
@dataclass(frozen=True)
class SettingsPayload(BaseLayoutPayload):
    server: QWidget
    port: QWidget
    timeout: QWidget

payload = SettingsPayload(
    server=IQtTextEntry("localhost"),
    port=IQtIntegerEntry(8080),
    timeout=IQtIntegerEntry(30)
)

# Compact layout: all in one row
def compact_layout(parent, payload):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(payload.server)
    layout.addWidget(payload.port)
    layout.addWidget(payload.timeout)
    return widget

# Expanded layout: one per row with labels
def expanded_layout(parent, payload):
    group = QGroupBox("Server Settings")
    layout = QVBoxLayout(group)
    
    layout.addWidget(QLabel("Server:"))
    layout.addWidget(payload.server)
    layout.addWidget(QLabel("Port:"))
    layout.addWidget(payload.port)
    layout.addWidget(QLabel("Timeout (seconds):"))
    layout.addWidget(payload.timeout)
    
    return group

# Create with compact layout
settings = IQtLayoutedWidget(payload, compact_layout)

# User clicks "expand" button → switch layout
settings.set_strategy(expanded_layout)  # Widgets preserved, just re-arranged!

# User clicks "compact" button → switch back
settings.set_strategy(compact_layout)
```

**Why this is powerful:**
- ✅ Same widgets, different layouts
- ✅ No data loss during switches
- ✅ Hook connections remain intact
- ✅ Responsive UI without code duplication

**Traditional Qt:** You'd need separate widget classes for compact vs expanded, or complex show/hide logic.

---

## Real-World Examples

### Example 1: Synchronized Slider and Entry

**Goal:** A slider and number entry that stay in sync.

```python
from nexpy import Hook
from integrated_widgets import IQtIntegerEntry, IQtRangeSlider

# Shared hook for the value
value_hook: Hook[int] = Hook(50)

# Create widgets both connected to same hook
slider = IQtRangeSlider(
    span_lower_relative_value=0.0,
    span_upper_relative_value=value_hook,  # Connected!
    range_lower_value=0.0,
    range_upper_value=100.0
)
entry = IQtIntegerEntry(value_hook)  # Also connected!

# Compose them
@dataclass(frozen=True)
class SliderEntryPayload(BaseLayoutPayload):
    slider: QWidget
    entry: QWidget

payload = SliderEntryPayload(slider, entry)

def slider_entry_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.slider)
    layout.addWidget(payload.entry)
    return widget

sync_widget = IQtLayoutedWidget(payload, slider_entry_layout)
```

**What happens automatically:**
- User drags slider → `value_hook` updates → entry shows new value
- User types in entry → `value_hook` updates → slider moves
- **No manual synchronization code!**

### Example 2: Settings Dialog with Enable/Disable Logic

**Goal:** A settings dialog where some options are only enabled when a checkbox is checked.

```python
from nexpy import Hook
from integrated_widgets import IQtCheckBox, IQtTextEntry, IQtIntegerEntry

# Hooks
use_proxy: Hook[bool] = Hook(False)
proxy_host: Hook[str] = Hook("")
proxy_port: Hook[int] = Hook(8080)

# Widgets
use_proxy_checkbox = IQtCheckBox(use_proxy, text="Use Proxy Server")
proxy_host_entry = IQtTextEntry(proxy_host)
proxy_port_entry = IQtIntegerEntry(proxy_port)

# Connect enabled state to checkbox
# When checkbox changes, enable/disable the proxy fields
def sync_enabled_state(enabled: bool):
    proxy_host_entry.controller.is_enabled = enabled
    proxy_port_entry.controller.is_enabled = enabled

use_proxy.on_change(sync_enabled_state)
sync_enabled_state(False)  # Initialize

# Compose into settings panel
@dataclass(frozen=True)
class ProxySettingsPayload(BaseLayoutPayload):
    enable_checkbox: QWidget
    host_entry: QWidget
    port_entry: QWidget

payload = ProxySettingsPayload(use_proxy_checkbox, proxy_host_entry, proxy_port_entry)

def proxy_settings_layout(parent, payload):
    group = QGroupBox("Proxy Settings")
    layout = QVBoxLayout(group)
    
    layout.addWidget(payload.enable_checkbox)
    
    # Indent the proxy settings
    proxy_fields = QWidget()
    proxy_layout = QHBoxLayout(proxy_fields)
    proxy_layout.addWidget(QLabel("Host:"))
    proxy_layout.addWidget(payload.host_entry)
    proxy_layout.addWidget(QLabel("Port:"))
    proxy_layout.addWidget(payload.port_entry)
    layout.addWidget(proxy_fields)
    
    return group

proxy_panel = IQtLayoutedWidget(payload, proxy_settings_layout)
```

**Result:** Check the box → proxy fields enable. Uncheck → they disable. **Automatically!**

### Example 3: Multi-Tab Settings Dialog

**Goal:** A settings dialog with multiple tabs, each tab is a composite widget.

```python
from PySide6.QtWidgets import QTabWidget

# Create individual setting panels as IQtLayoutedWidgets
connection_panel = create_connection_settings()  # IQtLayoutedWidget
appearance_panel = create_appearance_settings()  # IQtLayoutedWidget
advanced_panel = create_advanced_settings()      # IQtLayoutedWidget

# Compose them into tabs
@dataclass(frozen=True)
class SettingsDialogPayload(BaseLayoutPayload):
    connection_tab: QWidget
    appearance_tab: QWidget
    advanced_tab: QWidget

payload = SettingsDialogPayload(
    connection_panel,
    appearance_panel,
    advanced_panel
)

def tabbed_layout(parent, payload):
    tabs = QTabWidget()
    tabs.addTab(payload.connection_tab, "Connection")
    tabs.addTab(payload.appearance_tab, "Appearance")
    tabs.addTab(payload.advanced_tab, "Advanced")
    return tabs

settings_dialog = IQtLayoutedWidget(payload, tabbed_layout)
```

**Benefits:**
- ✅ Each panel is independently testable
- ✅ Each panel can have its own layout strategy
- ✅ Easy to add/remove tabs
- ✅ All hooked together - changes in one tab can affect others

---

## The Hook System Advantage

The hook system is what makes composition powerful. Here's why:

### Without Hooks (Traditional Qt)

```python
class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.name = QLineEdit()
        self.age = QSpinBox()
        
        # Manual synchronization
        self.name.textChanged.connect(self.on_name_changed)
        self.age.valueChanged.connect(self.on_age_changed)
    
    def on_name_changed(self, text):
        # Manually update model
        self.model.name = text
    
    def on_age_changed(self, value):
        # Manually update model
        self.model.age = value
    
    def update_from_model(self, model):
        # Manually update widgets
        self.name.setText(model.name)
        self.age.setValue(model.age)
```

**Problems:**
- ❌ Manual signal connections
- ❌ Manual two-way sync
- ❌ Boilerplate for every field
- ❌ Easy to forget to update one direction

### With Hooks (Our Way)

```python
# Hooks ARE your model
name_hook: Hook[str] = Hook("John Doe")
age_hook: Hook[int] = Hook(25)

# Widgets automatically sync
name_widget = IQtTextEntry(name_hook)
age_widget = IQtIntegerEntry(age_hook)

# That's it! No manual sync code needed.
# Change hook → widget updates
# Change widget → hook updates
```

**Benefits:**
- ✅ Zero boilerplate
- ✅ Automatic two-way sync
- ✅ Type-safe (int hook only accepts ints)
- ✅ Can't forget to sync

### Multi-Widget Synchronization

**Example:** Three widgets, all showing the same value in different ways.

```python
from nexpy import Hook
from integrated_widgets import IQtIntegerEntry, IQtRangeSlider, IQtDisplayValue

# One hook, three widgets
temperature: Hook[int] = Hook(20)

entry = IQtIntegerEntry(temperature)        # Edit as number
slider = IQtRangeSlider(...)                 # Edit as slider
display = IQtDisplayValue(                   # Display as text
    temperature,
    formatter=lambda t: f"{t}°C"
)

# Compose them
@dataclass(frozen=True)
class TempControlPayload(BaseLayoutPayload):
    entry: QWidget
    slider: QWidget
    display: QWidget

payload = TempControlPayload(entry, slider, display)

def temp_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.display)  # Read-only display at top
    layout.addWidget(payload.slider)   # Slider in middle
    layout.addWidget(payload.entry)    # Precise entry at bottom
    return widget

temp_control = IQtLayoutedWidget(payload, temp_layout)
```

**Result:** Change ANY of the three widgets → ALL three update instantly!

**Traditional Qt:** You'd write signal connections between all three, in both directions. That's 6 connections with manual sync logic.

---

## Dynamic Layouts

### When to Use Dynamic Layouts

**Good use cases:**
- Responsive UI (compact mobile vs spacious desktop)
- User preference (compact vs detailed view)
- Wizard steps (same widgets, different arrangements)
- Print preview (edit mode vs print layout)

### Example: Responsive Settings Panel

```python
@dataclass(frozen=True)
class SettingsPayload(BaseLayoutPayload):
    option1: QWidget
    option2: QWidget
    option3: QWidget
    option4: QWidget

# Create widgets once
payload = SettingsPayload(
    option1=IQtCheckBox(hook1, text="Option 1"),
    option2=IQtCheckBox(hook2, text="Option 2"),
    option3=IQtCheckBox(hook3, text="Option 3"),
    option4=IQtCheckBox(hook4, text="Option 4")
)

# Mobile layout: vertical stack
def mobile_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.option1)
    layout.addWidget(payload.option2)
    layout.addWidget(payload.option3)
    layout.addWidget(payload.option4)
    return widget

# Desktop layout: 2x2 grid
def desktop_layout(parent, payload):
    widget = QWidget()
    layout = QGridLayout(widget)
    layout.addWidget(payload.option1, 0, 0)
    layout.addWidget(payload.option2, 0, 1)
    layout.addWidget(payload.option3, 1, 0)
    layout.addWidget(payload.option4, 1, 1)
    return widget

# Create with mobile layout
settings = IQtLayoutedWidget(payload, mobile_layout)

# Window resized? Switch to desktop layout
def on_resize(width):
    if width > 600:
        settings.set_strategy(desktop_layout)
    else:
        settings.set_strategy(mobile_layout)
```

**Key point:** Widgets and their state (hook connections) survive layout changes!

---

## Real-World Examples

### Complete Example: Connection Settings Dialog

```python
"""
A complete connection settings dialog showing all patterns:
- Multiple widgets composed together
- Hooks for automatic synchronization
- Enable/disable logic
- Validation
- Grouped sections
"""

from dataclasses import dataclass
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel
from nexpy import Hook
from integrated_widgets import IQtTextEntry, IQtIntegerEntry, IQtCheckBox
from integrated_widgets.iqt_widgets.iqt_layouted_widget import IQtLayoutedWidget
from integrated_widgets.iqt_widgets.layout_payload import BaseLayoutPayload

# === Data Model (Hooks) ===
class ConnectionSettings:
    def __init__(self):
        self.host: Hook[str] = Hook("localhost")
        self.port: Hook[int] = Hook(8080)
        self.timeout: Hook[int] = Hook(30)
        self.use_ssl: Hook[bool] = Hook(False)
        self.verify_certificate: Hook[bool] = Hook(True)
        self.auto_reconnect: Hook[bool] = Hook(True)

settings = ConnectionSettings()

# === Enable/Disable Logic ===
def sync_ssl_options(use_ssl: bool):
    """When SSL is disabled, disable certificate verification."""
    verify_cert_widget.controller.is_enabled = use_ssl

settings.use_ssl.on_change(sync_ssl_options)

# === Create Widgets ===
host_widget = IQtTextEntry(settings.host)
port_widget = IQtIntegerEntry(
    settings.port,
    validator=lambda p: 1 <= p <= 65535  # Port range validation
)
timeout_widget = IQtIntegerEntry(
    settings.timeout,
    validator=lambda t: t > 0
)
use_ssl_widget = IQtCheckBox(settings.use_ssl, text="Use SSL/TLS")
verify_cert_widget = IQtCheckBox(settings.verify_certificate, text="Verify Certificate")
auto_reconnect_widget = IQtCheckBox(settings.auto_reconnect, text="Auto-reconnect")

# Initialize SSL enable state
sync_ssl_options(settings.use_ssl.value)

# === Compose: Basic Settings ===
@dataclass(frozen=True)
class BasicSettingsPayload(BaseLayoutPayload):
    host: QWidget
    port: QWidget
    timeout: QWidget

basic_payload = BasicSettingsPayload(host_widget, port_widget, timeout_widget)

def basic_settings_layout(parent, payload):
    group = QGroupBox("Server")
    layout = QVBoxLayout(group)
    
    # Host and port on same row
    row1 = QWidget()
    row1_layout = QHBoxLayout(row1)
    row1_layout.addWidget(QLabel("Host:"))
    row1_layout.addWidget(payload.host, 3)
    row1_layout.addWidget(QLabel("Port:"))
    row1_layout.addWidget(payload.port, 1)
    layout.addWidget(row1)
    
    # Timeout
    row2 = QWidget()
    row2_layout = QHBoxLayout(row2)
    row2_layout.addWidget(QLabel("Timeout (s):"))
    row2_layout.addWidget(payload.timeout)
    layout.addWidget(row2)
    
    return group

basic_settings = IQtLayoutedWidget(basic_payload, basic_settings_layout)

# === Compose: Security Settings ===
@dataclass(frozen=True)
class SecuritySettingsPayload(BaseLayoutPayload):
    use_ssl: QWidget
    verify_cert: QWidget

security_payload = SecuritySettingsPayload(use_ssl_widget, verify_cert_widget)

def security_settings_layout(parent, payload):
    group = QGroupBox("Security")
    layout = QVBoxLayout(group)
    layout.addWidget(payload.use_ssl)
    
    # Indent verify cert
    indent = QWidget()
    indent_layout = QHBoxLayout(indent)
    indent_layout.addSpacing(20)  # Indent
    indent_layout.addWidget(payload.verify_cert)
    layout.addWidget(indent)
    
    return group

security_settings = IQtLayoutedWidget(security_payload, security_settings_layout)

# === Compose Everything: Full Dialog ===
@dataclass(frozen=True)
class ConnectionDialogPayload(BaseLayoutPayload):
    basic: QWidget
    security: QWidget
    auto_reconnect: QWidget

dialog_payload = ConnectionDialogPayload(
    basic_settings,
    security_settings,
    auto_reconnect_widget
)

def dialog_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.basic)
    layout.addWidget(payload.security)
    layout.addWidget(payload.auto_reconnect)
    layout.addStretch()
    return widget

connection_dialog = IQtLayoutedWidget(dialog_payload, dialog_layout)

# === Usage ===
# Add to your window
main_window.setCentralWidget(connection_dialog)

# Access the settings anywhere in your code
print(f"Connecting to {settings.host.value}:{settings.port.value}")

# Settings automatically update when user changes widgets!
```

---

## Comparison to Traditional Qt

### Traditional Qt Approach

```python
class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create all widgets
        self.host_edit = QLineEdit("localhost")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(8080)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setValue(30)
        self.use_ssl_check = QCheckBox("Use SSL/TLS")
        self.verify_cert_check = QCheckBox("Verify Certificate")
        self.auto_reconnect_check = QCheckBox("Auto-reconnect")
        
        # Set up signals
        self.use_ssl_check.toggled.connect(self.on_ssl_toggled)
        self.host_edit.textChanged.connect(self.on_host_changed)
        self.port_spin.valueChanged.connect(self.on_port_changed)
        # ... many more connections
        
        # Build layout (hardcoded here)
        layout = QVBoxLayout(self)
        
        server_group = QGroupBox("Server")
        server_layout = QVBoxLayout(server_group)
        # ... layout code
        
        layout.addWidget(server_group)
        # ... more layout code
    
    def on_ssl_toggled(self, checked):
        self.verify_cert_check.setEnabled(checked)
    
    def on_host_changed(self, text):
        self.settings.host = text  # Manual sync
    
    def on_port_changed(self, value):
        self.settings.port = value  # Manual sync
    
    # ... many more slot methods
    
    def apply_settings(self, settings):
        """Manually update widgets from settings."""
        self.host_edit.setText(settings.host)
        self.port_spin.setValue(settings.port)
        # ... many more updates
    
    def get_settings(self):
        """Manually extract settings from widgets."""
        return {
            'host': self.host_edit.text(),
            'port': self.port_spin.value(),
            # ... many more extractions
        }
```

**Lines of code:** ~100+

**Manual work:**
- ❌ Connect every signal manually
- ❌ Write slot for every change
- ❌ Manually sync widget → model
- ❌ Manually sync model → widget
- ❌ Can't change layout dynamically
- ❌ Hard to test individual sections

### Our Approach

```python
# Create hooks (your model)
settings = ConnectionSettings()  # All hooks defined

# Create widgets connected to hooks
host_widget = IQtTextEntry(settings.host)
port_widget = IQtIntegerEntry(settings.port)
# ...

# Compose with payload + strategy
payload = ConnectionDialogPayload(...)
connection_dialog = IQtLayoutedWidget(payload, dialog_layout)

# Auto sync logic
settings.use_ssl.on_change(lambda enabled: 
    verify_cert_widget.controller.is_enabled = enabled
)
```

**Lines of code:** ~50

**What's automatic:**
- ✅ Widget → hook synchronization
- ✅ Hook → widget synchronization  
- ✅ Type validation
- ✅ Each section independently testable
- ✅ Can change layouts dynamically
- ✅ Composable and reusable

---

## Key Takeaways for Qt Users

### Mindset Shift

**Traditional Qt thinking:**
> "I create widgets, connect signals, build layout. If I need different layout, I create a different widget class."

**IQtLayoutedWidget thinking:**
> "I have data (hooks), I have widgets (connected to hooks), I have layout strategies (how to arrange). I can mix and match."

### When to Use What

**Use pre-built widgets (IQtCheckBox, IQtTextEntry, etc.):**
- ✅ Simple forms
- ✅ Quick prototypes  
- ✅ Standard layouts

**Use IQtLayoutedWidget:**
- ✅ Need dynamic layout switching
- ✅ Complex compositions with multiple sections
- ✅ Reusable component libraries
- ✅ Want hook system benefits across multiple widgets

**Use traditional QWidget subclasses:**
- ✅ Custom painting / rendering
- ✅ Event handling (mouse, keyboard)
- ✅ When you don't need hook synchronization

### Learning Curve

1. **Week 1:** Use pre-built IQt widgets → Easy, Qt-like
2. **Week 2:** Learn hooks → Powerful, "aha!" moment
3. **Week 3:** Compose with IQtLayoutedWidget → Advanced, very productive

---

## FAQ for Qt Users

**Q: Why frozen dataclass? Can't I just pass a list of widgets?**

A: Type safety! The dataclass ensures you pass the right widgets. Compare:
```python
# List - easy to mess up order
IQtLayoutedWidget([widget1, widget2, widget3], strategy)

# Dataclass - named fields, impossible to mess up
IQtLayoutedWidget(
    MyPayload(name=widget1, age=widget2, email=widget3),
    strategy
)
```

**Q: Why separate payload from strategy?**

A: Reusability! One payload type can have multiple strategies:
```python
compact_form = IQtLayoutedWidget(payload, compact_strategy)
expanded_form = IQtLayoutedWidget(payload, expanded_strategy)
mobile_form = IQtLayoutedWidget(payload, mobile_strategy)
# Same data, different layouts!
```

**Q: Can I just use it without understanding everything?**

A: **Yes!** Copy the examples, replace widget names. You don't need to understand the deep architecture to use it.

**Q: What if I need custom painting or events?**

A: Subclass QWidget the traditional way! IQtLayoutedWidget is for **composition**, not **custom rendering**.

---

## Quick Reference

### Minimal Complete Example

```python
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget, QVBoxLayout
from nexpy import Hook
from integrated_widgets import IQtTextEntry, IQtIntegerEntry
from integrated_widgets.iqt_widgets.iqt_layouted_widget import IQtLayoutedWidget
from integrated_widgets.iqt_widgets.layout_payload import BaseLayoutPayload

# 1. Create hooks (your data model)
name: Hook[str] = Hook("")
age: Hook[int] = Hook(0)

# 2. Create IQt widgets
name_widget = IQtTextEntry(name)
age_widget = IQtIntegerEntry(age)

# 3. Define payload
@dataclass(frozen=True)
class MyPayload(BaseLayoutPayload):
    name: QWidget
    age: QWidget

payload = MyPayload(name_widget, age_widget)

# 4. Define layout strategy
def my_layout(parent, payload):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(payload.name)
    layout.addWidget(payload.age)
    return widget

# 5. Create composite widget
my_widget = IQtLayoutedWidget(payload, my_layout)

# 6. Use it!
# Widgets automatically sync with hooks
# name.value = "Alice"  →  name_widget updates automatically
```

---

## Benefits Summary

| Feature | Traditional Qt | With IQtLayoutedWidget + Hooks |
|---------|---------------|-------------------------------|
| **Data binding** | Manual signals/slots | Automatic via hooks |
| **Type safety** | Runtime errors | Compile-time + runtime validation |
| **Multi-widget sync** | 6+ manual connections | 1 shared hook |
| **Layout changes** | Create new widget | `set_strategy()` |
| **Composition** | Nested classes | Payload + strategy |
| **Reusability** | Copy-paste classes | Reuse strategies |
| **Testing** | Mock signals/slots | Mock hooks (simpler) |

**The hook system is the game-changer.** Once Qt users understand hooks, composition becomes natural.

---

**For Qt Users:** Think of IQtLayoutedWidget as a "smart container" that knows how to preserve and rearrange its children while keeping them connected to your data model via hooks. It's like `QStackedWidget` but more flexible.

