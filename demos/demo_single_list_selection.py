#!/usr/bin/env python3
"""Demo application for IQtSingleListSelection widget."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
from observables import ObservableSingleValue, ObservableOptionalSelectionOption, ObservableSet

from integrated_widgets import IQtSingleListSelection, IQtDisplayValue


def main():
    """Main demo function."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IQtSingleListSelection Demo")
    window.resize(700, 500)
    
    # Central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QHBoxLayout(central_widget)
    
    # Left column - programming languages
    left_layout = QVBoxLayout()
    layout.addLayout(left_layout)
    
    left_layout.addWidget(QLabel("<h3>Programming Languages</h3>"))
    languages = ObservableSet(frozenset({"Python", "JavaScript", "Java", "C++", "Rust", "Go", "TypeScript", "Swift"}))
    selected_lang = ObservableSingleValue[str | None]("Python")
    
    lang_widget = IQtSingleListSelection(
        selected_lang,
        languages,
        formatter=lambda x: f"• {x}",
        allow_deselection=True
    )
    left_layout.addWidget(lang_widget)
    lang_display = IQtDisplayValue(
        selected_lang,
        formatter=lambda x: f"Selected: {x if x else 'None'}"
    )
    left_layout.addWidget(lang_display)
    
    # Right column - cities
    right_layout = QVBoxLayout()
    layout.addLayout(right_layout)
    
    right_layout.addWidget(QLabel("<h3>Cities</h3>"))
    cities = frozenset({"New York", "London", "Paris", "Tokyo", "Sydney", "Berlin", "Mumbai", "Toronto"})
    city_observable = ObservableOptionalSelectionOption[str](None, cities)
    
    city_widget = IQtSingleListSelection(
        selected_option=city_observable,
        available_options=None,
        order_by_callable=lambda x: x,
        formatter=lambda x: f"📍 {x}",
        allow_deselection=True
    )
    right_layout.addWidget(city_widget)
    city_display = IQtDisplayValue(
        city_observable.selected_option_hook,
        formatter=lambda x: f"Selected city: {x if x else 'None'}"
    )
    right_layout.addWidget(city_display)
    
    # Button to add/remove options dynamically
    def add_lang():
        current_langs = set(languages.value)
        new_langs = {"Kotlin", "Dart", "Scala", "Haskell", "Elixir"}
        available = new_langs - current_langs
        if available:
            lang_to_add = available.pop()
            languages.add(lang_to_add)
            print(f"Added: {lang_to_add}")
    
    def remove_lang():
        current_langs = set(languages.value)
        if len(current_langs) > 1:
            langs_list = list(current_langs)
            # Don't remove the currently selected language
            if selected_lang.value in langs_list:
                langs_list.remove(selected_lang.value)
            if langs_list:
                lang_to_remove = langs_list[0]
                languages.remove(lang_to_remove)
                print(f"Removed: {lang_to_remove}")
    
    button_layout = QVBoxLayout()
    add_button = QPushButton("Add Language")
    add_button.clicked.connect(add_lang)
    button_layout.addWidget(add_button)
    
    remove_button = QPushButton("Remove Language")
    remove_button.clicked.connect(remove_lang)
    button_layout.addWidget(remove_button)
    
    right_layout.addLayout(button_layout)
    
    # Show window and run
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

