#!/usr/bin/env python3
"""Demo application for IQtIntegerEntry widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from nexpy import XValue

from integrated_widgets import IQtIntegerEntry, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtIntegerEntry Demo")
    window.resize(500, 400)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtIntegerEntry Demo</h2>"))
    
    # Create observable integer values
    age = XValue(25)
    count = XValue(100)
    score = XValue(85)
    
    # Age with range validation
    layout.addWidget(QLabel("<b>Age (0-120):</b>"))
    age_widget = IQtIntegerEntry(
        age,
        validator=lambda x: 0 <= x <= 120
    )
    layout.addWidget(age_widget)
    age_display = IQtDisplayValue(age, formatter=lambda x: f"{x} years old")
    layout.addWidget(age_display)
    
    # Count (non-negative)
    layout.addWidget(QLabel("<b>Item Count (non-negative):</b>"))
    count_widget = IQtIntegerEntry(
        count,
        validator=lambda x: x >= 0
    )
    layout.addWidget(count_widget)
    count_display = IQtDisplayValue(count, formatter=lambda x: f"{x} items")
    layout.addWidget(count_display)
    
    # Score (0-100)
    layout.addWidget(QLabel("<b>Test Score (0-100):</b>"))
    score_widget = IQtIntegerEntry(
        score,
        validator=lambda x: 0 <= x <= 100
    )
    layout.addWidget(score_widget)
    score_display = IQtDisplayValue(score, formatter=lambda x: f"{x}/100 ({('F' if x < 60 else 'D' if x < 70 else 'C' if x < 80 else 'B' if x < 90 else 'A')})")
    layout.addWidget(score_display)
    
    # Buttons to modify values
    def increment_all():
        age.value = min(120, age.value + 1)
        count.value += 10
        score.value = min(100, score.value + 5)
    
    def decrement_all():
        age.value = max(0, age.value - 1)
        count.value = max(0, count.value - 10)
        score.value = max(0, score.value - 5)
    
    inc_button = QPushButton("Increment All")
    inc_button.clicked.connect(increment_all)
    layout.addWidget(inc_button)
    
    dec_button = QPushButton("Decrement All")
    dec_button.clicked.connect(decrement_all)
    layout.addWidget(dec_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

