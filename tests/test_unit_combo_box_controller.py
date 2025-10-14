"""Tests for UnitComboBoxController class.

This test suite focuses on the auto-add functionality that automatically
adds units and dimensions to the available_units dictionary when a new
unit is selected.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from united_system import Unit, Dimension
from observables import ObservableSingleValue, ObservableDict

from integrated_widgets.widget_controllers.unit_combo_box_controller import UnitComboBoxController


@pytest.mark.qt_log_ignore(".*")
def test_unit_combo_box_controller_initialization_with_direct_values(qtbot: QtBot) -> None:
    """Test that UnitComboBoxController initializes correctly with direct Unit values."""
    app = QApplication.instance() or QApplication([])
    
    # Create initial units
    meter = Unit("m")
    kilometer = Unit("km")
    length_dimension = meter.dimension
    
    # Create available units dict
    available_units: dict[Dimension, set[Unit]] = {
        length_dimension: {meter, kilometer}
    }
    
    # Create controller with direct values
    controller = UnitComboBoxController(
        selected_unit=meter,
        available_units=available_units
    )
    
    # Check initial values
    assert controller.selected_unit == meter
    assert length_dimension in controller.available_units
    assert meter in controller.available_units[length_dimension]
    assert kilometer in controller.available_units[length_dimension]


@pytest.mark.qt_log_ignore(".*")
def test_unit_combo_box_controller_initialization_with_observables(qtbot: QtBot) -> None:
    """Test that UnitComboBoxController initializes correctly with observables."""
    app = QApplication.instance() or QApplication([])
    
    # Create initial units
    meter = Unit("m")
    kilometer = Unit("km")
    length_dimension = meter.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter, kilometer}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Check initial values
    assert controller.selected_unit == meter
    assert selected_unit_observable.value == meter


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_new_unit_to_existing_dimension(qtbot: QtBot) -> None:
    """Test that a new unit is automatically added to an existing dimension."""
    app = QApplication.instance() or QApplication([])
    
    # Create initial units
    meter = Unit("m")
    kilometer = Unit("km")
    centimeter = Unit("cm")  # New unit to add
    length_dimension = meter.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter, kilometer}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Verify centimeter is not in available units initially
    assert centimeter not in available_units_observable.value[length_dimension]

    # Change selected unit to centimeter (which is not in available units)
    controller.selected_unit = centimeter
    
    # Verify centimeter was automatically added
    assert centimeter in controller.available_units[length_dimension]
    assert centimeter in available_units_observable.value[length_dimension]
    assert controller.selected_unit == centimeter


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_unit_with_new_dimension(qtbot: QtBot) -> None:
    """Test that a unit with a new dimension is automatically added."""
    app = QApplication.instance() or QApplication([])
    
    # Create initial units (length dimension)
    meter = Unit("m")
    kilometer = Unit("km")
    length_dimension = meter.dimension
    
    # Create a unit with a different dimension
    kilogram = Unit("kg")
    mass_dimension = kilogram.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter, kilometer}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Verify mass dimension is not in available units initially
    assert mass_dimension not in available_units_observable.value
    
    # Change selected unit to kilogram (different dimension)
    controller.selected_unit = kilogram
    
    # Verify mass dimension and kilogram were automatically added
    assert mass_dimension in controller.available_units
    assert kilogram in controller.available_units[mass_dimension]
    assert mass_dimension in available_units_observable.value
    assert kilogram in available_units_observable.value[mass_dimension]
    assert controller.selected_unit == kilogram


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_with_observable_updates(qtbot: QtBot) -> None:
    """Test that auto-add works when updating via observable."""
    app = QApplication.instance() or QApplication([])
    
    # Create initial units
    meter = Unit("m")
    length_dimension = meter.dimension
    
    # Create a unit with different dimension
    second = Unit("s")
    time_dimension = second.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Update via observable
    selected_unit_observable.value = second
    
    # Verify auto-add happened
    assert time_dimension in available_units_observable.value
    assert second in available_units_observable.value[time_dimension]


@pytest.mark.qt_log_ignore(".*")
def test_no_duplicate_units_added(qtbot: QtBot) -> None:
    """Test that setting an already-existing unit doesn't create duplicates."""
    app = QApplication.instance() or QApplication([])
    
    # Create initial units
    meter = Unit("m")
    kilometer = Unit("km")
    length_dimension = meter.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter, kilometer}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Count initial units
    initial_count = len(available_units_observable.value[length_dimension])
    
    # Set to meter again (already exists)
    controller.selected_unit = meter
    
    # Verify no duplicates (sets prevent duplicates anyway, but test behavior)
    assert len(available_units_observable.value[length_dimension]) == initial_count
    assert meter in available_units_observable.value[length_dimension]


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_multiple_units_sequentially(qtbot: QtBot) -> None:
    """Test auto-adding multiple different units sequentially."""
    app = QApplication.instance() or QApplication([])
    
    # Create units
    meter = Unit("m")
    second = Unit("s")
    kilogram = Unit("kg")
    ampere = Unit("A")
    
    length_dimension = meter.dimension
    time_dimension = second.dimension
    mass_dimension = kilogram.dimension
    current_dimension = ampere.dimension
    
    # Create observables with only one unit initially
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Sequentially add units from different dimensions
    controller.selected_unit = second
    assert time_dimension in controller.available_units
    assert second in controller.available_units[time_dimension]
    
    controller.selected_unit = kilogram
    assert mass_dimension in controller.available_units
    assert kilogram in controller.available_units[mass_dimension]
    
    controller.selected_unit = ampere
    assert current_dimension in controller.available_units
    assert ampere in controller.available_units[current_dimension]
    
    # Verify all dimensions are present
    assert len(controller.available_units) == 4


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_complex_units(qtbot: QtBot) -> None:
    """Test auto-adding complex/derived units."""
    app = QApplication.instance() or QApplication([])
    
    # Create initial simple unit
    meter = Unit("m")
    length_dimension = meter.dimension
    
    # Create complex units
    velocity = Unit("m/s")
    acceleration = Unit("m/s^2")
    velocity_dimension = velocity.dimension
    acceleration_dimension = acceleration.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Add complex unit
    controller.selected_unit = velocity
    assert velocity_dimension in controller.available_units
    assert velocity in controller.available_units[velocity_dimension]
    
    # Add another complex unit
    controller.selected_unit = acceleration
    assert acceleration_dimension in controller.available_units
    assert acceleration in controller.available_units[acceleration_dimension]


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_with_none_selected_unit(qtbot: QtBot) -> None:
    """Test behavior when selected_unit is None."""
    app = QApplication.instance() or QApplication([])
    
    # Create units
    meter = Unit("m")
    length_dimension = meter.dimension
    
    # Create observables with None as initial value
    selected_unit_observable = ObservableSingleValue[Unit | None](None)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Verify controller handles None
    assert controller.selected_unit is None
    
    # Set to a unit
    controller.selected_unit = meter
    assert controller.selected_unit == meter
    
    # Set back to None
    controller.selected_unit = None
    assert controller.selected_unit is None


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_preserves_existing_units(qtbot: QtBot) -> None:
    """Test that auto-add preserves all existing units in a dimension."""
    app = QApplication.instance() or QApplication([])
    
    # Create multiple units in same dimension
    meter = Unit("m")
    kilometer = Unit("km")
    centimeter = Unit("cm")
    millimeter = Unit("mm")
    micrometer = Unit("µm")
    length_dimension = meter.dimension
    
    # Create observables with several units
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter, kilometer, centimeter}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Add new units
    controller.selected_unit = millimeter
    
    # Verify all original units are still present
    assert meter in controller.available_units[length_dimension]
    assert kilometer in controller.available_units[length_dimension]
    assert centimeter in controller.available_units[length_dimension]
    assert millimeter in controller.available_units[length_dimension]
    
    # Add another unit
    controller.selected_unit = micrometer
    
    # Verify all units are still present
    assert meter in controller.available_units[length_dimension]
    assert kilometer in controller.available_units[length_dimension]
    assert centimeter in controller.available_units[length_dimension]
    assert millimeter in controller.available_units[length_dimension]
    assert micrometer in controller.available_units[length_dimension]


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_with_hook_interface(qtbot: QtBot) -> None:
    """Test that auto-add works when using hook interface."""
    app = QApplication.instance() or QApplication([])
    
    # Create units
    meter = Unit("m")
    second = Unit("s")
    length_dimension = meter.dimension
    time_dimension = second.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter}
    })
    
    # Create controller using hook interface
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable.hook,
        available_units=available_units_observable.value_hook
    )
    
    # Update via observable
    selected_unit_observable.value = second
    
    # Verify auto-add happened
    assert time_dimension in available_units_observable.value
    assert second in available_units_observable.value[time_dimension]


