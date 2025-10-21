#!/usr/bin/env python3
"""Demo application for IQtTextEntry widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from nexpy import XValue

from integrated_widgets import IQtTextEntry, IQtOptionalTextEntry, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtTextEntry Demo")
    window.resize(500, 450)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Title
    layout.addWidget(QLabel("<h2>IQtTextEntry Demo</h2>"))
    
    # Create observable string values
    name = XValue("John Doe")
    email = XValue("john@example.com")
    username = XValue("johndoe")
    nickname = XValue[str | None](None)
    
    # Name (non-empty)
    layout.addWidget(QLabel("<b>Name (required):</b>"))
    name_widget = IQtTextEntry(
        name,
        validator=lambda x: len(x) > 0
    )
    layout.addWidget(name_widget)
    name_display = IQtDisplayValue(name, formatter=lambda x: f"Name: {x}")
    layout.addWidget(name_display)
    
    # Email (must contain @)
    layout.addWidget(QLabel("<b>Email (must contain @):</b>"))
    email_widget = IQtTextEntry(
        email,
        validator=lambda x: "@" in x and len(x) > 3
    )
    layout.addWidget(email_widget)
    email_display = IQtDisplayValue(email, formatter=lambda x: f"Email: {x}")
    layout.addWidget(email_display)
    
    # Username (3-20 chars, no spaces)
    layout.addWidget(QLabel("<b>Username (3-20 chars, no spaces):</b>"))
    username_widget = IQtTextEntry(
        username,
        validator=lambda x: 3 <= len(x) <= 20 and " " not in x
    )
    layout.addWidget(username_widget)
    username_display = IQtDisplayValue(username, formatter=lambda x: f"@{x}")
    layout.addWidget(username_display)
    
    # Nickname (optional)
    layout.addWidget(QLabel("<b>Nickname (optional):</b>"))
    nickname_widget = IQtOptionalTextEntry(
        nickname,
        none_value="(none)"
    )
    layout.addWidget(nickname_widget)
    nickname_display = IQtDisplayValue(nickname, formatter=lambda x: f"Nickname: {x if x else 'Not set'}")
    layout.addWidget(nickname_display)
    
    # Button to clear optional field
    def clear_nickname():
        nickname.value = None
    
    clear_button = QPushButton("Clear Nickname")
    clear_button.clicked.connect(clear_nickname)
    layout.addWidget(clear_button)
    
    layout.addStretch()
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

