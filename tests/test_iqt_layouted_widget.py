"""
Tests for IQtLayoutedWidget - demonstrating composition of IQt widgets.

This test shows how users can create custom composite widgets by combining
existing IQt widgets using layout strategies.
"""

import sys
from dataclasses import dataclass

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox
from observables import FloatingHook

# Ensure QApplication exists before importing widgets
app = QApplication.instance() or QApplication(sys.argv)

from integrated_widgets.iqt_widgets.iqt_layouted_widget import IQtLayoutedWidget
from integrated_widgets.iqt_widgets.layout_payload import BaseLayoutPayload
from integrated_widgets.iqt_widgets.iqt_integer_entry import IQtIntegerEntry
from integrated_widgets.iqt_widgets.iqt_text_entry import IQtTextEntry
from integrated_widgets.iqt_widgets.iqt_check_box import IQtCheckBox
from integrated_widgets.iqt_widgets.iqt_selection_option import IQtSelectionOption


class TestIQtLayoutedWidget:
    """Tests for IQtLayoutedWidget demonstrating user composition patterns."""
    
    def test_simple_vertical_composition(self):
        """Test composing multiple IQt widgets vertically."""
        
        # Create payload with multiple IQt widgets
        @dataclass(frozen=True)
        class FormPayload(BaseLayoutPayload):
            name_entry: QWidget
            age_entry: QWidget
            active_checkbox: QWidget
        
        # Create the widgets
        name_widget = IQtTextEntry("John Doe")
        age_widget = IQtIntegerEntry(25)
        active_widget = IQtCheckBox(True, text="Active")
        
        # Create payload
        payload = FormPayload(
            name_entry=name_widget,
            age_entry=age_widget,
            active_checkbox=active_widget
        )
        
        # Define vertical layout strategy
        def vertical_layout(parent: QWidget, payload: FormPayload) -> QWidget:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(payload.name_entry)
            layout.addWidget(payload.age_entry)
            layout.addWidget(payload.active_checkbox)
            return widget
        
        # Create composite widget
        composite = IQtLayoutedWidget(payload, vertical_layout)
        
        # Verify structure
        assert composite._payload == payload # type: ignore
        assert composite._content_root is not None # type: ignore
        assert len(payload.registered_widgets) == 3
        
        # Verify we can access the hooks
        assert name_widget.get_value_of_hook("value") == "John Doe"
        assert age_widget.get_value_of_hook("value") == 25
        assert active_widget.get_value_of_hook("value") is True
        
        # Cleanup
        del composite
    
    def test_horizontal_composition(self):
        """Test composing widgets horizontally."""
        
        @dataclass(frozen=True)
        class ButtonRowPayload(BaseLayoutPayload):
            button1: QWidget
            button2: QWidget
            button3: QWidget
        
        # Create checkboxes
        btn1 = IQtCheckBox(False, text="Option 1")
        btn2 = IQtCheckBox(True, text="Option 2")
        btn3 = IQtCheckBox(False, text="Option 3")
        
        payload = ButtonRowPayload(btn1, btn2, btn3)
        
        def horizontal_layout(parent: QWidget, payload: ButtonRowPayload) -> QWidget:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(payload.button1)
            layout.addWidget(payload.button2)
            layout.addWidget(payload.button3)
            return widget
        
        composite = IQtLayoutedWidget(payload, horizontal_layout)
        
        assert len(payload.registered_widgets) == 3
        assert btn2.get_value_of_hook("value") is True
        
        del composite
    
    def test_grouped_layout_with_title(self):
        """Test using QGroupBox for a titled group of widgets."""
        
        @dataclass(frozen=True)
        class SettingsPayload(BaseLayoutPayload):
            port_entry: QWidget
            timeout_entry: QWidget
            debug_checkbox: QWidget
        
        port = IQtIntegerEntry(8080)
        timeout = IQtIntegerEntry(30)
        debug = IQtCheckBox(False, text="Enable Debug Mode")
        
        payload = SettingsPayload(port, timeout, debug)
        
        def grouped_layout(parent: QWidget, payload: SettingsPayload) -> QWidget:
            # Use QGroupBox for a titled container
            group = QGroupBox("Server Settings")
            layout = QVBoxLayout(group)
            layout.addWidget(payload.port_entry)
            layout.addWidget(payload.timeout_entry)
            layout.addWidget(payload.debug_checkbox)
            return group
        
        composite = IQtLayoutedWidget(payload, grouped_layout)
        
        # Verify content_root is the QGroupBox
        assert isinstance(composite._content_root, QGroupBox) # type: ignore
        assert composite._content_root.title() == "Server Settings" # type: ignore
        
        del composite
    
    def test_dynamic_layout_switching(self):
        """Test switching between different layout strategies dynamically."""
        
        @dataclass(frozen=True)
        class DynamicPayload(BaseLayoutPayload):
            widget1: QWidget
            widget2: QWidget
        
        w1 = IQtTextEntry("First")
        w2 = IQtTextEntry("Second")
        payload = DynamicPayload(w1, w2)
        
        def vertical_strategy(parent: QWidget, payload: DynamicPayload) -> QWidget:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(payload.widget1)
            layout.addWidget(payload.widget2)
            return widget
        
        def horizontal_strategy(parent: QWidget, payload: DynamicPayload) -> QWidget:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(payload.widget1)
            layout.addWidget(payload.widget2)
            return widget
        
        # Create with vertical layout
        composite = IQtLayoutedWidget(payload, vertical_strategy)
        
        # Widgets should work
        assert w1.get_value_of_hook("value") == "First"
        
        # Switch to horizontal layout
        composite.set_layout_strategy(horizontal_strategy) # type: ignore
        
        # Widgets should still work (not deleted)
        assert w1.get_value_of_hook("value") == "First"
        assert w2.get_value_of_hook("value") == "Second"
        
        del composite
    
    def test_deferred_layout_setup(self):
        """Test creating widget without layout, then setting it later."""
        
        @dataclass(frozen=True)
        class SimplePayload(BaseLayoutPayload):
            entry: QWidget
        
        entry = IQtIntegerEntry(100)
        payload = SimplePayload(entry)
        
        # Create widget WITHOUT layout strategy
        composite = IQtLayoutedWidget(payload)
        
        # Widget should be empty (no content_root yet)
        assert composite._content_root is None # type: ignore
        
        # Widget functionality still works
        assert entry.get_value_of_hook("value") == 100
        
        # Now set the layout
        def simple_layout(parent: QWidget, payload: SimplePayload) -> QWidget:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(payload.entry)
            return widget
        
        composite.set_layout_strategy(simple_layout) # type: ignore
        
        # Now content should exist
        assert composite._content_root is not None # type: ignore
        assert entry.get_value_of_hook("value") == 100
        
        del composite
    
    def test_complex_nested_composition(self):
        """Test creating complex nested widget compositions."""
        
        @dataclass(frozen=True)
        class PersonFormPayload(BaseLayoutPayload):
            name: QWidget
            age: QWidget
            city: QWidget
        
        # Create person form widgets
        name = IQtTextEntry("Alice")
        age = IQtIntegerEntry(30)
        city = IQtSelectionOption(
            selected_option="New York",
            available_options={"New York", "London", "Tokyo"}
        )
        
        person_payload = PersonFormPayload(name, age, city)
        
        def person_form_layout(parent: QWidget, payload: PersonFormPayload) -> QWidget:
            group = QGroupBox("Person Information")
            layout = QVBoxLayout(group)
            layout.addWidget(payload.name)
            layout.addWidget(payload.age)
            layout.addWidget(payload.city)
            return group
        
        person_form = IQtLayoutedWidget(person_payload, person_form_layout)
        
        # Verify all hooks work
        assert name.get_value_of_hook("value") == "Alice"
        assert age.get_value_of_hook("value") == 30
        assert city.get_value_of_hook("selected_option") == "New York"
        
        # Now compose the form with other widgets in another layout
        @dataclass(frozen=True)
        class ApplicationPayload(BaseLayoutPayload):
            form: QWidget
            submit_button: QWidget
        
        submit_btn = IQtCheckBox(False, text="Submit")
        app_payload = ApplicationPayload(person_form, submit_btn)
        
        def app_layout(parent: QWidget, payload: ApplicationPayload) -> QWidget:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(payload.form)
            layout.addWidget(payload.submit_button)
            return widget
        
        application = IQtLayoutedWidget(app_payload, app_layout)
        
        # Verify nested access still works
        assert name.get_value_of_hook("value") == "Alice"
        
        del application, person_form
    
    def test_with_observable_hooks(self):
        """Test that composed widgets with hooks work correctly."""
        
        @dataclass(frozen=True)
        class HookedPayload(BaseLayoutPayload):
            entry1: QWidget
            entry2: QWidget

        # Create shared hook
        shared_value: FloatingHook[int] = FloatingHook(42)
        
        # Create two widgets sharing the same hook
        entry1 = IQtIntegerEntry(shared_value)
        entry2 = IQtIntegerEntry(shared_value)
        
        payload = HookedPayload(entry1, entry2)
        
        def side_by_side(parent: QWidget, payload: HookedPayload) -> QWidget:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(payload.entry1)
            layout.addWidget(payload.entry2)
            return widget
        
        composite = IQtLayoutedWidget(payload, side_by_side)
        
        # Both should show same initial value (connected to same underlying hook)
        assert entry1.get_value_of_hook("value") == 42
        assert entry2.get_value_of_hook("value") == 42
        
        # Both widgets are functional in the composite
        assert composite._content_root is not None # type: ignore
        assert len(payload.registered_widgets) == 2
        
        del composite
    
    def test_payload_validation_rejects_non_widgets(self):
        """Test that payload validation prevents non-QWidget fields."""
        
        @dataclass(frozen=True)
        class BadPayload(BaseLayoutPayload):
            widget: QWidget
            not_a_widget: str  # This should fail validation
        
        entry = IQtTextEntry("Test")
        
        try:
            # This should raise ValueError
            payload = BadPayload(entry, "not a widget")  # type: ignore
            assert False, "Should have raised ValueError for non-QWidget field"
        except ValueError as e:
            assert "must be a QWidget" in str(e)
            assert "not_a_widget" in str(e)
    
    def test_multiple_instances_with_same_payload_type(self):
        """Test creating multiple widget instances with same payload structure."""
        
        @dataclass(frozen=True)
        class TwoEntryPayload(BaseLayoutPayload):
            left: QWidget
            right: QWidget
        
        def horizontal(parent: QWidget, payload: TwoEntryPayload) -> QWidget:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(payload.left)
            layout.addWidget(payload.right)
            return widget
        
        # Create multiple instances
        payload1 = TwoEntryPayload(IQtIntegerEntry(1), IQtIntegerEntry(2))
        payload2 = TwoEntryPayload(IQtIntegerEntry(10), IQtIntegerEntry(20))
        
        composite1 = IQtLayoutedWidget(payload1, horizontal)
        composite2 = IQtLayoutedWidget(payload2, horizontal)
        
        # Verify independent state
        assert payload1.left.get_value_of_hook("value") == 1 # type: ignore
        assert payload2.left.get_value_of_hook("value") == 10 # type: ignore
        
        del composite1, composite2
    
    def test_real_world_settings_panel(self):
        """Test a real-world example: creating a settings panel."""
        
        @dataclass(frozen=True)
        class SettingsPanelPayload(BaseLayoutPayload):
            server_url: QWidget
            port: QWidget
            timeout: QWidget
            use_ssl: QWidget
            auto_reconnect: QWidget
        
        # Create individual settings widgets
        server_url = IQtTextEntry("localhost")
        port = IQtIntegerEntry(8080)
        timeout = IQtIntegerEntry(30)
        use_ssl = IQtCheckBox(True, text="Use SSL")
        auto_reconnect = IQtCheckBox(True, text="Auto-reconnect")
        
        payload = SettingsPanelPayload(
            server_url=server_url,
            port=port,
            timeout=timeout,
            use_ssl=use_ssl,
            auto_reconnect=auto_reconnect
        )
        
        # Define a professional-looking layout strategy
        def settings_layout(parent: QWidget, payload: SettingsPanelPayload) -> QWidget:
            group = QGroupBox("Connection Settings")
            main_layout = QVBoxLayout(group)
            
            # Server settings in one row
            server_row = QWidget()
            server_layout = QHBoxLayout(server_row)
            server_layout.addWidget(payload.server_url, 3)  # More space for URL
            server_layout.addWidget(payload.port, 1)
            main_layout.addWidget(server_row)
            
            # Timeout
            main_layout.addWidget(payload.timeout)
            
            # Checkboxes
            main_layout.addWidget(payload.use_ssl)
            main_layout.addWidget(payload.auto_reconnect)
            
            return group
        
        # Create the settings panel
        settings_panel = IQtLayoutedWidget(payload, settings_layout)
        
        # Verify all settings are accessible
        assert server_url.get_value_of_hook("value") == "localhost"
        assert port.get_value_of_hook("value") == 8080
        assert timeout.get_value_of_hook("value") == 30
        assert use_ssl.get_value_of_hook("value") is True
        assert auto_reconnect.get_value_of_hook("value") is True
        
        # Verify payload has all 5 widgets registered
        assert len(payload.registered_widgets) == 5
        
        del settings_panel
    
    def test_strategy_switching_preserves_widget_state(self):
        """Test that switching layouts preserves widgets (they're not deleted)."""
        
        @dataclass(frozen=True)
        class SwitchablePayload(BaseLayoutPayload):
            entry: QWidget
            checkbox: QWidget
        
        entry = IQtIntegerEntry(42)
        checkbox = IQtCheckBox(True, text="Enabled")
        payload = SwitchablePayload(entry, checkbox)
        
        def compact_layout(parent: QWidget, payload: SwitchablePayload) -> QWidget:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(payload.entry)
            layout.addWidget(payload.checkbox)
            return widget
        
        def expanded_layout(parent: QWidget, payload: SwitchablePayload) -> QWidget:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(payload.entry)
            layout.addWidget(payload.checkbox)
            return widget
        
        # Create with compact layout
        composite = IQtLayoutedWidget(payload, compact_layout)
        
        # Capture initial state
        initial_entry_value = entry.get_value_of_hook("value")
        initial_checkbox_value = checkbox.get_value_of_hook("value")
        
        # Switch to expanded layout
        composite.set_layout_strategy(expanded_layout) # type: ignore
        
        # Widgets should still exist and have same values
        assert entry.get_value_of_hook("value") == initial_entry_value
        assert checkbox.get_value_of_hook("value") == initial_checkbox_value
        
        # Switch back
        composite.set_layout_strategy(compact_layout) # type: ignore
        
        # Still working
        assert entry.get_value_of_hook("value") == initial_entry_value
        assert checkbox.get_value_of_hook("value") == initial_checkbox_value
        
        del composite
    
    def test_custom_payload_with_non_widget_data(self):
        """Test payload with both widgets and metadata (widgets must be QWidget fields)."""
        
        # Note: Only QWidget fields are validated and registered
        # Non-widget fields can exist but won't be managed
        @dataclass(frozen=True)
        class WidgetOnlyPayload(BaseLayoutPayload):
            title_widget: QWidget
            value_widget: QWidget
        
        title = IQtTextEntry("Title")
        value = IQtIntegerEntry(123)
        
        payload = WidgetOnlyPayload(title, value)
        
        def simple_layout(parent: QWidget, payload: WidgetOnlyPayload) -> QWidget:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(payload.title_widget)
            layout.addWidget(payload.value_widget)
            return widget
        
        composite = IQtLayoutedWidget(payload, simple_layout)
        
        # Only QWidget fields are registered
        assert len(payload.registered_widgets) == 2
        
        del composite
    
    def test_reusable_layout_strategies(self):
        """Test that layout strategies can be reused across different payloads."""
        
        # Generic vertical layout strategy
        def vertical_two_widgets(parent: QWidget, payload: BaseLayoutPayload) -> QWidget:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            # Use registered_widgets to handle any payload with 2 widgets
            widgets = list(payload.registered_widgets)
            for w in sorted(widgets, key=lambda x: str(x)):  # Sort for consistency
                layout.addWidget(w)
            return widget
        
        # Create different payloads
        @dataclass(frozen=True)
        class Payload1(BaseLayoutPayload):
            a: QWidget
            b: QWidget
        
        @dataclass(frozen=True)
        class Payload2(BaseLayoutPayload):
            x: QWidget
            y: QWidget
        
        p1 = Payload1(IQtIntegerEntry(1), IQtIntegerEntry(2))
        p2 = Payload2(IQtTextEntry("Hello"), IQtTextEntry("World"))
        
        # Reuse same strategy
        c1 = IQtLayoutedWidget(p1, vertical_two_widgets)
        c2 = IQtLayoutedWidget(p2, vertical_two_widgets)
        
        assert c1._content_root is not None # type: ignore
        assert c2._content_root is not None # type: ignore
        
        del c1, c2


def run_tests():
    """Run all tests."""
    test_instance = TestIQtLayoutedWidget()
    
    tests = [
        ("Simple vertical composition", test_instance.test_simple_vertical_composition),
        ("Horizontal composition", test_instance.test_horizontal_composition),
        ("Grouped layout with title", test_instance.test_grouped_layout_with_title),
        ("Dynamic layout switching", test_instance.test_dynamic_layout_switching),
        ("Deferred layout setup", test_instance.test_deferred_layout_setup),
        ("Complex nested composition", test_instance.test_complex_nested_composition),
        ("Strategy switching preserves state", test_instance.test_strategy_switching_preserves_widget_state),
        ("Payload validation rejects non-widgets", test_instance.test_payload_validation_rejects_non_widgets),
        ("Multiple instances with same payload type", test_instance.test_multiple_instances_with_same_payload_type),
        ("Reusable layout strategies", test_instance.test_reusable_layout_strategies),
    ]
    
    passed = 0
    failed = 0
    
    print("="*70)
    print("IQtLayoutedWidget - User Composition Pattern Tests")
    print("="*70)
    print()
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ PASS: {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {name}")
            print(f"   {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   {type(e).__name__}: {e}")
            failed += 1
    
    print()
    print("="*70)
    print(f"Results: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} test(s) failed")
    print("="*70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())

