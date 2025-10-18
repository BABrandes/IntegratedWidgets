from __future__ import annotations

# Standard library imports
from typing import Optional, Callable, Mapping, final, TypeVar, Generic, Any, cast
from logging import Logger

# BAB imports
from observables.core import NexusManager, DEFAULT_NEXUS_MANAGER, ComplexObservableBase

# Local imports
from ..util.resources import log_msg
from .base_controller import BaseController

PHK = TypeVar("PHK", bound=str)
"""Primary Hook Keys - String literal type for user-modifiable hook identifiers
   Example: Literal["dict_value", "selected_key"] for DictSelectionController"""

SHK = TypeVar("SHK", bound=str)
"""Secondary Hook Keys - String literal type for computed/derived hook identifiers
   Example: Literal["selected_value", "keys", "values"] for read-only derived hooks"""

PHV = TypeVar("PHV")
"""Primary Hook Values - Union of value types for primary (user-modifiable) hooks
   Example: dict[str, str] | str for DictSelectionController"""

SHV = TypeVar("SHV")
"""Secondary Hook Values - Union of value types for secondary (computed) hooks
   Example: str | list[str] | list[str] for derived values"""

C = TypeVar('C', bound="BaseComplexHookController[Any, Any, Any, Any, Any]")
"""Controller Type - The concrete controller class for self-referential typing"""

