from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from .base_observable_widget import BaseWidget_With_Observable
from python.gui.custom_widgets.range_slider import CQRangeSlider
import math

from observables import ObservableSingleValue

class ObsQRangeSlider(BaseWidget_With_Observable[ObservableSingleValue[tuple[float, float]]]):
    def __init__(self, initial_value_or_observable: tuple[float, float]|ObservableSingleValue[tuple[float, float]], resolution: float = 0.01, orientation: Qt.Orientation = Qt.Orientation.Horizontal, allow_zero_range: bool = False, parent: QWidget | None = None):

        if isinstance(initial_value_or_observable, tuple):
            self._observable = ObservableSingleValue(initial_value_or_observable)
        else:
            self._observable = initial_value_or_observable

        super().__init__(self._observable, parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._resolution = resolution
        self._previous_valid_range = (0.0, 1.0)  # Store the last valid range

        # Create the range slider (CQRangeSlider doesn't take orientation parameter)
        # Calculate integer range based on resolution for 0.0 to 1.0 range
        min_int = int(round(0.0 / self._resolution, 0))
        max_int = int(round(1.0 / self._resolution, 0))
        self._slider = CQRangeSlider(parent, allow_zero_range=allow_zero_range, minimum=min_int, maximum=max_int, orientation=orientation)
        layout.addWidget(self._slider)
        
        # Set the step size to 1 (since we're using integer steps internally)
        self._slider.setStep(1)
        
        # Connect the slider's rangeChanged signal to update the observable
        self._slider.rangeChanged.connect(lambda _, __: self._internal_update_observable())

        self.construction_finished()

    def _validate_range(self, lower_bound: float, upper_bound: float) -> tuple[float, float]:
        """Validate and normalize range values."""
        # Handle NaN case
        if math.isnan(lower_bound) or math.isnan(upper_bound):
            return (math.nan, math.nan)
        
        # Ensure values are within 0.0 to 1.0 range
        lower_bound = max(0.0, min(1.0, lower_bound))
        upper_bound = max(0.0, min(1.0, upper_bound))
        
        # Ensure lower_bound <= upper_bound
        if lower_bound > upper_bound:
            lower_bound, upper_bound = upper_bound, lower_bound
            
        return (lower_bound, upper_bound)

    def update_widget(self):
        """Update the widget to reflect the current observable value."""
        current_range = self.observable.value
        lower_bound, upper_bound = current_range
        
        # Handle NaN case - disable slider
        if math.isnan(lower_bound) or math.isnan(upper_bound):
            self._slider.setEnabled(False)
            return
        
        # Enable slider and set values
        self._slider.setEnabled(True)
        
        # Convert float values to integers for the slider
        min_value = int(round(lower_bound / self._resolution, 0))
        max_value = int(round(upper_bound / self._resolution, 0))
        
        self._slider.setValue(min_value, max_value)
        
    def update_observable(self):
        """Update the observable to reflect the current widget value."""
        # Don't update if slider is disabled (NaN case)
        if not self._slider.isEnabled():
            return
        
        # Convert slider values back to floats using internal values
        min_value: int = self._slider._min_value
        max_value: int = self._slider._max_value
        fractional_min_value: float = min_value * self._resolution
        fractional_max_value: float = max_value * self._resolution
        
        # Validate the range
        new_range = self._validate_range(fractional_min_value, fractional_max_value)
        
        # Store the valid range for later restoration
        if not (math.isnan(new_range[0]) or math.isnan(new_range[1])):
            self._previous_valid_range = new_range
        
        self.observable.set_value(new_range)

    def setRange(self, lower_bound: float, upper_bound: float):
        """Set the range of the slider in fractional values (0.0 to 1.0)."""
        # Validate the range
        lower_bound, upper_bound = self._validate_range(lower_bound, upper_bound)
        
        # Handle NaN case
        if math.isnan(lower_bound) or math.isnan(upper_bound):
            self._slider.setEnabled(False)
            return
            
        # Enable slider and set range
        self._slider.setEnabled(True)
        min_int = int(round(lower_bound / self._resolution, 0))
        max_int = int(round(upper_bound / self._resolution, 0))
        self._slider.setRange(min_int, max_int)
        
    def getResolution(self) -> float:
        """Get the current resolution."""
        return self._resolution
        
    def setResolution(self, resolution: float):
        """Set the resolution and update the widget."""
        if resolution <= 0:
            raise ValueError("Resolution must be positive")
        self._resolution = resolution
        
        # Recalculate the slider range for 0.0 to 1.0
        min_int = int(round(0.0 / self._resolution, 0))
        max_int = int(round(1.0 / self._resolution, 0))
        self._slider.setRange(min_int, max_int)
        
        self.update_widget()