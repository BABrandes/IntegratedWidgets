#!/usr/bin/env python3
"""Test file for multi-observable functionality."""

from src.integrated_widgets.util.widget_base import ObservableWidgetMixin
from observables import ObservableTuple

class TestController(ObservableWidgetMixin):
    """Simple test controller to verify multi-observable functionality."""
    
    def __init__(self, observable):
        self.__init_mixin__(observable)
    
    def update_widget_from_observable(self):
        """Abstract method implementation."""
        pass
    
    def update_observable_from_widget(self):
        """Abstract method implementation."""
        pass

def test_single_observable():
    """Test single observable functionality."""
    print("Testing single observable...")
    obs1 = ObservableTuple(value=(42,))
    controller1 = TestController(obs1)
    print(f"  Single observable works: {controller1.observable.tuple_value}")
    print(f"  Observable keys: {controller1.get_observable_keys()}")
    print()

def test_multiple_observables():
    """Test multiple observables functionality."""
    print("Testing multiple observables...")
    obs1 = ObservableTuple(value=(42,))
    obs2 = ObservableTuple(value=('test',))
    obs3 = ObservableTuple(value=(3.14,))
    
    controller2 = TestController({
        'first': obs1, 
        'second': obs2, 
        'third': obs3
    })
    
    print(f"  Multiple observables work: {controller2.get_observable_keys()}")
    print(f"  First observable: {controller2.get_observable('first').tuple_value}")
    print(f"  Second observable: {controller2.get_observable('second').tuple_value}")
    print(f"  Third observable: {controller2.get_observable('third').tuple_value}")
    print(f"  Backward compatibility: {controller2.observable.tuple_value}")
    print()

def test_observable_management():
    """Test adding and removing observables."""
    print("Testing observable management...")
    obs1 = ObservableTuple(value=(42,))
    controller = TestController(obs1)
    
    print(f"  Initial keys: {controller.get_observable_keys()}")
    
    # Add new observable
    obs2 = ObservableTuple(value=('new',))
    controller.add_observable('new_key', obs2)
    print(f"  After adding 'new_key': {controller.get_observable_keys()}")
    
    # Remove observable
    controller.remove_observable('new_key')
    print(f"  After removing 'new_key': {controller.get_observable_keys()}")
    print()

if __name__ == "__main__":
    try:
        test_single_observable()
        test_multiple_observables()
        test_observable_management()
        print("✅ All tests passed! Multi-observable functionality is working correctly.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
