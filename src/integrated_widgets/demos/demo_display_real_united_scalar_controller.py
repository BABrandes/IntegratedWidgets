#!/usr/bin/env python3
"""
Simple demo for DisplayRealUnitedScalarController

This demo just displays the controller's all_widgets_as_frame output.
"""

# Standard library imports
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# BAB imports
from united_system import RealUnitedScalar, Unit, NamedQuantity, Dimension
from observables import ObservableSingleValue, ObservableDict
from integrated_widgets import RealUnitedScalarController, DisplayValueController

# Local imports
from .utils import debug_logger

class DemoWindow(QMainWindow):
    """Simple demo window that just shows the controller's frame."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DisplayRealUnitedScalarController Demo")
        self.setGeometry(100, 100, 600, 800)
        
        # Use the debug logger from utils
        self.logger = debug_logger
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create observable values
        value_observable = ObservableSingleValue[RealUnitedScalar](
            RealUnitedScalar(100.0, Unit("km"))
        )
        
        # Create unit options for different dimensions
        unit_options_observable = ObservableDict[Dimension, set[Unit]]({})
        unit_options_observable.value = {
            NamedQuantity.LENGTH.dimension: {
                Unit("m"), Unit("km"), Unit("cm"), Unit("mm")
            },
            NamedQuantity.TIME.dimension: {
                Unit("s"), Unit("min"), Unit("h")
            },
            NamedQuantity.MASS.dimension: {
                Unit("kg"), Unit("g")
            }
        }
        
        # Create the controller with logger
        controller = RealUnitedScalarController(
            value=value_observable,
            display_unit_options=unit_options_observable,
            parent_of_widgets=self,
            allowed_dimensions={NamedQuantity.LENGTH.dimension, NamedQuantity.TIME.dimension, NamedQuantity.MASS.dimension, NamedQuantity.VOLTAGE_SCAN_RATE.dimension, NamedQuantity.VOLTAGE.dimension},
            logger=self.logger
        )
        self.logger.info("Controller created successfully")
        
        # Just display the controller's frame
        frame = controller.all_widgets_as_frame()
        self.logger.info("Frame created successfully")
        main_layout.addWidget(frame)
        self.logger.info("Frame added to layout")
        
        # Add status display showing current value
        self.logger.info("Creating status display controller...")
        value_status = DisplayValueController[RealUnitedScalar](controller.value_hook, logger=self.logger)
        main_layout.addWidget(value_status.widget_label)
        self.logger.info("Status display added to layout")


def main():
    """Main demo function."""
    # Use the debug logger from utils
    main_logger = debug_logger
    main_logger.info("Starting demo...")
    
    try:
        app = QApplication(sys.argv)
        main_logger.info("QApplication created")
        
        # Create and show the demo window
        window = DemoWindow()
        main_logger.info("DemoWindow created")
        window.show()
        main_logger.info("Window created and shown")
        
        # Run the application
        main_logger.info("Starting Qt event loop...")
        sys.exit(app.exec())
    except Exception as e:
        main_logger.error(f"Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
