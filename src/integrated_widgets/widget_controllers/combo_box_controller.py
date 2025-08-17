from __future__ import annotations

from typing import Generic, Optional, TypeVar, overload, Callable, Any, Mapping

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import CarriesDistinctSingleValueHook, CarriesDistinctSetHook, InitialSyncMode, ObservableSelectionOptionLike, HookLike
from integrated_widgets.guarded_widgets import GuardedComboBox


T = TypeVar("T")


class ComboBoxController(
    BaseObservableController, 
    ObservableSelectionOptionLike[T], 
    Generic[T]
):
    """ComboBox controller that implements selection option hooks.

    Similar to ObservableSelectionOption, this controller manages both
    a selected value and available options through hooks.
    """

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"selected_option", "available_options"}

    @overload
    def __init__(
        self,
        selected_option: Optional[T],
        *,
        available_options: set[T],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_option: Optional[T],
        *,
        available_options: CarriesDistinctSetHook[T]|HookLike[set[T]],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_option: CarriesDistinctSingleValueHook[T]|HookLike[Optional[T]],
        *,
        available_options: set[T],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_option: CarriesDistinctSingleValueHook[T],
        *,
        available_options: CarriesDistinctSetHook[T]|HookLike[set[T]],
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        selected_option,
        *,
        available_options,
        allow_none: bool = True,
        formatter: Optional[Callable[[T], str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:

        self._formatter = formatter
        self._allow_none = allow_none
        
        # Handle different types of selected_value and options
        if selected_option is None:
            initial_selected_option: Optional[T] = None
            selected_option_hook: Optional[HookLike[Optional[T]]] = None
        elif isinstance(selected_option, HookLike):
            # It's a hook - set it and get initial value
            initial_selected_option = selected_option.value # type: ignore
            selected_option_hook: Optional[HookLike[Optional[T]]] = selected_option
        elif isinstance(selected_option, CarriesDistinctSingleValueHook):
            initial_selected_option: Optional[T] = selected_option.distinct_single_value_reference
            selected_option_hook: Optional[HookLike[Optional[T]]] = selected_option.distinct_single_value_hook
        else:
            initial_selected_option = selected_option
            selected_option_hook: Optional[HookLike[Optional[T]]] = None
        
        if isinstance(available_options, CarriesDistinctSetHook):
            initial_available_options: set[T] = available_options.distinct_set_reference    
            available_options_hook: Optional[HookLike[set[T]]] = available_options.distinct_set_hook
        elif isinstance(available_options, HookLike):
            initial_available_options: set[T] = available_options.value # type: ignore
            available_options_hook: Optional[HookLike[set[T]]] = available_options
        elif isinstance(available_options, set):
            initial_available_options: set[T] = available_options
            available_options_hook: Optional[HookLike[set[T]]] = None
        else:
            raise ValueError(f"Invalid available options: {available_options}")
        
        if not allow_none and (initial_selected_option is None or initial_available_options == set()):
            raise ValueError("Selected option is None but allow_none is False")
        
        if initial_selected_option is not None and initial_selected_option not in initial_available_options:
            raise ValueError(f"Selected option {initial_selected_option} not in options {initial_available_options}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys
            current_selected = x.get("selected_option", initial_selected_option)
            current_options = x.get("available_options", initial_available_options)
            
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
            {"selected_option": initial_selected_option, "available_options": initial_available_options},
            verification_method=verification_method,
        )

        if available_options_hook is not None:
            self.bind_available_options_to(available_options_hook)
            
        if selected_option_hook is not None:
            self.bind_selected_option_to(selected_option_hook)

    ###########################################################################
    # Public API
    ###########################################################################

    def bind_available_options_to(self, observable_or_hook: CarriesDistinctSetHook[T] | HookLike[set[T]], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """
        Establish a bidirectional binding for the options set with another observable.
        
        Args:
            hook: The observable to bind the options to
            initial_sync_mode: How to synchronize values initially
        """
        if isinstance(observable_or_hook, CarriesDistinctSetHook):
            observable_or_hook = observable_or_hook.distinct_set_hook
        self.distinct_set_hook.connect_to(observable_or_hook, initial_sync_mode)

    def bind_selected_option_to(self, observable_or_hook: CarriesDistinctSingleValueHook[Optional[T]] | HookLike[Optional[T]], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """
        Establish a bidirectional binding for the selected option with another observable.
        
        Args:
            hook: The observable to bind the selected option to
            initial_sync_mode: How to synchronize values initially
        """

        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        self.distinct_single_value_hook.connect_to(observable_or_hook, initial_sync_mode)

    def bind_to(self, observable: ObservableSelectionOptionLike[T], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:

        obs: ObservableSelectionOptionLike[T] = observable  # type: ignore

        # First, synchronize the values atomically to maintain consistency
        if initial_sync_mode == InitialSyncMode.SELF_IS_UPDATED:
            self.set_selected_option_and_available_options(
                obs.selected_option, 
                obs.available_options
            )
        elif initial_sync_mode == InitialSyncMode.SELF_UPDATES:
            obs.set_selected_option_and_available_options(
                self.selected_option, 
                self.available_options
            )

        # Then, establish the bindings with UPDATE_SELF_FROM_OBSERVABLE mode
        # to ensure this observable gets updated from the other one
        self.distinct_set_hook.connect_to(obs.distinct_set_hook, InitialSyncMode.SELF_IS_UPDATED)
        self.distinct_single_value_hook.connect_to(obs.distinct_single_value_hook, InitialSyncMode.SELF_IS_UPDATED)

    def detach(self) -> None:
        """Detach the combo box from the observable."""

        self.distinct_single_value_hook.detach()
        self.distinct_set_hook.detach()

    ###########################################################################
    # Hook Implementation
    ###########################################################################


    @property
    def distinct_single_value_hook(self) -> HookLike[Optional[T]]:
        """Get the hook for the single value."""
        return self._component_hooks["selected_option"]
    
    @property
    def distinct_single_value_reference(self) -> Optional[T]:
        """Get the reference for the single value."""
        return self._component_values["selected_option"]
    
    @property
    def distinct_set_hook(self) -> HookLike[set[T]]:
        """Get the hook for the set value."""
        return self._component_hooks["available_options"]
    
    @property
    def distinct_set_reference(self) -> set[T]:
        """Get the reference for the set value."""
        return self._component_values["available_options"]

    ###########################################################################
    # Public API (similar to ObservableSelectionOption)
    ###########################################################################

    @property
    def selected_option(self) -> Optional[T]:
        """Get the currently selected option."""
        return self.distinct_single_value_reference

    @selected_option.setter
    def selected_option(self, value: Optional[T]) -> None:
        """Set the selected option."""
        self._set_component_values(
            {"selected_option": value},
            notify_binding_system=True
        )

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        return self.distinct_set_reference

    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        self._set_component_values(
            {"available_options": options},
            notify_binding_system=True
        )

    @property
    def is_none_selection_allowed(self) -> bool:
        """Check if None selection is allowed."""
        return self._allow_none

    def set_selected_option_and_available_options(
        self, 
        selected_option: Optional[T], 
        available_options: set[T]
    ) -> None:
        """Set both selected option and available options at once."""
        self._set_component_values(
            {"selected_option": selected_option, "available_options": available_options},
            notify_binding_system=True
        )

    ###########################################################################
    # Widget Management
    ###########################################################################

    def initialize_widgets(self) -> None:
        """Initialize the combo box widget."""
        self._combobox = GuardedComboBox(self)
        self._combobox.currentIndexChanged.connect(lambda _i: self._on_changed())

    def update_widgets_from_component_values(self) -> None:
        """Update the combo box from the component values."""
        if not hasattr(self, '_combobox'):
            return
            
        # Use internal update context to allow widget modifications
        self._internal_widget_update = True
        try:
            self._combobox.clear()
            
            # Only show placeholder for None when allow_none is True
            if self._allow_none:
                self._combobox.addItem("", None)
            
            # Add all other options
            for opt in sorted(self.distinct_set_reference, key=lambda x: str(x) if x is not None else ""):
                if opt is not None:  # Skip None as it's already added
                    label = self._formatter(opt) if self._formatter is not None else str(opt)
                    self._combobox.addItem(label, userData=opt)
            
            # Select the current value
            if self.distinct_single_value_reference is None:
                self._combobox.setCurrentIndex(0 if self._allow_none else -1)
            else:
                for i in range(self._combobox.count()):
                    if self._combobox.itemData(i) == self.distinct_single_value_reference:
                        self._combobox.setCurrentIndex(i)
                        break
        finally:
            self._internal_widget_update = False

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the combo box."""
        idx = self._combobox.currentIndex()
        if idx < 0:
            return
        
        value = self._combobox.itemData(idx)
        # Treat empty string entry as None only when None is allowed
        if value is None and self._allow_none:
            self._set_component_values(
                {"selected_option": None},
                notify_binding_system=True
            )
        else:
            self._set_component_values(
                {"selected_option": value},
                notify_binding_system=True
            )

    def _on_changed(self) -> None:
        """Handle combo box selection change."""
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    ###########################################################################
    # Public Widget Access
    ###########################################################################

    @property
    def widget_combobox(self) -> GuardedComboBox:
        """Get the combo box widget."""
        return self._combobox

    @property
    def owner_widget(self) -> QWidget:
        """Get the owner widget for child widgets."""
        return self._owner_widget


