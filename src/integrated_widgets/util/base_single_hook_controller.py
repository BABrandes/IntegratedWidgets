from typing import Generic, TypeVar, Optional, Literal, Callable, Mapping, Any
from logging import Logger

from observables import ObservableSingleValueProtocol, Hook
from observables.core import HookNexus, CarriesHooksBase, NexusManager, DEFAULT_NEXUS_MANAGER
from observables._hooks.owned_hook import OwnedHook

from ..util.resources import log_msg
from .base_controller import BaseController

T = TypeVar('T')
"""Value Type - The type of the single value this controller manages (e.g., int, str, bool, RealUnitedScalar)"""

C = TypeVar('C', bound="BaseSingleHookController[Any, Any]")
"""Controller Type - The concrete controller class for self-referential typing"""

class BaseSingleHookController(BaseController[Literal["value"], T, C], CarriesHooksBase[Literal["value"], T, C], Generic[T, C]):
    """
    Base class for controllers managing a single observable value with a Qt widget.
    
    This is the most commonly used base class for creating custom widget controllers.
    It simplifies controller creation by handling all the hook plumbing, requiring
    only widget initialization and update logic.
    
    **When to Use:**
    Use this base class when your controller needs to:
    - Manage a single value that can change (int, str, bool, custom objects, etc.)
    - Synchronize between an observable/hook and Qt widgets
    - Provide validation for user input
    - Handle debounced updates for smooth user experience
    
    **Type Parameters:**
    
    T : Any
        The type of the single value this controller manages.
        Examples:
        - `int` for IntegerEntryController
        - `str` for TextEntryController
        - `bool` for CheckBoxController
        - `RealUnitedScalar` for complex value types
        - `Path | None` for optional path selection
        
    C : BaseSingleHookController
        The concrete controller subclass type for self-referential typing.
        Always set this to the name of your controller class (as a string).
        This enables proper return types for methods that return `self`.
    
    **Generic Type Declaration Examples:**
    
    ```python
    # Integer controller
    class IntegerController(
        BaseSingleHookController[int, "IntegerController"]
    ):
        # T = int (manages integer values)
        # C = "IntegerController" (self-reference)
        ...
    
    # String controller
    class TextController(
        BaseSingleHookController[str, "TextController"]
    ):
        # T = str (manages string values)
        # C = "TextController" (self-reference)
        ...
    
    # Custom type controller
    class PathController(
        BaseSingleHookController[Path | None, "PathController"]
    ):
        # T = Path | None (manages optional path values)
        # C = "PathController" (self-reference)
        ...
    ```
    
    **Required Method Implementations:**
    
    Subclasses MUST implement these 2 abstract methods:
    
    1. **`_initialize_widgets_impl(self) -> None`**
       Create Qt widgets and connect their signals.
       
       ```python
       def _initialize_widgets_impl(self) -> None:
           # Create widgets
           self._line_edit = QLineEdit()
           
           # Connect Qt signals to controller handlers
           self._line_edit.textChanged.connect(self._on_text_changed)
           self._line_edit.editingFinished.connect(self._on_editing_finished)
       ```
    
    2. **`_invalidate_widgets_impl(self) -> None`**
       Update widget display from current hook value.
       
       ```python
       def _invalidate_widgets_impl(self) -> None:
           # Get current value from hook
           current_value = self.value
           
           # Update widget display
           self._line_edit.setText(str(current_value))
       ```
    
    **Inherited Hook Interface:**
    
    All single-hook controllers automatically get:
    - `value_hook: Hook[T]` - The underlying hook for data binding
    - `value: T` - Property to get/set the current value
    - `change_value(value: T)` - Method to change the value
    - `submit(value: T)` - Submit value with debouncing
    
    **Complete Implementation Example:**
    
    ```python
    from integrated_widgets.util.base_single_hook_controller import BaseSingleHookController
    from PySide6.QtWidgets import QLineEdit, QLabel, QVBoxLayout, QWidget
    from observables import Hook, ObservableSingleValueProtocol
    from typing import Optional, Callable
    
    class CustomTextController(BaseSingleHookController[str, "CustomTextController"]):
        '''Controller for a text entry with live character count.'''
        
        def __init__(
            self,
            value_or_hook_or_observable: str | Hook[str] | ObservableSingleValueProtocol[str],
            *,
            max_length: int = 100,
            debounce_ms: Optional[int] = None,
            logger: Optional[Logger] = None
        ):
            self._max_length = max_length
            
            # Validation function
            def validate(text: str) -> tuple[bool, str]:
                if len(text) > self._max_length:
                    return False, f"Text exceeds {self._max_length} characters"
                return True, "Valid"
            
            # Call parent with validation
            super().__init__(
                value_or_hook_or_observable=value_or_hook_or_observable,
                verification_method=validate,
                debounce_ms=debounce_ms,
                logger=logger
            )
        
        def _initialize_widgets_impl(self) -> None:
            # Create widgets
            self._line_edit = QLineEdit()
            self._char_count_label = QLabel()
            
            # Connect signals
            self._line_edit.textChanged.connect(self._on_text_changed)
        
        def _invalidate_widgets_impl(self) -> None:
            # Update widgets from hook value
            current_text = self.value
            self._line_edit.setText(current_text)
            self._char_count_label.setText(f"{len(current_text)}/{self._max_length}")
        
        def _on_text_changed(self) -> None:
            # User changed text - submit with debounce
            if not self._internal_widget_update:
                new_text = self._line_edit.text()
                self.submit(new_text)  # Debounced submission
        
        @property
        def widget_line_edit(self) -> QLineEdit:
            return self._line_edit
        
        @property
        def widget_label(self) -> QLabel:
            return self._char_count_label
    ```
    
    **Initialization Flow:**
    
    1. User provides value/hook/observable to __init__
    2. BaseSingleHookController creates internal OwnedHook
    3. BaseController.__init__ sets up Qt infrastructure
    4. CarriesHooksBase.__init__ sets up hook system callbacks
    5. _initialize_widgets_impl() is called to create widgets
    6. If a hook/observable was provided, internal hook connects to it
    7. Initial widget invalidation queued
    8. Controller is ready for use
    
    **Data Flow:**
    
    Observable Change → Hook Update → invalidate_callback → Widget Invalidation
    Widget Change → submit() → Debounce Timer → Hook Submission → Observable Update
    
    **Verification Method:**
    
    The optional verification_method allows custom validation logic:
    
    ```python
    def validate_positive(value: int) -> tuple[bool, str]:
        if value < 0:
            return False, "Value must be positive"
        return True, "Valid"
    
    controller = MyController(
        value=42,
        verification_method=validate_positive
    )
    ```
    
    If validation fails, the widget reverts to the last valid value and
    _invalidate_widgets_impl() is called to refresh the display.
    
    See Also
    --------
    BaseController : Foundation class with Qt integration and lifecycle management
    BaseComplexHookController : For controllers with multiple related hooks
    OwnedHook : The hook type used internally for value management
    """

    def __init__(
        self,
        value_or_hook_or_observable: T | Hook[T] | ObservableSingleValueProtocol[T],
        *,
        verification_method: Optional[Callable[[T], tuple[bool, str]]] = None,
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER,
        ) -> None:
        """
        Initialize a single-hook controller with flexible input binding.
        
        This constructor handles three types of initial values and automatically
        creates the internal hook infrastructure for data binding.
        
        **Parameters:**
        
        value_or_hook_or_observable : T | Hook[T] | ObservableSingleValueProtocol[T]
            The initial value or data source to bind to. Can be:
            
            1. **Plain value** (type T):
               Creates an isolated controller with the given initial value.
               ```python
               controller = TextController("initial text")
               ```
            
            2. **Hook** (Hook[T]):
               Connects the controller to an existing hook for bidirectional sync.
               ```python
               existing_hook = FloatingHook(42)
               controller = IntegerController(existing_hook)
               # Changes to existing_hook update controller, and vice versa
               ```
            
            3. **Observable** (ObservableSingleValueProtocol[T]):
               Connects to an observable's value hook for bidirectional sync.
               ```python
               observable = ObservableSingleValue(True)
               controller = CheckBoxController(observable)
               # Changes to observable update controller, and vice versa
               ```
        
        verification_method : Callable[[T], tuple[bool, str]] | None, optional
            Optional validation function that checks if a value is acceptable.
            
            **Signature:** `(value: T) -> tuple[success: bool, message: str]`
            
            - Return `(True, "Valid")` if value is acceptable
            - Return `(False, "Error message")` if value should be rejected
            
            When validation fails:
            - The value is NOT submitted to the hook
            - Widgets are invalidated to show the last valid value
            - User sees their invalid input cleared
            
            **Example:**
            ```python
            def validate_percentage(value: float) -> tuple[bool, str]:
                if 0.0 <= value <= 100.0:
                    return True, "Valid percentage"
                return False, "Value must be between 0 and 100"
            
            controller = FloatController(
                50.0,
                verification_method=validate_percentage
            )
            ```
        
        debounce_ms : int | None, optional
            Debounce time in milliseconds for user input changes.
            - Default: 100ms (DEFAULT_DEBOUNCE_MS)
            - 0: Immediate submission (no debounce)
            - Higher values: Better for rapid input like typing
            
            **Example:**
            ```python
            # Quick response for buttons
            button_controller = CheckBoxController(False, debounce_ms=0)
            
            # Smooth typing experience
            text_controller = TextController("", debounce_ms=300)
            ```
        
        logger : Logger | None, optional
            Optional logger for debugging. Logs:
            - Initialization and disposal events
            - Widget invalidation calls
            - Value submission success/failure
            - Hook connection status
        
        nexus_manager : NexusManager, optional
            The nexus manager coordinating hook connections.
            Default: DEFAULT_NEXUS_MANAGER (usually sufficient)
            
            Custom nexus managers enable isolated hook networks for testing
            or multi-tenant applications.
        
        **What This Constructor Does:**
        
        1. Extracts value and optional hook from the input parameter
        2. Creates an internal OwnedHook with the initial value
        3. Initializes BaseController (Qt infrastructure, timers, signals)
        4. Initializes CarriesHooksBase (hook system callbacks)
        5. Calls _initialize_widgets_impl() to create Qt widgets
        6. Connects internal hook to provided hook/observable (if any)
        7. Queues initial widget invalidation
        
        **After Construction:**
        
        The controller is fully initialized and ready to use:
        - Widgets are created but not yet updated
        - Initial invalidation is queued (will update widgets)
        - Hook connections are active
        - Ready for user interaction
        
        **Example Usage:**
        
        ```python
        from observables import ObservableSingleValue
        
        # Create observable
        count_observable = ObservableSingleValue(0)
        
        # Create controller bound to observable
        controller = IntegerEntryController(
            value_or_hook_or_observable=count_observable,
            verification_method=lambda x: (x >= 0, "Must be non-negative"),
            debounce_ms=150,
            logger=my_logger
        )
        
        # Access widgets
        my_layout.addWidget(controller.widget_line_edit)
        
        # Value changes sync bidirectionally
        count_observable.set_value(42)  # Widget updates
        # User types "100" in widget → observable updates to 100
        ```
        """

        self._verification_method: Optional[Callable[[T], tuple[bool, str]]] = verification_method

        # ------------------------------------------------------------------------------------------------
        # Handle the provided value or hook or observable
        # ------------------------------------------------------------------------------------------------

        if isinstance(value_or_hook_or_observable, ObservableSingleValueProtocol):
            value_provided_value: T = value_or_hook_or_observable.value # type: ignore
            value_provided_hook: Optional[Hook[T]] = value_or_hook_or_observable.hook # type: ignore

        elif isinstance(value_or_hook_or_observable, Hook):
            value_provided_value = value_or_hook_or_observable.value # type: ignore
            value_provided_hook = value_or_hook_or_observable # type: ignore

        else:
            # It should be T
            value_provided_value = value_or_hook_or_observable # type: ignore
            value_provided_hook = None # type: ignore

        # ------------------------------------------------------------------------------------------------
        # Set the internal value hook
        # ------------------------------------------------------------------------------------------------

        self._internal_hook: OwnedHook[T] = OwnedHook[T](
            owner=self, 
            initial_value=value_provided_value, # type: ignore
            logger=logger,
            nexus_manager=nexus_manager
        )

        # ------------------------------------------------------------------------------------------------
        # Prepare the initialization of BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        # Step 1: Validate complete values in isolation callback
        def validate_complete_values_in_isolation_callback(_self: "BaseSingleHookController[Any, Any]", values: Mapping[Literal["value"], T]) -> tuple[bool, str]:
            """
            Check if the values are valid as part of the owner.
            """

            if _self._verification_method is None:
                return True, "Verification method is not set"

            try:
                value: T = values["value"] # type: ignore
                success, msg = _self._verification_method(value)

                if not success:
                    return False, msg
                else:
                    return True, "Verification method passed"

            except Exception as e:
                return False, f"Error validating value: {e}"

        # Step 2: Invalidate callback
        def invalidate_callback(_self: "BaseSingleHookController[Any, Any]") -> tuple[bool, str]:
            """Queue a widget invalidation request through the Qt event loop.
            
            Uses QueuedConnection to ensure widget updates happen asynchronously,
            preventing re-entrancy issues during hook system operations.
            
            Args:
                _self: Reference to the controller (weakref).
                calling_nexus_manager: The nexus manager calling this callback.
            """
            try:
                if _self is not None: # type: ignore
                    _self._widget_invalidation_signal.trigger.emit()
                else:
                    return False, "Controller has been garbage collected"

            except Exception as e:
                return False, f"Error invalidating widgets: {e}"

            return True, "Widgets invalidated"

        # ------------------------------------------------------------------------------------------------
        # Initialize BaseController and CarriesHooksBase
        # ------------------------------------------------------------------------------------------------

        BaseController.__init__( # type: ignore
            self,
            nexus_manager=nexus_manager,
            debounce_ms=debounce_ms,
            logger=logger
        )

        CarriesHooksBase.__init__( # type: ignore
            self,
            validate_complete_values_in_isolation_callback=validate_complete_values_in_isolation_callback,
            invalidate_callback=invalidate_callback,
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
        # Connect hooks, if provided
        # ------------------------------------------------------------------------------------------------

        if isinstance(value_provided_hook, Hook):
            self._internal_hook.connect_hook(value_provided_hook, initial_sync_mode="use_target_value") # type: ignore

        # ------------------------------------------------------------------------------------------------
        # Initialize is done!
        # ------------------------------------------------------------------------------------------------

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "SingleHookController initialized")

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

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
        
        # Disconnect value hook
        try:
            self.value_hook.disconnect_hook()
        except Exception as e:
            log_msg(self, "dispose", self._logger, f"Error disconnecting value hook: {e}")

    def __del__(self) -> None:
        """Mark object as being garbage collected.
        
        Note: We intentionally don't call dispose() here because Qt cleanup
        during garbage collection can crash. Controllers should be explicitly
        disposed before going out of scope, or rely on Qt's parent-child cleanup.
        """
        pass

    ###########################################################################
    # Convenience Properties and Methods
    ###########################################################################

    @property
    def value_hook(self) -> Hook[T]:
        return self._internal_hook

    @property
    def value(self) -> T:
        return self._internal_hook.value

    @value.setter
    def value(self, value: T) -> None:
        self.submit(value)

    def change_value(self, value: T) -> None:
        self.submit(value)

    ###########################################################################
    # CarriesHooksBase Interface Implementation
    ###########################################################################

    def _get_hook(self, key: Literal["value"]) -> OwnedHook[T]:
        """
        Get a hook by its key.
        """
        match key:
            case "value":
                return self._internal_hook # type: ignore

            case _: # type: ignore
                raise ValueError("Invalid key")
            
    def _get_value_reference_of_hook(self, key: Literal["value"]) -> T:
        """
        Get a value as a reference by its key.
        """
        match key:
            case "value":
                return self._internal_hook.value_reference

            case _: # type: ignore
                raise ValueError("Invalid key")
        
    def _get_hook_keys(self) -> set[Literal["value"]]:
        """
        Get all keys of the hooks.
        """
        return {"value"}

    def _get_hook_key(self, hook_or_nexus: Hook[Any]|HookNexus[Any]) -> Literal["value"]:
        """
        Get the key of a hook or nexus.
        """

        if isinstance(hook_or_nexus, Hook):
            match hook_or_nexus:
                case self._internal_hook:
                    return "value"

                case _:
                    raise ValueError("Invalid hook")
        elif isinstance(hook_or_nexus, HookNexus): # type: ignore
            match hook_or_nexus:
                case self._internal_hook.hook_nexus:
                    return "value"

                case _:
                    raise ValueError("Invalid nexus")
        else:
            raise ValueError("Invalid hook or nexus")

    ###########################################################################
    # Public API
    ###########################################################################


    def submit(self, value: T, *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """
        Submit the single value of this single hook controller with debouncing. (Shortcut for submit_values_debounced({"value": value}, debounce_ms=debounce_ms))
        """
        self._submit_values_debounced({"value": value}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)