@pytest.mark.qt_log_ignore(".*")
def test_auto_add_with_prefixed_units(qtbot: QtBot) -> None:
    """Test auto-adding units with SI prefixes."""
    app = QApplication.instance() or QApplication([])
    
    # Create base unit
    meter = Unit("m")
    length_dimension = meter.dimension
    
    # Create prefixed units
    kilometer = Unit("km")
    millimeter = Unit("mm")
    micrometer = Unit("µm")
    nanometer = Unit("nm")
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Add various prefixed units
    for unit in [kilometer, millimeter, micrometer, nanometer]:
        controller.selected_unit = unit
        assert unit in controller.available_units[length_dimension]
    
    # Verify all units are present
    assert len(controller.available_units[length_dimension]) == 5


@pytest.mark.qt_log_ignore(".*")
def test_simultaneous_update_of_selected_unit_and_available_units(qtbot: QtBot) -> None:
    """Test behavior when both selected_unit and selectable_units are updated together."""
    app = QApplication.instance() or QApplication([])
    
    # Create units
    meter = Unit("m")
    kilometer = Unit("km")
    second = Unit("s")
    length_dimension = meter.dimension
    time_dimension = second.dimension
    
    # Create observables
    selected_unit_observable = ObservableSingleValue[Unit | None](meter)
    available_units_observable = ObservableDict[Dimension, set[Unit]]({
        length_dimension: {meter, kilometer}
    })
    
    # Create controller
    controller = UnitComboBoxController(
        selected_unit=selected_unit_observable,
        available_units=available_units_observable
    )
    
    # Update both at once using the controller method
    new_selectable_units: set[Unit] = {second}
    controller.change_selected_unit_and_selectable_units(second, new_selectable_units)
    
    # Note: When both are updated together, the add_values_to_be_updated_callback
    # returns empty dict (case True, True), so no auto-add occurs
    assert controller.selected_unit == second

