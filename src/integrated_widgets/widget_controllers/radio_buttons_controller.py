from __future__ import annotations

from typing import Callable, Optional, TypeVar, overload, Generic, Any, Mapping

from PySide6.QtWidgets import QWidget, QButtonGroup

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSelectionOptionLike, Hook, SyncMode, CarriesDistinctSingleValueHook, CarriesDistinctSetHook, HookLike
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
        selected_value: T,
        *,
        available_options: set[T],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_value: T,
        *,
        available_options: CarriesDistinctSetHook[T],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_value: CarriesDistinctSingleValueHook[T],
        *,
        available_options: set[T],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_value: CarriesDistinctSingleValueHook[T],
        *,
        available_options: CarriesDistinctSetHook[T],
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        selected_value,
        *,
        available_options,
        formatter: Callable[[T], str] = DEFAULT_FORMATTER,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        self._formatter = formatter
        
        # Handle different types of selected_value and available_options
        if hasattr(selected_value, '_get_single_value'):
            # It's a hook - get initial value
            initial_selected_option = selected_value._get_single_value()
            selected_option_hook = selected_value
        else:
            # It's a direct value
            initial_selected_option = selected_value
            selected_option_hook = None
        
        if hasattr(available_options, '_get_set'):
            # It's a hook - get initial value
            available_options_set = available_options._get_set()
            available_options_hook = available_options
        else:
            # It's a direct set
            available_options_set = set(available_options) if available_options else set()
            available_options_hook = None
        
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
            {
                "selected_option": initial_selected_option,
                "available_options": available_options_set
            },
            {
                "selected_option": Hook(self, self._get_single_value, self._set_single_value),
                "available_options": Hook(self, self._get_set_value, self._set_set_value)
            },
            verification_method=verification_method,
            parent=parent
        )
        
        if available_options_hook is not None:
            self.bind_available_options_to_observable(available_options_hook)
            
        if selected_option_hook is not None:
            self.bind_selected_option_to_observable(selected_option_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_selected_option_to_observable(self, observable_or_hook: CarriesDistinctSingleValueHook[Optional[T]]|HookLike[Optional[T]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding for the options set with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().establish_binding(observable_or_hook, initial_sync_mode)

    def bind_available_options_to_observable(self, observable_or_hook: CarriesDistinctSetHook[T]|HookLike[set[T]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding for the selected option with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSetHook):
            observable_or_hook = observable_or_hook._get_set_hook()
        self._get_set_hook().establish_binding(observable_or_hook, initial_sync_mode)

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    def _get_single_value(self) -> T:
        """Get the currently selected value."""
        return self._get_component_value("selected_option")

    def _get_single_value_hook(self) -> HookLike[Optional[T]]:
        """Get self as a hook for binding."""
        return self._component_hooks["selected_option"]

    def _set_single_value(self, value: T) -> None:
        """Set the selected value."""
        if value not in self._get_set_value():
            raise ValueError(f"Value {value} is not in available options")
        self._set_component_value("selected_option", value)

    def _get_set_hook(self) -> HookLike[set[T]]:
        """Get self as a set hook for binding."""
        return self._component_hooks["available_options"]
    def _get_set_value(self) -> set[T]:
        """Get the set of available options from component values."""
        return self._get_component_value("available_options")

    def _set_set_value(self, value: set[T]) -> None:
        """Set the set of available options in component values."""
        self._set_component_value("available_options", value)

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
        available_options = self._get_set_value()
        if len(self._buttons) != len(available_options):
            self._rebuild_buttons()
        
        # set checked
        selected_value = self._get_single_value()
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
                self._set_single_value(value)
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
        available_options = self._get_set_value()
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

    @property
    def selected_option(self) -> T:
        """Get the currently selected option."""
        return self._get_single_value()

    @selected_option.setter
    def selected_option(self, value: T) -> None:
        """Set the selected option."""
        self._set_single_value(value)

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        return self._get_set_value().copy()

    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        self._set_set_value(options)

    @property
    def widgets_radio_buttons(self) -> list[GuardedRadioButton]:
        """Get the radio button widgets."""
        return list(self._buttons)


