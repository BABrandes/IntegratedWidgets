from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QPushButton, QFrame, QMenu, QApplication, QFileDialog
from PySide6.QtCore import Qt, QPoint, QDir
from PySide6.QtGui import QAction
from enum import Enum, auto
from python.common.logging_utils import Logger
from pathlib import Path
from python.common import utils
from python.gui.custom_widgets.observable_widgets.base_observable_frame import BaseFrame_With_Observable

from observables import ObservableSingleValue

BUTTON_SELECT_WIDTH: int = 130

class LookingForFileOrDirectory_Keys(Enum):
    FILE = auto()
    FILE_ONLY_READ = auto()
    DIRECTORY = auto()
    
class ObsQSelectPath(BaseFrame_With_Observable[ObservableSingleValue[Path|None]], QFrame):
    """
    A widget that allows the user to select a file or directory.
    The widget will display the path to the selected file or directory.
    The widget will also allow the user to select a file or directory.
    The widget will also allow the user to clear the selected file or directory.
    The widget will also allow the user to add a listener to the widget.
    The widget will also allow the user to remove a listener from the widget.
    The widget will also allow the user to clear all listeners from the widget.
    
    Args:
        initial_path_to_directory_for_prompt: The initial path to the directory for the prompt. If None, the home directory will be used.
        looking_for: The type of file or directory to look for.
        suggested_file_name_without_extension: The suggested file name without extension. If None, no suggested file name will be used.
        file_extension_without_dot: The file extension without the dot. If None, no file extension will be used.
        logger: The logger to use. If None, no logger will be used.
    """

    def __init__(
            self,
            initial_path_or_observable: Path | None | ObservableSingleValue[Path|None],
            looking_for: LookingForFileOrDirectory_Keys,
            suggested_file_name_without_extension: str | None = None,
            file_extension_without_dot: str | None = None,
            logger: Logger | None = None):
        
        # Step 1: Initialize the observable

        if isinstance(initial_path_or_observable, ObservableSingleValue):
            observable = initial_path_or_observable
        else:
            observable = ObservableSingleValue(initial_path_or_observable)
            
        super().__init__(observable=observable)

        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(0)

        # Step 2: Initialize the instance fields
        self._looking_for: LookingForFileOrDirectory_Keys = looking_for
        self._suggested_file_name_without_extension = suggested_file_name_without_extension
        self._file_extension_without_dot = file_extension_without_dot
        self._logger = logger
        
        # Initialize path suggestion with better logic
        if observable.value is not None:
            self._path_suggestion = observable.value
        elif looking_for == LookingForFileOrDirectory_Keys.DIRECTORY:
            self._path_suggestion = Path.home()
        else:  # FILE
            if suggested_file_name_without_extension is not None and file_extension_without_dot is not None:
                self._path_suggestion = Path.home() / f"{suggested_file_name_without_extension}.{file_extension_without_dot}"
            else:
                self._path_suggestion = Path.home()
        
        self._message: str = ""

        # Step 5: Create the layout
        hbox_layout = QHBoxLayout(self)
        hbox_layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        hbox_layout.setSpacing(10)

        # Step 6: Create the path label
        placeholder_text = "No file selected" if looking_for == LookingForFileOrDirectory_Keys.FILE or looking_for == LookingForFileOrDirectory_Keys.FILE_ONLY_READ else "No directory selected"
        self._path_label = QLabel(placeholder_text)
        self._path_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._path_label.setToolTip("Click to select a path")

        # Step 7: Create the scroll area
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setWidget(self._path_label)
        self._scroll_area.setFixedHeight(35)
        self._scroll_area.setToolTip("Click to select a path")

        # Step 8: Add the scroll area to the group box layout
        hbox_layout.addWidget(self._scroll_area)

        # Step 9: Create the select button with appropriate text
        button_text = "Select File" if looking_for == LookingForFileOrDirectory_Keys.FILE or looking_for == LookingForFileOrDirectory_Keys.FILE_ONLY_READ else "Select Directory"
        select_directory_button = QPushButton(button_text)
        select_directory_button.setToolTip(f"Click to {button_text.lower()}")
        select_directory_button.setFixedWidth(BUTTON_SELECT_WIDTH)
        hbox_layout.addWidget(select_directory_button)

        # Step 10: Add functionality
        select_directory_button.clicked.connect(self.update_observable)

        # Step 11: Open the directory when the label is clicked
        self._scroll_area.setCursor(Qt.CursorShape.PointingHandCursor)
        self._path_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self._path_label.mousePressEvent = self._mouse_press_event

        self._scroll_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._scroll_area.customContextMenuRequested.connect(self._show_context_menu)
        
        self._path_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._path_label.customContextMenuRequested.connect(self._show_context_menu)

        self.construction_finished()

    def update_observable(self):

        # Step 1: Get the path from user selection

        path_to_show_initially: Path
        path_selected: Path | None
        
        if self._looking_for == LookingForFileOrDirectory_Keys.DIRECTORY:
            # For directory selection, use the current value or path suggestion
            if self.observable.value is not None:
                path_to_show_initially = self.observable.value
            else:
                path_to_show_initially = self._path_suggestion

            dialog = QFileDialog()
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            dialog.setFileMode(QFileDialog.FileMode.Directory)
            dialog.setWindowTitle("Select a directory")

            if dialog.exec():
                path_selected = Path(dialog.selectedFiles()[0])
            else:
                self._message = "Nothing happened."
                return
            
        elif self._looking_for == LookingForFileOrDirectory_Keys.FILE or self._looking_for == LookingForFileOrDirectory_Keys.FILE_ONLY_READ:    
            # For file selection, validate required parameters
            if self._file_extension_without_dot is None:
                raise ValueError("file_extension_without_dot is required when looking for a file")
            
            # Determine the initial path to show
            if self.observable.value is not None:
                path_to_show_initially = self.observable.value
            else:
                path_to_show_initially = self._path_suggestion
            
            # Get the directory path from the file path
            # If path_to_show_initially is a file that exists, use its parent directory
            # If it's a directory or doesn't exist, use it as the directory

            dialog = QFileDialog()
            if path_to_show_initially.exists() and path_to_show_initially.is_file() and str(path_to_show_initially).endswith(f".{self._file_extension_without_dot}"):
                dialog.setDirectory(QDir(path_to_show_initially.parent))
                dialog.selectFile(path_to_show_initially.name)
            else:
                directory_path = path_to_show_initially.parent
                while not directory_path.exists():
                    directory_path = directory_path.parent
                dialog.setDirectory(QDir(directory_path))
                if self._suggested_file_name_without_extension is not None:
                    dialog.selectFile(f"{self._suggested_file_name_without_extension}.{self._file_extension_without_dot}")
                else:
                    dialog.selectFile(f".{self._file_extension_without_dot}")
            if self._looking_for == LookingForFileOrDirectory_Keys.FILE_ONLY_READ:
                dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            else:
                dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setWindowTitle("Select a file")

            if dialog.exec():
                path_selected = Path(dialog.selectedFiles()[0])
            else:
                self._message = "Nothing happened."
                return
        else:
            raise ValueError(f"Invalid looking_for: {self._looking_for}")
        
        # Set the path value of the observable
        self._message = self.create_message_for_path_change(self.observable.value, path_selected)
        self._path_suggestion = path_selected if path_selected is not None else self._path_suggestion
        self.observable.set_value(path_selected)

    def _show_context_menu(self, position: QPoint):
        menu = QMenu(self)

        # Add copy path action (only if there's a path to copy)
        if self.observable.value is not None:
            action_copy_path = QAction("Copy", self)
            action_copy_path.triggered.connect(self._copy_path_to_clipboard)
            menu.addAction(action_copy_path)

        action_clear_path = QAction("Clear path", self)
        action_clear_path.triggered.connect(lambda: self.observable.set_value(None))
        menu.addAction(action_clear_path)

        # Show the menu at the cursor's position relative to the widget
        menu.exec(self._scroll_area.mapToGlobal(position))

    def _copy_path_to_clipboard(self):
        if self.observable.value is not None:
            clipboard = QApplication.clipboard()
            clipboard.setText(str(self.observable.value))

    def update_widget_non_empty(self):

        if self.observable.value is None:
            self._path_label.setText("No file selected" if self._looking_for == LookingForFileOrDirectory_Keys.FILE else "No directory selected")
        else:
            self._path_label.setText(str(self.observable.value))

        scrollbar = self._scroll_area.horizontalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_widget_empty(self) -> None:
        self._path_label.setText("No file selected" if self._looking_for == LookingForFileOrDirectory_Keys.FILE else "No directory selected")

    def _mouse_press_event(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.update_observable()

    @property
    def path(self) -> Path | None:
        return self.observable.value
    
    @property
    def message(self) -> str:
        return self._message

    def set_path_suggestion(self, path_suggestion: Path):
        self._path_suggestion = path_suggestion

    @classmethod
    def create_message_for_path_change(cls, previous_path: Path | None, new_path: Path | None) -> str:
        if previous_path == new_path:
            return "Nothing happened"
        else:
            match previous_path, new_path:
                case None, None:
                    return "Nothing happened"
                case None, Path():
                    return f"Path set to '{str(new_path)}'"
                case Path(), None:
                    return f"Path '{str(previous_path)}' removed"
                case Path(), Path():
                    return f"Path changed from '{utils.path_strings_with_only_connecting_node(previous_path, new_path)[0]}' to '{utils.path_strings_with_only_connecting_node(previous_path, new_path)[1]}'"
                case _:
                    raise ValueError(f"Invalid previous_path: {previous_path} and new_path: {new_path}")