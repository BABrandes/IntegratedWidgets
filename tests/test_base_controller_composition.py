"""Tests for BaseControllerComposition class."""

from __future__ import annotations

from typing import Any
import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets.util.base_contoller_composition import BaseControllerComposition
from integrated_widgets.util.base_controller import BaseController

# Import real controllers for testing
from integrated_widgets.widget_controllers.display_value_controller import DisplayValueController
from integrated_widgets.widget_controllers.check_box_controller import CheckBoxController
from integrated_widgets.widget_controllers.text_entry_controller import TextEntryController


# Ensure Qt application is running for all tests
@pytest.fixture(scope="session", autouse=True)
def qt_app():
    """Ensure Qt application is running for all tests."""
    import gc
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Disable automatic garbage collection during tests to prevent crashes
    gc.disable()
    yield app
    # Re-enable GC after tests
    gc.enable()

# Force cleanup after each test
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Clean up after each test to prevent state pollution."""
    yield
    # Process any pending Qt events
    app = QApplication.instance()
    if app:
        app.processEvents()
        # Let Qt process deleteLater() calls
        app.sendPostedEvents(None, 0)  # Process deferred delete events
        app.processEvents()


def test_basic_composition_lifecycle() -> None:
    """Test basic composition registration and disposal."""
    comp = BaseControllerComposition()
    
    # Create real controllers
    controller1 = DisplayValueController("Hello")
    controller2 = CheckBoxController(True, text="Test checkbox")
    
    # Register controllers
    comp.register_controllers(controller1, controller2) # type: ignore
    
    # Check registration
    assert len(comp.controllers) == 2
    assert controller1 in comp.controllers
    assert controller2 in comp.controllers
    assert not comp.is_disposed
        
    # Check controllers are not disposed yet
    assert not controller1._is_disposed # type: ignore
    assert not controller2._is_disposed # type: ignore
    
    # Dispose composition
    comp.dispose()
    
    # Check disposal
    assert comp.is_disposed
    assert len(comp.controllers) == 0
    assert controller1._is_disposed # type: ignore
    assert controller2._is_disposed # type: ignore


def test_idempotent_disposal() -> None:
    """Test that disposal is idempotent."""
    comp = BaseControllerComposition()
    controller = DisplayValueController(42)
    
    comp.register_controllers(controller) # type: ignore
    
    # First disposal
    comp.dispose()
    assert comp.is_disposed
    assert controller._is_disposed # type: ignore
    
    # Second disposal should be safe
    comp.dispose()
    assert comp.is_disposed
    assert controller._is_disposed # type: ignore


def test_auto_register_controllers() -> None:
    """Test auto-registration of controllers."""
    comp = BaseControllerComposition()
    
    # Create a source object with controllers
    class SourceObject:
        def __init__(self) -> None:
            self.controller1 = DisplayValueController("auto1")
            self.controller2 = CheckBoxController(False, text="auto2")
            self.not_controller = "not a controller"
            self._private_controller = TextEntryController("private")
            self.method_controller = lambda: None  # Should be ignored
    
    source = SourceObject()
    
    # Auto-register controllers
    new_count = comp.auto_register_controllers(source)
    
    # Should find 2 controllers (not_controller and _private_controller are ignored)
    assert new_count == 2
    assert len(comp.controllers) == 2
    assert source.controller1 in comp.controllers
    assert source.controller2 in comp.controllers
    assert source.not_controller not in comp.controllers
    assert source._private_controller not in comp.controllers # type: ignore


def test_nested_composition_basic() -> None:
    """Test basic nested composition functionality."""
    # Create child compositions
    child_comp_a = BaseControllerComposition()
    child_comp_b = BaseControllerComposition()
    
    # Add controllers to child compositions
    child_controller_a1 = DisplayValueController("child_a1")
    child_controller_a2 = CheckBoxController(True, text="child_a2")
    child_controller_b1 = TextEntryController("child_b1")
    child_controller_b2 = DisplayValueController(42)
    
    child_comp_a.register_controllers(child_controller_a1, child_controller_a2) # type: ignore
    child_comp_b.register_controllers(child_controller_b1, child_controller_b2) # type: ignore
    
    # Create parent composition
    parent_comp = BaseControllerComposition()
    standalone_controller = CheckBoxController(False, text="standalone")
    
    # Register child compositions and standalone controller
    parent_comp.register_controllers(child_comp_a, child_comp_b, standalone_controller) # type: ignore
    
    # Check registration
    assert len(parent_comp.controllers) == 3
    assert child_comp_a in parent_comp.controllers
    assert child_comp_b in parent_comp.controllers
    assert standalone_controller in parent_comp.controllers
    
    # Check child compositions are not disposed yet
    assert not child_comp_a.is_disposed
    assert not child_comp_b.is_disposed
    assert not any(c._is_disposed for c in [child_controller_a1, child_controller_a2, child_controller_b1, child_controller_b2]) # type: ignore
    assert not standalone_controller._is_disposed # type: ignore
    
    # Dispose parent composition
    parent_comp.dispose()
    
    # Check that parent is disposed
    assert parent_comp.is_disposed
    
    # Check that child compositions are disposed (reverse order)
    assert child_comp_a.is_disposed
    assert child_comp_b.is_disposed
    
    # Check that all controllers are disposed
    assert standalone_controller._is_disposed # type: ignore
    assert child_controller_a1._is_disposed # type: ignore
    assert child_controller_a2._is_disposed # type: ignore
    assert child_controller_b1._is_disposed # type: ignore
    assert child_controller_b2._is_disposed # type: ignore


def test_nested_composition_auto_registration() -> None:
    """Test that auto-registration finds nested compositions."""
    # Create child composition
    child_comp = BaseControllerComposition()
    child_controller = DisplayValueController("child")
    child_comp.register_controllers(child_controller) # type: ignore
    
    # Create parent composition with child as attribute
    class ParentObject:
        def __init__(self) -> None:
            self.child_composition = child_comp
            self.standalone_controller = CheckBoxController(True, text="standalone")
    
    parent_obj = ParentObject()
    parent_comp = BaseControllerComposition()
    
    # Auto-register should find both the child composition and standalone controller
    new_count = parent_comp.auto_register_controllers(parent_obj)
    
    assert new_count == 2
    assert len(parent_comp.controllers) == 2
    assert child_comp in parent_comp.controllers
    assert parent_obj.standalone_controller in parent_comp.controllers


def test_nested_composition_disposal_order() -> None:
    """Test that nested compositions are disposed in hierarchical order (type-based)."""
    # Track disposal order
    disposal_order: list[str] = []
    
    class TrackingController(DisplayValueController): # type: ignore
        def __init__(self, name: str) -> None:
            super().__init__(name) # type: ignore
            self.name = name
        
        def dispose(self) -> None: # type: ignore
            disposal_order.append(self.name)
            super().dispose() # type: ignore
    
    class TrackingComposition(BaseControllerComposition): # type: ignore
        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name
        
        def dispose(self) -> None: #type: ignore
            disposal_order.append(f"composition_{self.name}")
            super().dispose()
    
    # Create nested structure
    # Parent -> ChildB -> ChildA -> Controllers
    child_a = TrackingComposition("A")
    child_b = TrackingComposition("B")
    parent = TrackingComposition("Parent")
    
    # Add controllers to child A
    child_a.register_controllers( # type: ignore
        TrackingController("child_a_1"),
        TrackingController("child_a_2")
    )
    
    # Add controllers to child B
    child_b.register_controllers( # type: ignore
        TrackingController("child_b_1"),
        TrackingController("child_b_2")
    )
    
    # Add child compositions and standalone controller to parent
    parent.register_controllers( # type: ignore
        child_b,
        child_a,
        TrackingController("standalone")
    )
    
    # Dispose parent
    parent.dispose()
    
    # Check disposal order (should be hierarchical: controllers first, then compositions)
    # The parent composition's dispose() method is called first, then its controllers
    expected_order = [
        "composition_Parent",   # Parent composition dispose() called first
        "standalone",           # Controllers disposed first (leaf nodes)
        "composition_B",        # Compositions disposed after controllers (parent nodes)
        "child_b_1",           # Controllers in child B
        "child_b_2",           
        "composition_A",        # Compositions disposed after controllers (parent nodes)
        "child_a_1",           # Controllers in child A
        "child_a_2",           
    ]
    
    assert disposal_order == expected_order


def test_disposal_with_errors() -> None:
    """Test that disposal continues even when individual controllers raise errors."""
    comp = BaseControllerComposition()
    
    # Create controllers, one with error
    good_controller = DisplayValueController("good")
    
    # Create a controller that will raise an error during disposal
    class ErrorController(DisplayValueController): # type: ignore
        def dispose(self) -> None:  # type: ignore
            self._is_disposed = True  # Mark as disposed before raising error
            raise RuntimeError("Disposal error")
    
    bad_controller = ErrorController("bad")
    
    comp.register_controllers(good_controller, bad_controller) # type: ignore
    
    # Dispose should not raise exception
    comp.dispose()
    
    # Both controllers should be marked as disposed
    assert comp.is_disposed
    assert good_controller._is_disposed # type: ignore
    assert bad_controller._is_disposed # type: ignore


def test_context_manager() -> None:
    """Test that composition works as a context manager."""
    controller = CheckBoxController(True, text="context")
    
    with BaseControllerComposition() as comp:
        comp.register_controllers(controller) # type: ignore
        assert not comp.is_disposed
        assert not controller._is_disposed # type: ignore
    
    # Should be disposed after context exit
    assert comp.is_disposed
    assert controller._is_disposed # type: ignore


def test_controllers_property() -> None:
    """Test that controllers property returns a tuple."""
    comp = BaseControllerComposition()
    controller1 = DisplayValueController("1")
    controller2 = CheckBoxController(False, text="2")
    
    comp.register_controllers(controller1, controller2) # type: ignore
    
    controllers = comp.controllers
    assert isinstance(controllers, tuple)
    assert len(controllers) == 2
    assert controller1 in controllers
    assert controller2 in controllers


def test_warn_on_unregistered_controllers() -> None:
    """Test the warning behavior for unregistered controllers."""
    import warnings
    
    # Test with warnings enabled (default)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        comp = BaseControllerComposition()
        
        # Create a source with unregistered controllers
        class SourceWithControllers: # type: ignore
            def __init__(self) -> None:
                self.controller = DisplayValueController("unregistered")
        
        source = SourceWithControllers()
        comp.auto_register_controllers(source)  # This should register the controller
        
        # Now dispose - should not warn since controller was registered
        comp.dispose()
        
        # Should not have any warnings
        assert len(w) == 0
    
    # Test with warnings disabled
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        comp = BaseControllerComposition(warn_on_unregistered_controllers=False)
        
        # Create a source with unregistered controllers
        class SourceWithControllers:
            def __init__(self) -> None:
                self.controller = DisplayValueController("unregistered")
        
        source = SourceWithControllers()
        comp.auto_register_controllers(source)
        comp.dispose()
        
        # Should not have any warnings even if there were unregistered controllers
        assert len(w) == 0


def test_deeply_nested_composition() -> None:
    """Test deeply nested composition structure."""
    # Create a deep nesting: Level1 -> Level2 -> Level3 -> Controllers
    level3 = BaseControllerComposition()
    level2 = BaseControllerComposition()
    level1 = BaseControllerComposition()
    
    # Add controllers to level 3
    level3_controller = DisplayValueController("level3")
    level3.register_controllers(level3_controller) # type: ignore
    
    # Add level 3 to level 2
    level2_controller = CheckBoxController(True, text="level2")
    level2.register_controllers(level2_controller, level3) # type: ignore
    
    # Add level 2 to level 1
    level1_controller = TextEntryController("level1")
    level1.register_controllers(level1_controller, level2) # type: ignore
    
    # Check initial state
    assert not any(comp.is_disposed for comp in [level1, level2, level3])
    assert not any(ctrl._is_disposed for ctrl in [level1_controller, level2_controller, level3_controller]) # type: ignore
    
    # Dispose level 1
    level1.dispose()
    
    # Check all levels and controllers are disposed
    assert all(comp.is_disposed for comp in [level1, level2, level3])
    assert all(ctrl._is_disposed for ctrl in [level1_controller, level2_controller, level3_controller]) # type: ignore


def test_type_restrictions() -> None:
    """Test that only BaseController and BaseControllerComposition instances can be registered."""
    comp = BaseControllerComposition()
    
    # Test with invalid types
    invalid_objects: list[Any] = [
        "string",
        42,
        [],
        {},
        lambda: None,
        object(),
    ]
    
    for invalid_obj in invalid_objects:
        with pytest.raises(TypeError, match="Only BaseController and BaseControllerComposition instances can be registered"):
            comp.register_controllers(invalid_obj) # type: ignore
    
    # Test with object that has dispose but isn't BaseController-like
    class FakeController:
        def dispose(self):
            pass
    
    with pytest.raises(TypeError, match="Only BaseController and BaseControllerComposition instances can be registered"):
        comp.register_controllers(FakeController()) # type: ignore
    
    # Test with valid types (should not raise)
    valid_controller = DisplayValueController("valid")
    valid_composition = BaseControllerComposition()
    
    # These should not raise
    comp.register_controllers(valid_controller, valid_composition) # type: ignore
    assert len(comp.controllers) == 2


def test_disposal_order_independence() -> None:
    """Test that disposal order is independent of registration order."""
    # Test 1: Controllers first, then compositions
    comp1 = BaseControllerComposition()
    child_comp1 = BaseControllerComposition()
    child_comp2 = BaseControllerComposition()
    
    controller1 = DisplayValueController("Controller1")
    controller2 = CheckBoxController(True, text="Controller2")
    
    comp1.register_controllers(controller1, controller2, child_comp1, child_comp2) # type: ignore
    
    # Track disposal order
    disposal_order = []
    
    def track_disposal(controller: BaseController[Any, Any, Any], name: str) -> None:
        original_dispose = controller.dispose
        def tracked_dispose():
            disposal_order.append(name) # type: ignore
            original_dispose()
        controller.dispose = tracked_dispose # type: ignore
    
    track_disposal(controller1, "Controller1")
    track_disposal(controller2, "Controller2")
    
    # Mock composition disposal tracking
    original_dispose1 = child_comp1.dispose
    original_dispose2 = child_comp2.dispose
    
    def tracked_dispose1():
        disposal_order.append("ChildComp1") # type: ignore
        original_dispose1()
    
    def tracked_dispose2():
        disposal_order.append("ChildComp2") # type: ignore
        original_dispose2()
    
    child_comp1.dispose = tracked_dispose1 # type: ignore
    child_comp2.dispose = tracked_dispose2 # type: ignore
    
    comp1.dispose()
    
    # Controllers should be disposed first, then compositions
    assert disposal_order == ["Controller1", "Controller2", "ChildComp1", "ChildComp2"]
    
    # Test 2: Compositions first, then controllers (different order)
    comp2 = BaseControllerComposition()
    child_comp3 = BaseControllerComposition()
    child_comp4 = BaseControllerComposition()
    
    controller3 = TextEntryController("Controller3")
    controller4 = DisplayValueController(42)
    
    comp2.register_controllers(child_comp3, child_comp4, controller3, controller4) # type: ignore
    
    disposal_order2 = []
    
    def track_disposal2(controller: BaseController[Any, Any, Any], name: str) -> None:
        original_dispose = controller.dispose
        def tracked_dispose() -> None:
            disposal_order2.append(name) # type: ignore
            original_dispose()
        controller.dispose = tracked_dispose # type: ignore
    
    track_disposal2(controller3, "Controller3")
    track_disposal2(controller4, "Controller4")
    
    # Mock composition disposal tracking
    original_dispose3 = child_comp3.dispose
    original_dispose4 = child_comp4.dispose
    
    def tracked_dispose3():
        disposal_order2.append("ChildComp3") # type: ignore
        original_dispose3()
    
    def tracked_dispose4():
        disposal_order2.append("ChildComp4") # type: ignore
        original_dispose4()
    
    child_comp3.dispose = tracked_dispose3 # type: ignore
    child_comp4.dispose = tracked_dispose4 # type: ignore
    
    comp2.dispose()
    
    # Controllers should still be disposed first, then compositions
    assert disposal_order2 == ["Controller3", "Controller4", "ChildComp3", "ChildComp4"]