class BaseComplexHookController(BaseController[PHK|SHK, PHV|SHV, C], ComplexObservableBase[PHK, SHK, PHV, SHV, C], Generic[PHK, SHK, PHV, SHV, C]):
    """
    Base class for controllers managing multiple related observable values with Qt widgets.
    
    Use this base class when your controller needs to manage multiple interdependent values
    with both user-modifiable primary hooks and computed secondary hooks. This is more
    powerful than BaseSingleHookController but requires more setup.
    
    **When to Use:**
    
    Use BaseComplexHookController when you need:
    - Multiple related values that change together (e.g., dict + selected key)
    - Derived/computed values based on primary values (e.g., selected value from key)
    - Complex validation involving multiple values
    - Atomic updates of multiple related fields
    
    **Type Parameters:**
    
    PHK : str (bound)
        Primary Hook Keys - Literal union of user-modifiable hook names.
        These hooks can be changed by users and submitted back to observables.
        
        Example: `Literal["dict_value", "selected_key"]`
        
    SHK : str (bound)
        Secondary Hook Keys - Literal union of computed/derived hook names.
        These hooks are automatically calculated from primary hooks and are read-only.
        
        Example: `Literal["selected_value", "available_keys"]`
        
    PHV : Any
        Primary Hook Values - Union of value types for all primary hooks.
        
        Example: `dict[str, str] | str` for dict_value (dict) and selected_key (str)
        
    SHV : Any
        Secondary Hook Values - Union of value types for all secondary hooks.
        
        Example: `str | list[str]` for selected_value (str) and available_keys (list)
        
    C : BaseComplexHookController
        Controller type - The concrete subclass for self-referential typing.
        Always set to your controller class name as a string.
    
    **Generic Type Declaration Example:**
    
    ```python
    from typing import Literal
    
    class DictSelectionController(
        BaseComplexHookController[
            Literal["dict_value", "selected_key"],  # PHK - Primary hooks
            Literal["selected_value", "keys"],       # SHK - Secondary hooks  
            dict[str, str] | str,                   # PHV - Primary values
            str | list[str],                        # SHV - Secondary values
            "DictSelectionController"               # C - Self-reference
        ]
    ):
        # Primary hooks (user can modify):
        #   - dict_value: dict[str, str] - The dictionary
        #   - selected_key: str - The selected key
        #
        # Secondary hooks (computed):
        #   - selected_value: str - The value at selected_key
        #   - keys: list[str] - List of all keys in dict
        ...
    ```
    
    **Primary vs Secondary Hooks:**
    
    - **Primary Hooks**: User-modifiable, submitted back to observables
      - Represent the core state
      - Can be connected to observables
      - Accept user input from widgets
      - Example: dict_value, selected_key, range_min, range_max
    
    - **Secondary Hooks**: Computed from primary hooks, read-only
      - Derived from primary values via callbacks
      - Cannot be directly set by users
      - Automatically update when primaries change
      - Example: selected_value (from dict[key]), available_options, is_valid
    
    **Required Method Implementations:**
    
    Subclasses MUST implement:
    
    1. **`_initialize_widgets_impl(self) -> None`**
       Create all Qt widgets and connect their signals.
       
    2. **`_invalidate_widgets_impl(self) -> None`**
       Update all widgets from current primary and secondary hook values.
    
    **Secondary Hook Callbacks:**
    
    Define secondary hooks using callback functions:
    
    ```python
    # In __init__:
    def compute_selected_value(primary_values: Mapping) -> str:
        '''Compute selected value from dict and key.'''
        dict_val = primary_values["dict_value"]
        key = primary_values["selected_key"]
        return dict_val.get(key, "")
    
    def compute_keys(primary_values: Mapping) -> list[str]:
        '''Extract all keys from the dictionary.'''
        dict_val = primary_values["dict_value"]
        return list(dict_val.keys())
    
    super().__init__(
        initial_component_values={
            "dict_value": {"a": "1", "b": "2"},
            "selected_key": "a"
        },
        secondary_hook_callbacks={
            "selected_value": compute_selected_value,
            "keys": compute_keys
        }
    )
    ```
    
    **Complete Example - Dictionary Selection Controller:**
    
    ```python
    from typing import Literal, Mapping
    from integrated_widgets.util.base_complex_hook_controller import BaseComplexHookController
    from PySide6.QtWidgets import QComboBox, QLineEdit
    
    class DictController(BaseComplexHookController[
        Literal["dict_value", "selected_key"],    # Primary hooks
        Literal["selected_value"],                # Secondary hooks
        dict[str, str] | str,                     # Primary types
        str,                                      # Secondary types
        "DictController"                          # Self-reference
    ]):
        def __init__(
            self,
            dict_value: dict[str, str],
            selected_key: str
        ):
            # Define how secondary hooks are computed
            def selected_value_callback(primaries: Mapping) -> str:
                d = primaries["dict_value"]
                k = primaries["selected_key"]
                return d.get(k, "")
            
            # Initialize complex controller
            super().__init__(
                initial_component_values={
                    "dict_value": dict_value,
                    "selected_key": selected_key
                },
                secondary_hook_callbacks={
                    "selected_value": selected_value_callback
                }
            )
        
        def _initialize_widgets_impl(self) -> None:
            # Create widgets
            self._combo = QComboBox()
            self._value_edit = QLineEdit()
            
            # Connect signals
            self._combo.currentTextChanged.connect(self._on_key_changed)
            self._value_edit.textChanged.connect(self._on_value_changed)
        
        def _invalidate_widgets_impl(self) -> None:
            # Update widgets from hooks
            dict_val = self.get_value_of_hook("dict_value")
            selected_key = self.get_value_of_hook("selected_key")
            selected_value = self.get_value_of_hook("selected_value")
            
            # Update combo box
            self._combo.clear()
            self._combo.addItems(list(dict_val.keys()))
            self._combo.setCurrentText(selected_key)
            
            # Update value display
            self._value_edit.setText(selected_value)
        
        def _on_key_changed(self, key: str) -> None:
            if not self._internal_widget_update:
                # User changed selection - update selected_key
                self.submit_primary_values({"selected_key": key})
        
        def _on_value_changed(self, value: str) -> None:
            if not self._internal_widget_update:
                # User edited value - update dict
                current_dict = dict(self.get_value_of_hook("dict_value"))
                current_key = self.get_value_of_hook("selected_key")
                current_dict[current_key] = value
                self.submit_primary_values({"dict_value": current_dict})
    ```
    
    **Advantages Over BaseSingleHookController:**
    
    - Multiple related values stay synchronized automatically
    - Secondary hooks computed on-demand (no manual calculation)
    - Atomic updates (multiple values change together)
    - Complex validation involving multiple fields
    - Type-safe access to all hooks
    
    **Architecture Summary:**
    
    Controllers inherit from this base class and implement ONLY 2 required methods:
    
    1. `_initialize_widgets_impl()` - Create widgets (REQUIRED - abstract)
    2. `_invalidate_widgets_impl()` - Update UI from data (REQUIRED - abstract)
    
    The base controller handles ALL other functionality automatically:
    - Change notifications and binding updates
    - Widget update scheduling and signal management
    - Lifecycle management and disposal
    - Hook synchronization and error handling
    - Secondary hook computation
    
    **How It Works:**
    
    1. Base controller automatically calls `invalidate_widgets()` when values change
    2. This triggers `_invalidate_widgets_impl()` to update the UI
    3. Widget changes trigger `submit_primary_values()` to update data
    4. Secondary hooks automatically recompute from new primary values
    5. All change notifications and binding updates handled automatically
    
    See Also
    --------
    BaseSingleHookController : Simpler base class for single-value controllers
    BaseController : Foundation class with Qt integration
    ComplexObservableBase : Observables framework base for complex hook management
    """

    def __init__(
        self,
        initial_component_values: dict[PHK, PHV],
        *,
        verification_method: Optional[Callable[[Mapping[PHK, PHV]], tuple[bool, str]]] = None,
        secondary_hook_callbacks: Mapping[SHK, Callable[[Mapping[PHK, PHV]], SHV]] = {},
        add_values_to_be_updated_callback: Optional[Callable[[ComplexObservableBase[PHK, SHK, PHV, SHV, C], Mapping[PHK, PHV], Mapping[PHK, PHV]], Mapping[PHK, PHV]]] = None,
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,

    ) -> None:
        """
        Initialize a complex-hook controller with multiple related values.
        
        This constructor sets up primary hooks (user-modifiable), secondary hooks
        (computed from primaries), and the infrastructure for synchronizing them
        with Qt widgets.
        
        **Parameters:**
        
        initial_component_values : dict[PHK, PHV]
            Dictionary of initial values for all primary hooks.
            Keys must match the PHK type parameter (the primary hook names).
            
            **Example:**
            ```python
            initial_component_values={
                "dict_value": {"a": "apple", "b": "banana"},
                "selected_key": "a"
            }
            ```
        
        verification_method : Callable[[Mapping[PHK, PHV]], tuple[bool, str]] | None, optional
            Optional validation function that checks if a set of primary values is valid.
            
            **Signature:** `(values: Mapping[PHK, PHV]) -> tuple[success: bool, message: str]`
            
            Unlike BaseSingleHookController, this validates ALL primary values together,
            enabling cross-field validation logic.
            
            **Example:**
            ```python
            def validate_range(values: Mapping) -> tuple[bool, str]:
                min_val = values["range_min"]
                max_val = values["range_max"]
                if min_val >= max_val:
                    return False, "Min must be less than max"
                return True, "Valid range"
            
            controller = RangeController(
                initial_component_values={"range_min": 0, "range_max": 100},
                verification_method=validate_range
            )
            ```
        
        secondary_hook_callbacks : Mapping[SHK, Callable[[Mapping[PHK, PHV]], SHV]], optional
            Dictionary mapping secondary hook names to computation functions.
            
            Each callback receives all current primary values and computes one
            secondary value. Secondary hooks automatically update when primaries change.
            
            **Callback Signature:** `(primary_values: Mapping[PHK, PHV]) -> SHV`
            
            **Example:**
            ```python
            def compute_selected_value(primaries: Mapping) -> str:
                '''Get the value at the selected key.'''
                return primaries["dict_value"].get(primaries["selected_key"], "")
            
            def compute_keys(primaries: Mapping) -> list[str]:
                '''Get all available keys.'''
                return list(primaries["dict_value"].keys())
            
            def compute_values(primaries: Mapping) -> list[str]:
                '''Get all available values.'''
                return list(primaries["dict_value"].values())
            
            secondary_hook_callbacks={
                "selected_value": compute_selected_value,
                "keys": compute_keys,
                "values": compute_values
            }
            ```
        
        add_values_to_be_updated_callback : Callable | None, optional
            Advanced callback for augmenting value updates with dependent values.
            
            This enables automatic cascade updates when changing one value requires
            updating other related values. Rarely needed for most controllers.
            
            **Signature:**
            ```python
            (
                controller: ComplexObservableBase,
                new_values: Mapping[PHK, PHV],
                old_values: Mapping[PHK, PHV]
            ) -> Mapping[PHK, PHV]
            ```
            
            Returns additional values to update alongside the requested changes.
            
            **Example:**
            ```python
            def ensure_key_exists(controller, new_vals, old_vals):
                '''If dict changes, ensure selected_key still exists.'''
                if "dict_value" in new_vals:
                    new_dict = new_vals["dict_value"]
                    current_key = old_vals.get("selected_key")
                    if current_key not in new_dict:
                        # Add updated selected_key to use first available key
                        return {"selected_key": next(iter(new_dict.keys()))}
                return {}
            
            controller = DictController(
                initial_component_values=...,
                add_values_to_be_updated_callback=ensure_key_exists
            )
            ```
        
        debounce_ms : int | None, optional
            Debounce time in milliseconds. Same as BaseSingleHookController.
            Default: 100ms
        
        logger : Logger | None, optional
            Optional logger for debugging controller operations.
        
        nexus_manager : NexusManager, optional
            Nexus manager for hook coordination.
            Default: DEFAULT_NEXUS_MANAGER
        
        **Initialization Flow:**
        
        1. BaseController.__init__ sets up Qt infrastructure
        2. ComplexObservableBase.__init__ creates primary and secondary hooks
        3. Secondary hooks are linked to primary hooks via callbacks
        4. _initialize_widgets_impl() creates Qt widgets
        5. Initial widget invalidation queued
        6. Controller ready for use
        
        **Submitting Changes:**
        
        Use `submit_primary_values()` to update primary hooks:
        
        ```python
        # Update single primary value
        controller.submit_primary_values({"selected_key": "new_key"})
        
        # Update multiple primary values atomically
        controller.submit_primary_values({
            "dict_value": new_dict,
            "selected_key": "new_key"
        })
        ```
        
        Secondary hooks automatically recompute when primaries change.
        
        See Also
        --------
        BaseSingleHookController : Simpler alternative for single-value controllers
        ComplexObservableBase : Observables base class for complex hook management
        """

        # ------------------------------------------------------------------------------------------------
        # Prepare the initialization of BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        def invalidate_callback(_self: "BaseComplexHookController[Any, Any, Any, Any, Any]"):
            # Check if the controller has been garbage collected
            if _self is not None: # type: ignore
                _self._widget_invalidation_signal.trigger.emit()

        # ------------------------------------------------------------------------------------------------
        # Initialize BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        BaseController.__init__( # type: ignore
            self,
            nexus_manager=nexus_manager,
            debounce_ms=debounce_ms,
            logger=logger
        )

        ComplexObservableBase.__init__( # type: ignore
            self,
            initial_component_values_or_hooks=initial_component_values,
            verification_method=verification_method,
            secondary_hook_callbacks=secondary_hook_callbacks,
            add_values_to_be_updated_callback=add_values_to_be_updated_callback,
            invalidate_callback=lambda: invalidate_callback(self),
            logger=logger
        )
      
        # ------------------------------------------------------------------------------------------------
        # Initialize widgets
        # ------------------------------------------------------------------------------------------------

        with self._internal_update():
            self.is_blocking_signals = True
            self._initialize_widgets_impl()
            self.is_blocking_signals = False


        # ------------------------------------------------------------------------------------------------
        # Initialize is done!
        # ------------------------------------------------------------------------------------------------

        log_msg(self, f"{cast(Any, self).__class__.__name__} initialized", self._logger, "ComplexHookController initialized")

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    @final
    def dispose_impl(self) -> None:
        """Dispose of the controller and clean up resources."""
        
        # Check if we're in a safe state for cleanup
        # During garbage collection, some objects may be in an unstable state
        try:
            from PySide6.QtWidgets import QApplication
            if QApplication.instance() is None:
                # Qt application has been destroyed, skip cleanup that might use Qt
                return
        except (ImportError, RuntimeError):
            # Qt is shutting down or unavailable
            return
        
        # Disconnect all hooks first to prevent further updates
        try:
            for hook in self.get_dict_of_hooks().values():
                try:
                    hook.disconnect_hook()
                except Exception as e:
                    log_msg(self, "dispose", self._logger, f"Error disconnecting hook '{hook}': {e}")
        except Exception as e:
            log_msg(self, "dispose", self._logger, f"Error disconnecting hooks: {e}")

    def __del__(self) -> None:
        """Mark object as being garbage collected.
        
        Note: We intentionally don't call dispose() here because Qt cleanup
        during garbage collection can crash. Controllers should be explicitly
        disposed before going out of scope, or rely on Qt's parent-child cleanup.
        """
        pass

    ###########################################################################
    # Public API
    ###########################################################################

    def submit_primary_values(self, values: Mapping[PHK, PHV], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        return BaseController.submit_values(self, values, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore