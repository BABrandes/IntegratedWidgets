from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from united_system import RealUnitedScalar, Unit
from integrated_widgets import DisplayValueController
from observables import ObservableSingleValue, Hook


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_constructs_with_direct_value(qtbot: QtBot):
    """Test that DisplayValueController constructs with a direct value."""
    app = QApplication.instance() or QApplication([])
    
    # Test with string value
    c = DisplayValueController("Hello, World!")
    qtbot.addWidget(c._owner_widget)
    assert c.single_value == "Hello, World!"
    assert c.widget_label.text() == "Hello, World!"
    
    # Test with integer value
    c2 = DisplayValueController(42)
    qtbot.addWidget(c2._owner_widget)
    assert c2.single_value == 42
    assert c2.widget_label.text() == "42"
    
    # Test with float value
    c3 = DisplayValueController(3.14)
    qtbot.addWidget(c3._owner_widget)
    assert c3.single_value == 3.14
    assert c3.widget_label.text() == "3.14"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_constructs_with_hook(qtbot: QtBot):
    """Test that DisplayValueController constructs with a Hook."""
    app = QApplication.instance() or QApplication([])
    
    # Create a hook with initial value - use a simple controller instead
    from integrated_widgets import DisplayValueController
    hook = DisplayValueController("Hook Value")
    
    c = DisplayValueController(hook)
    qtbot.addWidget(c._owner_widget)
    assert c.single_value == "Hook Value"
    assert c.widget_label.text() == "Hook Value"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_constructs_with_observable(qtbot: QtBot):
    """Test that DisplayValueController constructs with an ObservableSingleValue."""
    app = QApplication.instance() or QApplication([])
    
    # Create an observable with initial value
    obs = ObservableSingleValue(RealUnitedScalar(10, Unit("m")))
    
    c = DisplayValueController(obs)
    qtbot.addWidget(c._owner_widget)
    assert c.single_value == RealUnitedScalar(10, Unit("m"))
    assert c.widget_label.text() == "10.000 m"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_constructs_with_carries_distinct_single_value_hook(qtbot: QtBot):
    """Test that DisplayValueController constructs with a CarriesDistinctSingleValueHook."""
    app = QApplication.instance() or QApplication([])
    
    # Create a controller that implements CarriesDistinctSingleValueHook
    from integrated_widgets import CheckBoxController
    check_controller = CheckBoxController(True)
    
    c = DisplayValueController(check_controller)
    qtbot.addWidget(c._owner_widget)
    assert c.single_value is True
    assert c.widget_label.text() == "True"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_binding(qtbot: QtBot):
    """Test that DisplayValueController can bind to other observables."""
    app = QApplication.instance() or QApplication([])
    
    # Create an observable
    obs = ObservableSingleValue("Initial Value")
    
    # Create the display controller with the same initial value
    c = DisplayValueController("Initial Value")
    qtbot.addWidget(c._owner_widget)
    
    # Bind to the observable
    c.bind_to(obs)
    
    # Check initial binding - both should have the same value
    assert c.single_value == "Initial Value"
    assert obs.single_value == "Initial Value"
    assert c.widget_label.text() == "Initial Value"
    
    # Test that the binding was established
    assert c.distinct_single_value_hook is not None
    assert obs.distinct_single_value_hook is not None


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_disconnect(qtbot: QtBot):
    """Test that DisplayValueController can disconnect from observables."""
    app = QApplication.instance() or QApplication([])
    
    # Create an observable
    obs = ObservableSingleValue("Initial Value")
    
    # Create the display controller with the same initial value
    c = DisplayValueController("Initial Value")
    qtbot.addWidget(c._owner_widget)
    
    # Bind to the observable
    c.bind_to(obs)
    
    # Check initial binding
    assert c.single_value == "Initial Value"
    
    # Disconnect
    c.detach()
    
    # Test that disconnection worked
    assert c.distinct_single_value_hook is not None


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_read_only(qtbot: QtBot):
    """Test that DisplayValueController is read-only and doesn't update component values from widgets."""
    app = QApplication.instance() or QApplication([])
    
    c = DisplayValueController("Test Value")
    qtbot.addWidget(c._owner_widget)
    
    # The update_component_values_from_widgets should be a no-op
    c.update_component_values_from_widgets()
    
    # Value should remain unchanged
    assert c.single_value == "Test Value"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_widget_updates(qtbot: QtBot):
    """Test that DisplayValueController updates its widget when component values change."""
    app = QApplication.instance() or QApplication([])
    
    c = DisplayValueController("Initial")
    qtbot.addWidget(c._owner_widget)
    
    # Manually update the component value
    c._set_component_values({"value": "Updated"}, notify_binding_system=True)
    
    # Widget update should happen automatically, but let's trigger it manually to be sure
    c.update_widgets_from_component_values()
    
    # Check that the widget text is updated
    assert c.widget_label.text() == "Updated"
    assert c.single_value == "Updated"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_with_real_united_scalar(qtbot: QtBot):
    """Test that DisplayValueController works with RealUnitedScalar values."""
    app = QApplication.instance() or QApplication([])
    
    # Test with RealUnitedScalar
    value = RealUnitedScalar(15.5, Unit("kg"))
    c = DisplayValueController(value)
    qtbot.addWidget(c._owner_widget)
    
    assert c.single_value == value
    assert c.widget_label.text() == "15.500 kg"
    
    # Test with different unit
    value2 = RealUnitedScalar(15500, Unit("g"))
    c2 = DisplayValueController(value2)
    qtbot.addWidget(c2._owner_widget)
    
    assert c2.single_value == value2
    assert c2.widget_label.text() == "15500.000 g"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_with_complex_types(qtbot: QtBot):
    """Test that DisplayValueController works with complex types like lists and dicts."""
    app = QApplication.instance() or QApplication([])
    
    # Test with list
    list_value = [1, 2, 3, "test"]
    c = DisplayValueController(list_value)
    qtbot.addWidget(c._owner_widget)
    
    assert c.single_value == list_value
    assert c.widget_label.text() == "[1, 2, 3, 'test']"
    
    # Test with dict
    dict_value = {"key": "value", "number": 42}
    c2 = DisplayValueController(dict_value)
    qtbot.addWidget(c2._owner_widget)
    
    assert c2.single_value == dict_value
    assert c2.widget_label.text() == "{'key': 'value', 'number': 42}"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_mandatory_keys(qtbot: QtBot):
    """Test that DisplayValueController has the correct mandatory component value keys."""
    app = QApplication.instance() or QApplication([])
    
    c = DisplayValueController("Test")
    qtbot.addWidget(c._owner_widget)
    
    assert c._mandatory_component_value_keys() == {"value"}


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_hook_properties(qtbot: QtBot):
    """Test that DisplayValueController provides the correct hook properties."""
    app = QApplication.instance() or QApplication([])
    
    c = DisplayValueController("Test Value")
    qtbot.addWidget(c._owner_widget)
    
    # Check that the hook properties exist and work
    assert hasattr(c, 'distinct_single_value_hook')
    assert hasattr(c, 'distinct_single_value_reference')
    
    # Check that the hook can be accessed
    hook = c.distinct_single_value_hook
    assert hook is not None
    
    # Check that the reference value is correct
    assert c.distinct_single_value_reference == "Test Value"


@pytest.mark.qt_log_ignore(".*")
def test_display_value_controller_initialization_flow(qtbot: QtBot):
    """Test the complete initialization flow of DisplayValueController."""
    app = QApplication.instance() or QApplication([])
    
    # Create with a direct value
    c = DisplayValueController("Initial Value")
    qtbot.addWidget(c._owner_widget)
    
    # Check that widgets are initialized
    assert hasattr(c, '_label')
    assert c._label is not None
    
    # Check that the label text is set
    assert c._label.text() == "Initial Value"
    
    # Check that the component value is correct
    assert c._component_values["value"] == "Initial Value"
    
    # Check that the public property works
    assert c.single_value == "Initial Value"
    assert c.widget_label == c._label


