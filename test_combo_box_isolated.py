#!/usr/bin/env python3
"""Test ComboBoxController syntax in complete isolation."""

# Mock all the dependencies
from typing import Generic, TypeVar

T = TypeVar("T")

class MockBaseObservableController:
    def __init__(self, component_values, component_hooks, **kwargs):
        self._component_hooks = component_hooks
        self._component_values = component_values
        pass

class MockHook:
    def __init__(self, obj, getter, setter):
        self.obj = obj
        self.getter = getter
        self.setter = setter

class MockCarriesDistinctSingleValueHook(Generic[T]):
    def _get_single_value(self):
        pass
    def _get_single_value_hook(self):
        pass

class MockCarriesDistinctSetHook(Generic[T]):
    def _get_set(self):
        pass
    def _get_set_hook(self):
        pass

class MockSyncMode:
    UPDATE_SELF_FROM_OBSERVABLE = "UPDATE_SELF_FROM_OBSERVABLE"

class MockObservableSelectionOption:
    pass

class MockGuardedComboBox:
    def __init__(self, parent):
        self.parent = parent
        self.currentIndexChanged = MockSignal()
    
    def blockSignals(self, block):
        pass
    
    def clear(self):
        pass
    
    def addItem(self, text, userData=None):
        pass
    
    def setCurrentIndex(self, index):
        pass
    
    def count(self):
        return 0
    
    def currentIndex(self):
        return 0
    
    def itemData(self, index):
        return None

class MockSignal:
    def connect(self, slot):
        pass

class MockQWidget:
    pass

# Now define the ComboBoxController class
from typing import Generic, Optional, TypeVar, overload, Callable, Any, Mapping

T = TypeVar("T")

class ComboBoxController(
    MockBaseObservableController, 
    MockCarriesDistinctSingleValueHook, 
    MockCarriesDistinctSetHook, 
    Generic[T]
):
    """ComboBox controller that implements selection option hooks."""

    @overload
    def __init__(
        self,
        selected_value: Optional[T],
        *,
        options: set[T],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[MockQWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_value: Optional[T],
        *,
        options: MockCarriesDistinctSetHook[T],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[MockQWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_value: MockCarriesDistinctSingleValueHook[T],
        *,
        options: set[T],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[MockQWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_value: MockCarriesDistinctSingleValueHook[T],
        *,
        options: MockCarriesDistinctSetHook[T],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[MockQWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        selected_value,
        *,
        options,
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[MockQWidget] = None,
    ) -> None:

        self._formatter = formatter
        self._allow_none = allow_none
        
        # Handle different types of selected_value and options
        if hasattr(selected_value, '_get_single_value'):
            # It's a hook - set it and get initial value
            initial_selected_option = selected_value._get_single_value()
            selected_option_hook = selected_value
        else:
            # It's a direct value - create internal storage
            initial_selected_option = selected_value
            selected_option_hook = None
        if hasattr(options, '_get_set'):
            # It's a hook - set it and get initial value
            available_options = options._get_set()
            available_options_hook = options
        else:
            # It's a direct set - create internal storage
            available_options = options or set()
            available_options_hook = None
        
        if not allow_none and (initial_selected_option is None or available_options == set()):
            raise ValueError("Selected option is None but allow_none is False")
        
        if initial_selected_option is not None and initial_selected_option not in available_options:
            raise ValueError(f"Selected option {initial_selected_option} not in options {available_options}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys
            current_selected = x.get("selected_option", initial_selected_option)
            current_options = x.get("available_options", available_options)
            
            if not self._allow_none and current_selected is None:
                return False, "Selected option is None but allow_none is False"
            
            if current_options is not None and not isinstance(current_options, set):
                return False, "Options is not a set"
            
            if current_selected is not None and current_options is not None and current_selected not in current_options:
                return False, f"Selected option {current_selected} not in options {current_options}"
            
            if not self._allow_none and current_options == set():
                return False, "Options set is empty but allow_none is False"

            return True, "Verification method passed"

        super().__init__(
            {
                "selected_option": initial_selected_option,
                "available_options": available_options
            },
            {
                "selected_option": MockHook(self, self._get_single_value, self._set_single_value),
                "available_options": MockHook(self, self._get_set, self._set_set)
            },
            verification_method=verification_method,
        )
        
        # Store hooks for later binding
        self._selected_value_hook = selected_option_hook
        self._available_options_hook = available_options_hook
        
        if available_options_hook is not None:
            self.bind_options_to_observable(available_options_hook)
            
        if selected_option_hook is not None:
            self.bind_selected_option_to_observable(selected_option_hook)
        
        # Initialize widgets after setting up state
        self.initialize_widgets()
        self.update_widgets_from_component_values()

    def bind_options_to_observable(self, hook: MockCarriesDistinctSetHook[T], initial_sync_mode: MockSyncMode = MockSyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding for the options set with another observable."""
        if isinstance(hook, MockCarriesDistinctSetHook):
            hook = hook._get_set_hook()
        self._get_set_hook().establish_binding(hook, initial_sync_mode)

    def bind_selected_option_to_observable(self, hook: MockCarriesDistinctSingleValueHook[T], initial_sync_mode: MockSyncMode = MockSyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding for the selected option with another observable."""
        if isinstance(hook, MockCarriesDistinctSingleValueHook):
            hook = hook._get_single_value_hook()
        self._get_single_value_hook().establish_binding(hook, initial_sync_mode)

    def _get_single_value(self) -> Optional[T]:
        """Get the currently selected value."""
        return self._get_component_value("selected_option")

    def _get_single_value_hook(self) -> MockHook:
        """Get self as a hook for binding."""
        return self._component_hooks["selected_option"]

    def _set_single_value(self, value: Optional[T]) -> None:
        """Set the selected value."""
        if value is not None and value not in self._get_set():
            raise ValueError(f"Value {value} is not in available options")
        self._set_component_value("selected_option", value)

    def _get_set(self) -> set[T]:
        """Get the available options."""
        return self._get_component_value("available_options")

    def _get_set_hook(self) -> MockHook:
        """Get self as a set hook for binding."""
        return self._component_hooks["available_options"]

    def _set_set(self, options: set[T]) -> None:
        """Set the available options."""
        self._set_component_value("available_options", options)

    def _get_component_value(self, key: str):
        return self._component_values.get(key)
    
    def _set_component_value(self, key: str, value):
        self._component_values[key] = value

    def initialize_widgets(self) -> None:
        """Initialize the combo box widget."""
        self._combobox = MockGuardedComboBox(None)
        self._combobox.currentIndexChanged.connect(lambda _i: self._on_changed())

    def update_widgets_from_component_values(self) -> None:
        """Update the combo box from the component values."""
        pass

    def _on_changed(self) -> None:
        """Handle combo box selection change."""
        pass

# Test if we can create an instance
try:
    controller = ComboBoxController("A", options={"A", "B", "C"})
    print("✅ ComboBoxController created successfully!")
    print("✅ All syntax is valid!")
except Exception as e:
    print(f"❌ Failed to create ComboBoxController: {e}")
    import traceback
    traceback.print_exc()
