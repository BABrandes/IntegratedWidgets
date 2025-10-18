from __future__ import annotations

# Standard library imports
from typing import Generic, TypeVar, Callable, Any, Mapping, Literal
from logging import Logger

# BAB imports
from observables import ObservableSelectionDict, Hook, ObservableSingleValueProtocol

# Local imports
from ..util.base_complex_hook_controller import BaseComplexHookController
from ..controlled_widgets.controlled_combobox import ControlledComboBox
from ..controlled_widgets.controlled_qlabel import ControlledQLabel
from ..util.resources import log_msg, combo_box_find_data

K = TypeVar("K")
V = TypeVar("V")

class DictSelectionController(BaseComplexHookController[Literal["dict", "selected_key", "selected_value"], Any, dict[K, V] | K | V, Any, "DictSelectionController[K, V]"], Generic[K,V]):
    """
    A controller for managing selection from a dictionary.
    
    This controller provides a combobox widget that allows users to select from dictionary 
    keys. It can synchronize with observable values and hooks from the observables library, 
    making it suitable for reactive applications.
    
    The controller maintains three synchronized values:
    - dict: The dictionary to select from
    - selected_key: The currently selected key (must always be set)
    - selected_value: The value at the selected key
    
    The controller ensures that the selected_key is always present in the dictionary.
    The dictionary must never be empty since a key must always be selected.
    
    Parameters
    ----------
    dict_value : dict[K, V] | Hook[dict[K, V]] | ObservableSelectionDict[K, V]
        The initial dictionary or an observable/hook to sync with. Can be:
        - A direct dictionary value (must not be empty)
        - A Hook object for bidirectional synchronization
        - An ObservableSelectionDict that provides dict, key, and value
    selected_key : K | Hook[K] | None
        The initial selected key or an observable/hook to sync with. Can be:
        - A direct value
        - A Hook object for bidirectional synchronization
        - None only if dict_value is ObservableSelectionDict
    selected_value : V | Hook[V] | None
        The initial selected value or an observable/hook to sync with. Can be:
        - A direct value
        - A Hook object for bidirectional synchronization
        - None only if dict_value is ObservableSelectionDict
    formatter : Callable[[K], str], optional
        Function to convert keys to display strings. Defaults to str().
    logger : Logger, optional
        Logger instance for debugging. Defaults to None.
    
    Raises
    ------
    ValueError
        If selected_key or selected_value is provided when dict_value is ObservableSelectionDict.
    ValueError
        If selected_key is not in the dictionary.
    ValueError
        If the dictionary is empty.
    
    Attributes
    ----------
    dict_value : dict[K, V]
        Property to get/set the dictionary.
    selected_key : K
        Property to get/set the currently selected key.
    selected_value : V
        Property to get/set the currently selected value.
    dict_hook : OwnedHook[dict[K, V]]
        Hook for the dictionary that can be connected to observables.
    selected_key_hook : OwnedHook[K]
        Hook for the selected key that can be connected to observables.
    selected_value_hook : OwnedHook[V]
        Hook for the selected value that can be connected to observables.
    formatter : Callable[[K], str]
        Property to get/set the formatter function.
    widget_combobox : ControlledComboBox
        The combobox widget for user selection.
    widget_label : ControlledQLabel
        A label widget showing the current selection (created on first access).
    
    Examples
    --------
    Basic usage with static values:
    
    >>> controller = DictSelectionController(
    ...     dict_value={"apple": "red", "banana": "yellow", "orange": "orange"},
    ...     selected_key="apple"
    ... )
    >>> controller.selected_key
    'apple'
    >>> controller.selected_value
    'red'
    >>> controller.selected_key = "banana"
    
    With observables for reactive programming:
    
    >>> from observables import ObservableSelectionDict
    >>> observable = ObservableSelectionDict(
    ...     dict_hook={"red": 1, "green": 2, "blue": 3},
    ...     key_hook="red"
    ... )
    >>> controller = DictSelectionController(observable)
    >>> # Changes to controller.selected_key automatically sync with observable
    
    Custom formatting:
    
    >>> controller = DictSelectionController(
    ...     dict_value={1: "one", 2: "two", 3: "three"},
    ...     selected_key=1,
    ...     formatter=lambda x: f"Key {x}"
    ... )
    
    Dict-like interface:
    
    >>> controller["new_key"] = "new_value"  # Add to dictionary
    >>> value = controller["new_key"]  # Get value
    >>> del controller["new_key"]  # Remove from dictionary (if not selected)
    >>> keys = list(controller.keys())  # Get all keys
    >>> values = list(controller.values())  # Get all values
    
    Notes
    -----
    - Keys in the dropdown are sorted by their formatted text
    - The controller validates that selected_key is always in the dictionary
    - Empty dictionary ({}) is invalid - there must always be at least one key-value pair
    - The controller provides a dict-like interface for convenience
    """

    def __init__(
        self,
        dict_value: dict[K, V] | Hook[dict[K, V]] | ObservableSelectionDict[K, V],
        selected_key: K | Hook[K] | ObservableSingleValueProtocol[K] | None = None,
        selected_value: V | Hook[V] | ObservableSingleValueProtocol[V] | None = None,
        *,
        formatter: Callable[[K], str] = lambda item: str(item),
        debounce_ms: int | None = None,
        logger: Logger | None = None,
    ) -> None:

        log_msg(self, "__init__", logger, f"Starting initialization with dict_value={dict_value}, selected_key={selected_key}, selected_value={selected_value}")
        
        self._formatter = formatter
        log_msg(self, "__init__", logger, f"Formatter set: {formatter}")

        if isinstance(dict_value, ObservableSelectionDict):
            log_msg(self, "__init__", logger, "dict_value is ObservableSelectionDict")
            if selected_key is not None or selected_value is not None:
                raise ValueError("selected_key and selected_value are not allowed when dict_value is an ObservableSelectionDict")

            initial_dict_value: dict[K, V] = dict_value.dict_hook.value # type: ignore
            hook_dict_value: Hook[dict[K, V]] | None = dict_value.dict_hook # type: ignore
            initial_selected_key: K = dict_value.key_hook.value # type: ignore
            hook_selected_key: Hook[K] | None = dict_value.key_hook # type: ignore
            initial_selected_value: V = dict_value.value_hook.value # type: ignore
            hook_selected_value: Hook[V] | None = dict_value.value_hook # type: ignore
            
            log_msg(self, "__init__", logger, f"From ObservableSelectionDict: initial_dict_value={initial_dict_value}, initial_selected_key={initial_selected_key}, initial_selected_value={initial_selected_value}")

        else:
            log_msg(self, "__init__", logger, "dict_value is not ObservableSelectionDict, processing manually")

            if isinstance(dict_value, Hook):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "dict_value is Hook")
                initial_dict_value: dict[K, V] = dict_value.value # type: ignore
                hook_dict_value: Hook[dict[K, V]] | None = dict_value # type: ignore
                log_msg(self, "__init__", logger, f"From Hook: initial_dict_value={initial_dict_value}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "dict_value is direct value")
                initial_dict_value = dict_value
                hook_dict_value = None
                log_msg(self, "__init__", logger, f"Direct value: initial_dict_value={initial_dict_value}")
            
            # Validate that dict is not empty
            if not initial_dict_value:
                raise ValueError("Dictionary cannot be empty for DictSelectionController")
            
            if selected_key is None:
                log_msg(self, "__init__", logger, "selected_key is None, using first key from dict")
                initial_selected_key = next(iter(initial_dict_value.keys()))
                hook_selected_key = None
                log_msg(self, "__init__", logger, f"Using first key: initial_selected_key={initial_selected_key}")

            elif isinstance(selected_key, Hook):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "selected_key is Hook")
                initial_selected_key: K = selected_key.value # type: ignore
                hook_selected_key: Hook[K] | None = selected_key # type: ignore
                log_msg(self, "__init__", logger, f"From Hook: initial_selected_key={initial_selected_key}")

            elif isinstance(selected_key, ObservableSingleValueProtocol):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "selected_key is ObservableSingleValueProtocol")
                initial_selected_key: K = selected_key.value # type: ignore
                hook_selected_key: Hook[K] | None = selected_key.hook # type: ignore
                log_msg(self, "__init__", logger, f"From ObservableSingleValueProtocol: initial_selected_key={initial_selected_key}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "selected_key is direct value")
                initial_selected_key = selected_key
                hook_selected_key = None
                log_msg(self, "__init__", logger, f"Direct value: initial_selected_key={initial_selected_key}")
            
            if selected_value is None:
                log_msg(self, "__init__", logger, "selected_value is None, computing from selected_key")
                initial_selected_value = initial_dict_value[initial_selected_key]
                hook_selected_value = None
                log_msg(self, "__init__", logger, f"Computed from selected_key: initial_selected_value={initial_selected_value}")

            elif isinstance(selected_value, Hook):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "selected_value is Hook")
                initial_selected_value: V = selected_value.value # type: ignore
                hook_selected_value: Hook[V] | None = selected_value # type: ignore
                log_msg(self, "__init__", logger, f"From Hook: initial_selected_value={initial_selected_value}")

            elif isinstance(selected_value, ObservableSingleValueProtocol):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "selected_value is ObservableSingleValueProtocol")
                initial_selected_value: V = selected_value.value # type: ignore
                hook_selected_value: Hook[V] | None = selected_value.hook # type: ignore
                log_msg(self, "__init__", logger, f"From ObservableSingleValueProtocol: initial_selected_value={initial_selected_value}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "selected_value is direct value")
                initial_selected_value = selected_value
                hook_selected_value = None
                log_msg(self, "__init__", logger, f"Direct value: initial_selected_value={initial_selected_value}")
        
        log_msg(self, "__init__", logger, f"Final values: initial_dict_value={initial_dict_value}, initial_selected_key={initial_selected_key}, initial_selected_value={initial_selected_value}")

        def add_values_to_be_updated_callback(
            self_ref: "DictSelectionController[K, V]",
            current_values: Mapping[Literal["dict", "selected_key", "selected_value"], Any],
            submitted_values: Mapping[Literal["dict", "selected_key", "selected_value"], Any]
            ) -> Mapping[Literal["dict", "selected_key", "selected_value"], Any]:
            """
            Add values to be updated if the submitted values are not complete.
            """

            match ("dict" in submitted_values, "selected_key" in submitted_values, "selected_value" in submitted_values):
                case (True, True, True):
                    # All three values provided
                    return {}
                case (True, True, False):
                    # Dict and selected_key provided - get selected_value from dict
                    if submitted_values["selected_key"] not in submitted_values["dict"]:
                        raise KeyError(f"Key {submitted_values['selected_key']} not in dictionary")
                    selected_value = submitted_values["dict"][submitted_values["selected_key"]]
                    return {"selected_value": selected_value}
                case (True, False, True):
                    # Dict and selected_value provided - validate selected_value matches selected_key
                    if submitted_values["selected_value"] != submitted_values["dict"][current_values["selected_key"]]:
                        raise ValueError(f"Value {submitted_values['selected_value']} is not the same as the value in the dictionary {submitted_values['dict'][current_values['selected_key']]}")
                    return {}
                case (True, False, False):
                    # Dict provided - get selected_value for current selected_key
                    # Check if current selected_key exists in the new dict
                    if current_values["selected_key"] not in submitted_values["dict"]:
                        # If selected key is not in new dict, raise error - don't override submitted values
                        raise KeyError(f"Selected key {current_values['selected_key']} not in new dictionary")
                    else:
                        selected_value = submitted_values["dict"][current_values["selected_key"]]
                        return {"selected_value": selected_value}
                case (False, True, True):
                    # selected_key and selected_value provided - update dict with new value
                    _dict = current_values["dict"].copy()
                    _dict[submitted_values["selected_key"]] = submitted_values["selected_value"]
                    return {"dict": _dict}
                case (False, True, False):
                    # selected_key provided - get selected_value from current dict
                    if submitted_values["selected_key"] not in current_values["dict"]:
                        # If key doesn't exist, raise error - don't override submitted values
                        raise KeyError(f"Key {submitted_values['selected_key']} not in dictionary")
                    selected_value = current_values["dict"][submitted_values["selected_key"]]
                    return {"selected_value": selected_value}
                case (False, False, True):
                    # selected_value provided - update dict with the new value at current key
                    _dict = current_values["dict"].copy()
                    _dict[current_values["selected_key"]] = submitted_values["selected_value"]
                    return {"dict": _dict}
                case (False, False, False):
                    # Nothing provided - no updates needed
                    return {}

            raise ValueError("Invalid keys")

        def verification_method(values: Mapping[Literal["dict", "selected_key", "selected_value"], Any]) -> tuple[bool, str]:
            log_msg(self, "verification_method", logger, f"Verifying: {values}")
            # Handle partial updates by getting current values for missing keys

            if "dict" in values:
                dict_value: dict[K, V] = values["dict"]
                log_msg(self, "verification_method", logger, f"dict_value from input: {dict_value}")
            else:
                dict_value = self.get_value_of_hook("dict") # type: ignore
                log_msg(self, "verification_method", logger, f"dict_value from current: {dict_value}")

            if "selected_key" in values:
                selected_key: K = values["selected_key"]
                log_msg(self, "verification_method", logger, f"selected_key from input: {selected_key}")
            else:
                selected_key = self.get_value_of_hook("selected_key") # type: ignore
                log_msg(self, "verification_method", logger, f"selected_key from current: {selected_key}")

            if "selected_value" in values:
                selected_value: V = values["selected_value"]
                log_msg(self, "verification_method", logger, f"selected_value from input: {selected_value}")
            else:
                selected_value = self.get_value_of_hook("selected_value") # type: ignore
                log_msg(self, "verification_method", logger, f"selected_value from current: {selected_value}")

            # Validate consistency
            if not dict_value:
                log_msg(self, "verification_method", logger, "VERIFICATION FAILED: dictionary is empty")
                return False, "Dictionary cannot be empty"
            
            if selected_key not in dict_value:
                log_msg(self, "verification_method", logger, f"VERIFICATION FAILED: {selected_key} not in {dict_value}")
                return False, f"Selected key {selected_key} not in dictionary: {dict_value}"
            
            if selected_value != dict_value[selected_key]:
                log_msg(self, "verification_method", logger, f"VERIFICATION FAILED: {selected_value} != {dict_value[selected_key]}")
                return False, f"Selected value {selected_value} does not match dictionary value {dict_value[selected_key]}"
            
            log_msg(self, "verification_method", logger, "VERIFICATION PASSED")
            return True, "Verification method passed"

        log_msg(self, "__init__", logger, "Calling super().__init__")
        super().__init__(
            {
                "dict": initial_dict_value,
                "selected_key": initial_selected_key,
                "selected_value": initial_selected_value
            },
            add_values_to_be_updated_callback=add_values_to_be_updated_callback, # type: ignore
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            logger=logger
        )
        
        log_msg(self, "__init__", logger, "Super().__init__ completed, attaching hooks")
        
        if hook_dict_value is not None:
            log_msg(self, "__init__", logger, f"Attaching dict hook: {hook_dict_value}")
            self.connect_hook(hook_dict_value, "dict", initial_sync_mode="use_target_value") # type: ignore
        if hook_selected_key is not None:
            log_msg(self, "__init__", logger, f"Attaching selected_key hook: {hook_selected_key}")
            self.connect_hook(hook_selected_key, "selected_key", initial_sync_mode="use_target_value") # type: ignore
        if hook_selected_value is not None:
            log_msg(self, "__init__", logger, f"Attaching selected_value hook: {hook_selected_value}")
            self.connect_hook(hook_selected_value, "selected_value", initial_sync_mode="use_target_value") # type: ignore
        
        log_msg(self, "__init__", logger, "Initialization completed successfully")

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """
        Create and configure all the user interface widgets.
        
        This method is called internally during initialization. It creates the combobox
        widget and connects its signals to the controller's internal handlers.
        
        Created Widgets
        ---------------
        - ControlledComboBox: The dropdown selection widget
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        log_msg(self, "initialize_widgets", self._logger, "Starting widget initialization")

        self._combobox = ControlledComboBox(self, logger=self._logger)
        log_msg(self, "initialize_widgets", self._logger, f"Created ControlledComboBox: {self._combobox}")

        # Connect UI -> model
        self._combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed()) # type: ignore
        log_msg(self, "initialize_widgets", self._logger, "Connected currentIndexChanged signal")

        log_msg(self, "initialize_widgets", self._logger, "Widget initialization completed")

    def _on_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a different option from the dropdown menu.
        
        This internal callback is triggered whenever the combobox index changes. It:
        1. Checks if signals are currently blocked (to prevent feedback loops)
        2. Retrieves the selected key data from the combobox
        3. Submits the new values through the controller's validation system
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        log_msg(self, "_on_combobox_index_changed", self._logger, "Combo box index changed")

        if self.is_blocking_signals:
            log_msg(self, "_on_combobox_index_changed", self._logger, "Signals are blocked, returning")
            return
        
        ################# Processing user input #################
        log_msg(self, "_on_combobox_index_changed", self._logger, "Processing user input")

        # Get the new key from the combo box
        new_key: K = self._combobox.currentData()
        log_msg(self, "_on_combobox_index_changed", self._logger, f"New key from combo box: {new_key}")

        # Submit only the selected_key - the add_values_to_be_updated_callback will complete the rest
        self.submit_value("selected_key", new_key)
        
        log_msg(self, "_on_combobox_index_changed", self._logger, "Combo box change handling completed")

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the widgets from the component values.
        
        This internal method synchronizes the UI widgets with the current state of
        the controller's values. It:
        1. Clears the combobox
        2. Adds all dictionary keys (sorted by formatted text)
        3. Sets the combobox to display the currently selected key
        4. Updates the label widget if it exists
        
        The method is called automatically whenever the controller's state changes,
        whether from user interaction, programmatic changes, or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

        component_values: dict[Literal["dict", "selected_key", "selected_value"], Any] = self.get_dict_of_values() # type: ignore

        log_msg(self, "_invalidate_widgets", self._logger, f"Filling widgets with: {component_values}")

        dict_value: dict[K, V] = component_values["dict"]
        selected_key: K = component_values["selected_key"]
        selected_value: V = component_values["selected_value"]
        log_msg(self, "_invalidate_widgets", self._logger, f"dict_value: {dict_value}, selected_key: {selected_key}, selected_value: {selected_value}")
        
        log_msg(self, "_invalidate_widgets", self._logger, "Starting widget update")
        
        self._combobox.clear()
        log_msg(self, "_invalidate_widgets", self._logger, "Cleared combo box")
        
        sorted_keys = sorted(dict_value.keys(), key=self._formatter)
        log_msg(self, "_invalidate_widgets", self._logger, f"Sorted keys: {sorted_keys}")
        
        for key in sorted_keys:
            formatted_text = self._formatter(key)
            log_msg(self, "_invalidate_widgets", self._logger, f"Adding item: '{formatted_text}' with data: {key}")
            self._combobox.addItem(formatted_text, userData=key) # type: ignore
        
        current_index = combo_box_find_data(self._combobox, selected_key)
        log_msg(self, "_invalidate_widgets", self._logger, f"Setting current index to: {current_index} for selected_key: {selected_key}")
        self._combobox.setCurrentIndex(current_index)

        if hasattr(self, "_label"):
            self._label.setText(self._formatter(self.selected_key))
        
        log_msg(self, "_invalidate_widgets", self._logger, "Widget update completed")

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def dict_value(self) -> dict[K, V]:
        """
        Get the dictionary.
        
        Returns
        -------
        dict[K, V]
            The current dictionary.
        """
        value: dict[K, V] = self.get_value_of_hook("dict") # type: ignore
        log_msg(self, "dict_value.getter", self._logger, f"Getting dict_value: {value}")
        return value
    
    @dict_value.setter
    def dict_value(self, dict_value: dict[K, V]) -> None:
        """
        Set the dictionary.
        
        Parameters
        ----------
        dict_value : dict[K, V]
            The new dictionary (must not be empty).
        
        Raises
        ------
        ValueError
            If the dictionary is empty.
        ValueError
            If the currently selected_key is not in the new dictionary.
        """
        log_msg(self, "dict_value.setter", self._logger, f"Setting dict_value to: {dict_value}")
        self.submit_values({"dict": dict_value})

    def change_dict_value(self, dict_value: dict[K, V]) -> None:
        """
        Set the dictionary (alternative method name).
        
        This method is functionally identical to using the dict_value property setter.
        
        Parameters
        ----------
        dict_value : dict[K, V]
            The new dictionary (must not be empty).
        
        Raises
        ------
        ValueError
            If the dictionary is empty.
        ValueError
            If the currently selected_key is not in the new dictionary.
        """
        log_msg(self, "change_dict_value", self._logger, f"Changing dict_value to: {dict_value}")
        self.submit_values({"dict": dict_value})

    @property
    def selected_key(self) -> K:
        """
        Get the currently selected key.
        
        Returns
        -------
        K
            The currently selected key.
        """
        value: K = self.get_value_of_hook("selected_key") # type: ignore
        log_msg(self, "selected_key.getter", self._logger, f"Getting selected_key: {value}")
        return value
    
    @selected_key.setter
    def selected_key(self, selected_key: K) -> None:
        """
        Set the selected key.
        
        Parameters
        ----------
        selected_key : K
            The key to select.
        
        Raises
        ------
        ValueError
            If the selected_key is not in the dictionary.
        """
        log_msg(self, "selected_key.setter", self._logger, f"Setting selected_key to: {selected_key}")
        
        # Submit only the selected_key - the add_values_to_be_updated_callback will complete the rest
        self.submit_value("selected_key", selected_key)

    def change_selected_key(self, selected_key: K) -> None:
        """
        Set the selected key (alternative method name).
        
        This method is functionally identical to using the selected_key property setter.
        
        Parameters
        ----------
        selected_key : K
            The key to select.
        
        Raises
        ------
        ValueError
            If the selected_key is not in the dictionary.
        """
        log_msg(self, "change_selected_key", self._logger, f"Changing selected_key to: {selected_key}")
        
        # Submit only the selected_key - the add_values_to_be_updated_callback will complete the rest
        self.submit_value("selected_key", selected_key)
    
    @property
    def selected_value(self) -> V:
        """
        Get the currently selected value.
        
        Returns
        -------
        V
            The currently selected value.
        """
        value: V = self.get_value_of_hook("selected_value") # type: ignore
        log_msg(self, "selected_value.getter", self._logger, f"Getting selected_value: {value}")
        return value
    
    @selected_value.setter
    def selected_value(self, selected_value: V) -> None:
        """
        Set the selected value.
        
        Parameters
        ----------
        selected_value : V
            The value to set for the currently selected key.
        """
        log_msg(self, "selected_value.setter", self._logger, f"Setting selected_value to: {selected_value}")
        self.submit_values({"selected_value": selected_value})

    def change_selected_value(self, selected_value: V) -> None:
        """
        Set the selected value (alternative method name).
        
        This method is functionally identical to using the selected_value property setter.
        
        Parameters
        ----------
        selected_value : V
            The value to set for the currently selected key.
        """
        log_msg(self, "change_selected_value", self._logger, f"Changing selected_value to: {selected_value}")
        self.submit_values({"selected_value": selected_value})
    
    @property
    def dict_hook(self) -> Hook[dict[K, V]]:
        """
        Get the hook for the dictionary.
        
        The hook can be connected to observables for bidirectional synchronization.
        
        Returns
        -------
        OwnedHook[dict[K, V]]
            The hook object for the dict value.
        """
        hook: Hook[dict[K, V]] = self.get_hook("dict") # type: ignore
        return hook
    
    @property
    def selected_key_hook(self) -> Hook[K]:
        """
        Get the hook for the selected key.
        
        The hook can be connected to observables for bidirectional synchronization.
        
        Returns
        -------
        OwnedHook[K]
            The hook object for the selected_key value.
        """
        hook: Hook[K] = self.get_hook("selected_key") # type: ignore
        return hook
    
    @property
    def selected_value_hook(self) -> Hook[V]:
        """
        Get the hook for the selected value.
        
        The hook can be connected to observables for bidirectional synchronization.
        
        Returns
        -------
        OwnedHook[V]
            The hook object for the selected_value value.
        """
        hook: Hook[V] = self.get_hook("selected_value") # type: ignore
        return hook

    def change_dict_key_and_value(self, selected_key: K, selected_value: V) -> None:
        """
        Set the selected key and value atomically.
        
        This method allows you to change both values in a single operation, which
        is useful when you need to ensure consistency or avoid intermediate validation
        failures.
        
        Parameters
        ----------
        selected_key : K
            The new selected key.
        selected_value : V
            The new selected value.
        
        Raises
        ------
        ValueError
            If selected_key is not in the dictionary.
        
        Examples
        --------
        >>> controller.change_dict_key_and_value(
        ...     selected_key="orange",
        ...     selected_value="orange_color"
        ... )
        """
        log_msg(self, "change_dict_key_and_value", self._logger, f"Changing both: selected_key={selected_key}, selected_value={selected_value}")
        self.submit_values({"selected_key": selected_key, "selected_value": selected_value})

    def change_dict_and_key(self, dict_value: dict[K, V], selected_key: K) -> None:
        """
        Set the dictionary and selected key atomically.
        
        This method allows you to change both values in a single operation, which
        is useful when you need to ensure consistency or avoid intermediate validation
        failures.
        
        Parameters
        ----------
        dict_value : dict[K, V]
            The new dictionary (must not be empty).
        selected_key : K
            The new selected key.
        
        Raises
        ------
        ValueError
            If the dictionary is empty.
        ValueError
            If selected_key is not in the dictionary.
        
        Examples
        --------
        >>> controller.change_dict_and_key(
        ...     dict_value={"orange": "orange_color", "grape": "purple_color"},
        ...     selected_key="orange"
        ... )
        """
        log_msg(self, "change_dict_and_key", self._logger, f"Changing both: dict_value={dict_value}, selected_key={selected_key}")
        self.submit_values({"dict": dict_value, "selected_key": selected_key})

    def change_all(self, dict_value: dict[K, V], selected_key: K, selected_value: V) -> None:
        """
        Set the dictionary, selected key, and selected value atomically.
        
        This method allows you to change all three values in a single operation, which
        is useful when you need to ensure consistency or avoid intermediate validation
        failures.
        
        Parameters
        ----------
        dict_value : dict[K, V]
            The new dictionary (must not be empty).
        selected_key : K
            The new selected key.
        selected_value : V
            The new selected value.
        
        Raises
        ------
        ValueError
            If the dictionary is empty.
        ValueError
            If selected_key is not in the dictionary.
        
        Examples
        --------
        >>> controller.change_all(
        ...     dict_value={"orange": "orange_color", "grape": "purple_color"},
        ...     selected_key="orange",
        ...     selected_value="orange_color"
        ... )
        """
        log_msg(self, "change_all", self._logger, f"Changing all: dict_value={dict_value}, selected_key={selected_key}, selected_value={selected_value}")
        self.submit_values({"dict": dict_value, "selected_key": selected_key, "selected_value": selected_value})

    @property
    def formatter(self) -> Callable[[K], str]:
        """
        Get the formatter function.
        
        Returns
        -------
        Callable[[K], str]
            The current formatter function used to convert keys to display strings.
        """
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Callable[[K], str]) -> None:
        """
        Set the formatter function.
        
        Changing the formatter will automatically update the widget display.
        
        Parameters
        ----------
        formatter : Callable[[K], str]
            A function that takes a key value and returns its display string.
        
        Examples
        --------
        >>> controller.formatter = lambda x: f"Key {x}"
        >>> controller.formatter = str.upper
        """
        log_msg(self, "formatter.setter", self._logger, f"Setting formatter to: {formatter}")
        self._formatter = formatter
        self.invalidate_widgets()

    def change_formatter(self, formatter: Callable[[K], str]) -> None:
        """
        Set the formatter function (alternative method name).
        
        This method is functionally identical to using the formatter property setter.
        Changing the formatter will automatically update the widget display.
        
        Parameters
        ----------
        formatter : Callable[[K], str]
            A function that takes a key value and returns its display string.
        """
        log_msg(self, "change_formatter", self._logger, f"Changing formatter to: {formatter}")
        self._formatter = formatter
        self.invalidate_widgets()

    @property
    def widget_combobox(self) -> ControlledComboBox:
        """
        Get the combobox widget for displaying and selecting keys.
        
        This is the primary widget for user interaction. It displays all available
        keys and allows the user to select one.
        
        Returns
        -------
        ControlledComboBox
            The combobox widget managed by this controller.
        """
        return self._combobox

    @property
    def widget_label(self) -> ControlledQLabel:
        """
        Get a label widget that displays the current selection.
        
        This label is created on first access and automatically updates to show
        the formatted text of the current selection.
        
        Returns
        -------
        ControlledQLabel
            A label widget showing the current selected key.
        
        Notes
        -----
        The label is created lazily on first access and is not part of the default
        widget set returned by `all_widgets_as_frame()`.
        """
        if not hasattr(self, "_label"):
            self._label = ControlledQLabel(self)
        return self._label

    ###########################################################################
    # Dict-like interface
    ###########################################################################

    def __getitem__(self, key: K) -> V:
        """
        Get a value from the dictionary.
        
        Parameters
        ----------
        key : K
            The key to look up.
        
        Returns
        -------
        V
            The value associated with the key.
        
        Raises
        ------
        KeyError
            If the key is not in the dictionary.
        
        Examples
        --------
        >>> value = controller["apple"]
        """
        return self.dict_value[key]

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set a value in the dictionary.
        
        Parameters
        ----------
        key : K
            The key to set.
        value : V
            The value to associate with the key.
        
        Examples
        --------
        >>> controller["apple"] = "red"
        """
        current_dict = self.dict_value.copy()
        current_dict[key] = value
        self.dict_value = current_dict

    def __delitem__(self, key: K) -> None:
        """
        Delete a key from the dictionary.
        
        Parameters
        ----------
        key : K
            The key to delete.
        
        Raises
        ------
        KeyError
            If the key is not in the dictionary.
        ValueError
            If the key being deleted is currently the selected_key.
            You must select a different key first.
        ValueError
            If deleting this key would leave the dictionary empty.
        
        Examples
        --------
        >>> del controller["apple"]
        """
        if self.selected_key == key:
            raise ValueError(f"Cannot delete key '{key}' because it is currently selected. Select a different key first.")
        
        current_dict = self.dict_value.copy()
        del current_dict[key]
        
        if not current_dict:
            raise ValueError(f"Cannot delete key '{key}' because it would leave the dictionary empty.")
        
        self.dict_value = current_dict

    def __contains__(self, key: K) -> bool:
        """
        Check if a key is in the dictionary.
        
        Parameters
        ----------
        key : K
            The key to check.
        
        Returns
        -------
        bool
            True if the key is in the dictionary, False otherwise.
        
        Examples
        --------
        >>> if "apple" in controller:
        ...     print("Apple is in the dictionary")
        """
        return key in self.dict_value

    def __len__(self) -> int:
        """
        Get the number of items in the dictionary.
        
        Returns
        -------
        int
            The number of key-value pairs in the dictionary.
        
        Examples
        --------
        >>> count = len(controller)
        """
        return len(self.dict_value)

    def keys(self) -> set[K]:
        """
        Get all keys in the dictionary.
        
        Returns
        -------
        set[K]
            A set of all keys in the dictionary.
        
        Examples
        --------
        >>> all_keys = controller.keys()
        """
        return set(self.dict_value.keys())

    def values(self) -> list[V]:
        """
        Get all values in the dictionary.
        
        Returns
        -------
        list[V]
            A list of all values in the dictionary.
        
        Examples
        --------
        >>> all_values = controller.values()
        """
        return list(self.dict_value.values())

    def items(self) -> list[tuple[K, V]]:
        """
        Get all key-value pairs in the dictionary.
        
        Returns
        -------
        list[tuple[K, V]]
            A list of (key, value) tuples.
        
        Examples
        --------
        >>> all_items = controller.items()
        """
        return list(self.dict_value.items())

    def get(self, key: K, default: V | None = None) -> V | None:
        """
        Get a value from the dictionary with a default.
        
        Parameters
        ----------
        key : K
            The key to look up.
        default : V | None, optional
            The default value to return if the key is not found. Defaults to None.
        
        Returns
        -------
        V | None
            The value associated with the key, or the default if the key is not found.
        
        Examples
        --------
        >>> value = controller.get("apple", "unknown")
        """
        return self.dict_value.get(key, default)

    def pop(self, key: K, default: V | None = None) -> V | None:
        """
        Remove and return a value from the dictionary.
        
        Parameters
        ----------
        key : K
            The key to remove.
        default : V | None, optional
            The default value to return if the key is not found. Defaults to None.
        
        Returns
        -------
        V | None
            The value that was removed, or the default if the key was not found.
        
        Raises
        ------
        ValueError
            If the key being removed is currently the selected_key.
            You must select a different key first.
        ValueError
            If removing this key would leave the dictionary empty.
        
        Examples
        --------
        >>> value = controller.pop("apple", "unknown")
        """
        if key in self.dict_value:
            if self.selected_key == key:
                raise ValueError(f"Cannot pop key '{key}' because it is currently selected. Select a different key first.")
            
            current_dict = self.dict_value.copy()
            if len(current_dict) == 1:
                raise ValueError(f"Cannot pop key '{key}' because it would leave the dictionary empty.")
        
        current_dict = self.dict_value.copy()
        result = current_dict.pop(key, default)
        self.dict_value = current_dict
        return result

    def update(self, other: dict[K, V] | Mapping[K, V]) -> None:
        """
        Update the dictionary with key-value pairs from another dictionary.
        
        Parameters
        ----------
        other : dict[K, V] | Mapping[K, V]
            Another dictionary or mapping to update from.
        
        Examples
        --------
        >>> controller.update({"grape": "purple", "orange": "orange"})
        """
        current_dict = self.dict_value.copy()
        current_dict.update(other)
        self.dict_value = current_dict

    def copy(self) -> dict[K, V]:
        """
        Create a shallow copy of the dictionary.
        
        Returns
        -------
        dict[K, V]
            A shallow copy of the dictionary.
        
        Examples
        --------
        >>> dict_copy = controller.copy()
        """
        return self.dict_value.copy()

