from __future__ import annotations

from typing import Callable, Optional, TypeVar, overload, Generic, Any, Mapping

from PySide6.QtWidgets import QWidget, QButtonGroup

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSelectionOptionLike, CarriesDistinctSingleValueHook, CarriesDistinctSetHook, HookLike, InitialSyncMode
from integrated_widgets.guarded_widgets import GuardedRadioButton

T = TypeVar("T")
DEFAULT_FORMATTER: Callable[[Any], str] = lambda e: str(e)

class RadioButtonsController(BaseObservableController, ObservableSelectionOptionLike[T], Generic[T]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"selected_option", "available_options"}
    @overload
    def __init__(
        self,
        selected_option: T,
        *,
        available_options: set[T],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_option: T,
        *,
        available_options: CarriesDistinctSetHook[T] | HookLike[set[T]],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_option: CarriesDistinctSingleValueHook[T] | HookLike[T],
        *,
        available_options: set[T],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_option: CarriesDistinctSingleValueHook[T] | HookLike[T],
        *,
        available_options: CarriesDistinctSetHook[T] | HookLike[set[T]],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        selected_option,
        *,
        available_options,
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        self._formatter = formatter
        
        # Handle different types of selected_value and available_options
        if isinstance(selected_option, CarriesDistinctSingleValueHook):
            # It's a hook - get initial value
            initial_selected_option = selected_option.distinct_single_value_reference
            selected_option_hook = selected_option.distinct_single_value_hook
        elif isinstance(selected_option, HookLike):
            # It's a hook - get initial value
            initial_selected_option = selected_option.value # type: ignore
            selected_option_hook = selected_option
        else:
            # It's a direct value
            initial_selected_option = selected_option
            selected_option_hook = None
        
        if isinstance(available_options, CarriesDistinctSetHook):
            # It's a hook - get initial value
            available_options_set = available_options.distinct_set_reference
            available_options_hook = available_options.distinct_set_hook
        elif isinstance(available_options, HookLike):
            # It's a hook - get initial value
            available_options_set = available_options.value # type: ignore
            available_options_hook = available_options
        elif isinstance(available_options, set):
            # It's a direct set
            available_options_set = set(available_options) if available_options else set()
            available_options_hook = None
        else:
            raise ValueError(f"Invalid available_options: {available_options}")
        
        if initial_selected_option not in available_options_set:
            raise ValueError(f"Selected option {initial_selected_option} not in available options {available_options_set}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys
            current_selected = x.get("selected_option", initial_selected_option)
            current_options = x.get("available_options", available_options_set)
            
            if current_options is not None and not isinstance(current_options, set):
                return False, "Available options is not a set"
            
            if current_selected is not None and current_options is not None and current_selected not in current_options:
                return False, f"Selected option {current_selected} not in available options {current_options}"
            
            if not current_options:
                return False, "Available options set is empty"

            return True, "Verification method passed"

        super().__init__(
            {"selected_option": initial_selected_option, "available_options": available_options_set},
            verification_method=verification_method,
            parent=parent
        )
        
        if available_options_hook is not None:
            self.bind_available_options_to(available_options_hook)
            
        if selected_option_hook is not None:
            self.bind_selected_option_to(selected_option_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_selected_option_to(self, observable_or_hook: CarriesDistinctSingleValueHook[T]|HookLike[T], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding for the options set with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        self.distinct_single_value_hook.connect_to(observable_or_hook, initial_sync_mode)

    def bind_available_options_to(self, observable_or_hook: CarriesDistinctSetHook[T]|HookLike[set[T]], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding for the selected option with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSetHook):
            observable_or_hook = observable_or_hook.distinct_set_hook
        self.distinct_set_hook.connect_to(observable_or_hook, initial_sync_mode)

    def bind_to(self, observable: ObservableSelectionOptionLike[T], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding with another observable."""

        if initial_sync_mode == InitialSyncMode.SELF_IS_UPDATED:
            selected_option = observable.selected_option
            if selected_option is None:
                raise ValueError("Selected option is None")
            self.set_selected_option_and_available_options(
                selected_option,
                observable.available_options
            )
        elif initial_sync_mode == InitialSyncMode.SELF_UPDATES:
            observable.set_selected_option_and_available_options(
                self.selected_option,
                self.available_options
            )

        self.bind_selected_option_to(observable.distinct_single_value_hook, initial_sync_mode) # type: ignore
        self.bind_available_options_to(observable.distinct_set_hook, initial_sync_mode)

    def detach(self) -> None:
        """Detach the radio buttons controller from the observable."""
        self.distinct_single_value_hook.detach()
        self.distinct_set_hook.detach()

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    @property
    def distinct_single_value_hook(self) -> HookLike[T]:
        """Get the hook for the single value."""
        return self._component_hooks["selected_option"]
    
    @property
    def distinct_single_value_reference(self) -> T:
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



    def initialize_widgets(self) -> None:
        self._group = QButtonGroup(self._owner_widget)
        self._buttons: list[GuardedRadioButton] = []
        self._rebuild_buttons()
        # connect after build
        for btn in self._buttons:
            btn.toggled.connect(self._on_toggled)

    def update_widgets_from_component_values(self) -> None:
        """Update the radio buttons from the component values."""
        if not hasattr(self, '_buttons'):
            return
            
        # ensure buttons match available options
        available_options = self.distinct_set_reference
        if len(self._buttons) != len(available_options):
            self._rebuild_buttons()
        
        # set checked
        selected_value = self.distinct_single_value_reference
        if selected_value is not None:
            for btn in self._buttons:
                if btn.property("value") == selected_value:
                    btn.setChecked(True)
                    break

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the radio buttons."""
        for btn in self._buttons:
            if btn.isChecked():
                value = btn.property("value")
                self._set_component_values(
                    {"selected_option": value},
                    notify_binding_system=True
                )
                break

    ###########################################################################
    # Internal
    ###########################################################################

    def _rebuild_buttons(self) -> None:
        """Rebuild the radio button widgets."""
        # disconnect old
        try:
            for btn in self._buttons:
                btn.toggled.disconnect()
                self._group.removeButton(btn)
                btn.setParent(None)
        except Exception:
            pass
        self._buttons = []
        # build new
        available_options = self.distinct_set_reference
        for member in sorted(available_options, key=lambda m: str(m)):
            btn = GuardedRadioButton(self._owner_widget, self._formatter(member))
            btn.setProperty("value", member)
            self._group.addButton(btn)
            self._buttons.append(btn)

    def _on_toggled(self, checked: bool) -> None:
        """Handle radio button toggle."""
        if not checked or self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    ###########################################################################
    # Disposal
    ###########################################################################
    def dispose_before_children(self) -> None:
        for btn in self._buttons:
            try:
                btn.toggled.disconnect()
            except Exception:
                pass

    ###########################################################################
    # Public API
    ###########################################################################

    def set_selected_option_and_available_options(self, selected_option: T, available_options: set[T]) -> None:
        """Set both selected option and available options at once."""
        self._set_component_values(
            {"selected_option": selected_option, "available_options": available_options},
            notify_binding_system=False
        )

    @property
    def selected_option(self) -> T:
        """Get the currently selected option."""
        return self.distinct_single_value_reference

    @selected_option.setter
    def selected_option(self, value: T) -> None:
        """Set the selected option."""
        self._set_component_values(
            {"selected_option": value},
            notify_binding_system=True
        )

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        return self.distinct_set_reference.copy()

    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        self._set_component_values(
            {"available_options": options},
            notify_binding_system=True
        )

    @property
    def widgets_radio_buttons(self) -> list[GuardedRadioButton]:
        """Get the radio button widgets."""
        return list(self._buttons)


