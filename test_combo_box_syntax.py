#!/usr/bin/env python3
"""Test ComboBoxController syntax in isolation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock the problematic imports
class MockBaseObservableController:
    def __init__(self, *args, **kwargs):
        pass

class MockHook:
    pass

class MockCarriesDistinctSingleValueHook:
    pass

class MockCarriesDistinctSetHook:
    pass

class MockSyncMode:
    UPDATE_SELF_FROM_OBSERVABLE = "UPDATE_SELF_FROM_OBSERVABLE"

class MockObservableSelectionOption:
    pass

class MockGuardedComboBox:
    def __init__(self, parent):
        pass

# Replace the imports
sys.modules['integrated_widgets.widget_controllers.base_controller'] = type('MockModule', (), {
    'BaseObservableController': MockBaseObservableController
})

sys.modules['observables'] = type('MockModule', (), {
    'CarriesDistinctSingleValueHook': MockCarriesDistinctSingleValueHook,
    'CarriesDistinctSetHook': MockCarriesDistinctSetHook,
    'Hook': MockHook,
    'SyncMode': MockSyncMode,
    'ObservableSelectionOption': MockObservableSelectionOption
})

sys.modules['integrated_widgets.guarded_widgets'] = type('MockModule', (), {
    'GuardedComboBox': MockGuardedComboBox
})

# Now try to import
try:
    from integrated_widgets.widget_controllers.combo_box_controller import ComboBoxController
    print("✅ ComboBoxController imported successfully!")
    print("✅ Syntax is valid!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
