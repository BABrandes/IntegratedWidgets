"""ControlledRangeSlider widget for selecting a range with two handles.

This module provides a rich range slider widget with min/max handles and a center
handle for simultaneous movement. The widget uses a tick-based coordinate system
for precise, discrete value control.

Key Features:
    - Two-handle range selection (min and max)
    - Center handle for moving entire range
    - Tick-based discrete value system
    - Keyboard navigation support
    - Horizontal and vertical orientations
    - Customizable visual appearance
    - Display-only mode (hide handles)

Example Usage:
    ```python
    from integrated_widgets.controlled_widgets import ControlledRangeSlider
    from integrated_widgets.util.base_controller import BaseController
    from PySide6.QtCore import Qt
    
    controller = MyController()
    slider = ControlledRangeSlider(controller, parent)
    slider.setTickRange(0, 1000)
    slider.setTickStep(10)
    slider.setTickValue(200, 800)
    slider.rangeChanged.connect(on_range_changed)
    ```

Classes:
    ControlledRangeSlider: The main range slider widget
"""
from __future__ import annotations

from typing import Literal, Optional, Any
from logging import Logger

from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QMouseEvent, QPaintEvent, QKeyEvent
from PySide6.QtWidgets import QWidget
from integrated_widgets.controllers.core.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget


class ControlledRangeSlider(BaseControlledWidget, QWidget):
    """A compact two-handle range slider rendered in a single widget.

    This widget provides a rich range selection interface with two draggable handles
    for selecting a minimum and maximum value, plus a center handle for moving both
    handles simultaneously. The widget operates on a tick-based system where values
    are discrete integer positions, ensuring precise control over the selected range.
    
    Architecture:
        The widget uses a tick-based coordinate system internally, where all positions
        are represented as integer tick values. This allows for precise snapping behavior
        and eliminates floating-point precision issues. Controllers using this widget
        can map these tick values to any desired domain (e.g., physical units, dates).
    
    Primary API (tick-based nomenclature):
        - setTickRange(min_tick, max_tick): Set the range of available ticks
        - setTickValue(min_tick_value, max_tick_value): Set current tick values
        - getTickRange() -> (min_tick_value, max_tick_value): Get current tick values
        - setTickStep(tick_step): Set the step size between ticks
        - setMinimumTickGap(tick_gap): Set minimum gap between min and max ticks
        - setShowHandles(show): Toggle visibility of handles and selection
        - setAllowZeroRange(allow): Control whether min and max can be equal
    
    Visual Customization:
        - setCenterBarWidth(width): Adjust the width of the center drag handle
        - setHighlightColor(color): Set the color for the active handle highlight
        - setHighlightThickness(thickness): Set the thickness of the highlight arc
    
    Signals:
        - rangeChanged(min_tick_value, max_tick_value): Emitted whenever the range
          changes, including during drag operations and programmatic updates
        - sliderMoved(min_tick_value, max_tick_value): Emitted continuously while
          the user is dragging a handle
    
    Interaction Model:
        - Left-click and drag the min/max handles to adjust individual bounds
        - Left-click and drag the center handle to move the entire range
        - Click outside handles to jump the nearest handle to that position
        - Use arrow keys to nudge the active handle (PageUp/PageDown for larger steps)
        - Use Home/End keys to move handles to extremes
    
    Backward Compatibility:
        For compatibility with older code, non-tick-prefixed methods are available:
        - setRange(), setValue(), getRange(), setStep(), setMinimumGap()
    
    Example:
        ```python
        # Create a range slider with tick-based values
        controller = MyController()
        slider = ControlledRangeSlider(controller, parent)
        
        # Configure the tick domain (0-1000 with steps of 10)
        slider.setTickRange(0, 1000)
        slider.setTickStep(10)
        slider.setMinimumTickGap(20)  # Handles must be at least 20 ticks apart
        
        # Set initial selection
        slider.setTickValue(200, 800)
        
        # Connect to signals
        slider.rangeChanged.connect(on_range_changed)
        slider.sliderMoved.connect(on_slider_moved)
        
        # Hide handles for display-only mode
        slider.setShowHandles(False)
        ```
    
    Args:
        controller: The BaseController managing this widget's state and behavior
        parent_of_widget: Optional parent QWidget for this widget
        orientation: Qt.Orientation.Horizontal or Qt.Orientation.Vertical
        logger: Optional logger for debugging; if None, uses controller's logger
    """

    #: Signal emitted whenever the range changes (programmatically or via user interaction).
    #: Parameters: (min_tick_value: int, max_tick_value: int)
    rangeChanged: Signal = Signal(int, int)
    
    #: Signal emitted continuously while a handle is being dragged by the user.
    #: Parameters: (min_tick_value: int, max_tick_value: int)
    sliderMoved: Signal = Signal(int, int)

    def __init__(self, controller: BaseController[Any, Any], parent_of_widget: Optional[QWidget] = None, orientation: Qt.Orientation = Qt.Orientation.Horizontal, logger: Optional[Logger] = None) -> None:
        """Initialize the ControlledRangeSlider widget.
        
        Sets up all internal state, visual properties, and widget configuration
        for a fully-functional range slider with default settings.
        """
        BaseControlledWidget.__init__(self, controller, logger)
        QWidget.__init__(self, parent_of_widget)
        self._orientation = orientation

        # Tick domain - all values are discrete integer positions
        self._tick_min_bound = 0  # minimum boundary of the available tick range
        self._tick_max_bound = 100  # maximum boundary of the available tick range
        self._tick_min_value = 0  # current position of the min handle
        self._tick_max_value = 100  # current position of the max handle
        self._tick_step = 1  # step size between ticks
        self._allow_zero_range = True  # whether min and max can be equal
        self._min_tick_gap = 0  # minimal gap between max and min tick values
        self._show_handles = True  # whether to show handles and selection

        # Drag state - tracks which handle is being dragged and related data
        self._dragging_min = False  # True when min handle is being dragged
        self._dragging_max = False  # True when max handle is being dragged
        self._dragging_center = False  # True when center handle is being dragged
        self._active_handle: Literal["min", "max", "center"] = "min"  # which handle was last interacted with
        self._last_mouse_pos = QPoint()  # last recorded mouse position during drag
        self._center_init_min = 0  # min value when center drag started
        self._center_init_max = 0  # max value when center drag started
        self._press_value = 0  # tick value where center drag was initiated

        # Visuals - colors, sizes, and styling
        self._handle_size = 14  # diameter of the circular handles
        self._track_thickness = 4  # thickness of the slider track
        self._track_color = QColor(200, 200, 200)  # background track color
        self._range_color = QColor(120, 170, 230)  # selected range color
        self._handle_fill = QColor(245, 245, 245)  # handle interior color
        self._handle_border = QColor(160, 160, 160)  # handle border color
        # Center handle uses same colors as end handles
        self._center_fill = self._handle_fill  # center handle interior color
        self._center_border = self._handle_border  # center handle border color
        # Center handle sizing (for horizontal slider: vertical bar; for vertical slider: horizontal bar)
        self._center_bar_width = 12  # width of the center drag handle bar
        self._center_bar_extra = 0  # reserved for future use; currently unused
        self._highlight_color = QColor(80, 140, 255, 200)  # active handle highlight color
        self._highlight_thickness = 2  # thickness of the highlight arc

        # Basic size and interaction setup
        if self._orientation == Qt.Orientation.Horizontal:
            self.setMinimumHeight(32)
        else:
            self.setMinimumWidth(32)
        self.setMouseTracking(True)  # enable mouse move events without button press
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # allow keyboard focus

    ###########################################################################
    # Public API
    ###########################################################################
    def setTickRange(self, min_tick: int, max_tick: int) -> None:
        """Set the available range of tick positions for the slider.
        
        This defines the bounds within which the min and max handles can move.
        Existing tick values will be clamped to fit within the new range.
        
        Args:
            min_tick: The minimum tick position (must be less than max_tick)
            max_tick: The maximum tick position (must be greater than min_tick)
        
        Note:
            If min_tick >= max_tick, the call is silently ignored.
            Current tick values are automatically adjusted to remain valid.
        """
        if min_tick >= max_tick:
            return
        self._tick_min_bound = min_tick
        self._tick_max_bound = max_tick
        # Clamp current values
        self._tick_min_value = max(self._tick_min_bound, min(self._tick_min_value, self._tick_max_bound))
        self._tick_max_value = max(self._tick_min_value, min(self._tick_max_value, self._tick_max_bound))
        self.update()

    def setTickStep(self, tick_step: int) -> None:
        """Set the step size for tick value increments.
        
        When dragging handles or using keyboard navigation, the tick values
        will snap to multiples of this step size.
        
        Args:
            tick_step: The step size between valid tick positions (must be > 0)
        
        Note:
            If tick_step <= 0, it is automatically clamped to 1.
        """
        if tick_step <= 0:
            tick_step = 1
        self._tick_step = tick_step

    def setAllowZeroRange(self, allow: bool) -> None:
        """Control whether the min and max handles can occupy the same position.
        
        When False, the minimum gap between handles will be at least one tick_step.
        When True, the handles can overlap completely.
        
        Args:
            allow: If True, allow min_tick_value == max_tick_value; if False, enforce
                   a minimum gap of at least one tick_step
        """
        self._allow_zero_range = allow

    def setTickValue(self, min_tick_value: int, max_tick_value: int) -> None:
        """Set the current tick values for both handles.
        
        This method automatically clamps the values to the valid tick range and
        enforces the minimum gap requirement. If the provided values are too close,
        they will be adjusted based on the active handle to maintain the required gap.
        
        Args:
            min_tick_value: The desired minimum tick value
            max_tick_value: The desired maximum tick value
        
        Emits:
            rangeChanged: Only if the values actually changed after validation
        
        Note:
            - Values are automatically swapped if min > max
            - Values are clamped to [_tick_min_bound, _tick_max_bound]
            - The required gap (_min_tick_gap or _tick_step) is enforced
            - If values are too close, expansion favors the active handle's direction
        """
        if min_tick_value > max_tick_value:
            min_tick_value, max_tick_value = max_tick_value, min_tick_value
        min_tick_value = max(self._tick_min_bound, min(self._tick_max_bound, min_tick_value))
        max_tick_value = max(self._tick_min_bound, min(self._tick_max_bound, max_tick_value))
        required_gap = self._required_tick_gap()
        if max_tick_value - min_tick_value < required_gap:
            # Expand toward active handle direction when possible
            if self._active_handle == "min":
                min_tick_value = max(self._tick_min_bound, max_tick_value - required_gap)
            else:
                max_tick_value = min(self._tick_max_bound, min_tick_value + required_gap)
        if min_tick_value == self._tick_min_value and max_tick_value == self._tick_max_value:
            return
        self._tick_min_value = min_tick_value
        self._tick_max_value = max_tick_value
        self.rangeChanged.emit(self._tick_min_value, self._tick_max_value)
        self.update()

    def getTickRange(self) -> tuple[int, int]:
        """Get the current tick values for both handles.
        
        Returns:
            A tuple (min_tick_value, max_tick_value) representing the current selection
        """
        return self._tick_min_value, self._tick_max_value

    def setMinimumTickGap(self, tick_gap: int) -> None:
        """Set the minimum required gap between min and max tick values.
        
        This enforces a minimum separation between the two handles beyond what
        setAllowZeroRange() provides. Useful for ensuring a minimum range width.
        
        Args:
            tick_gap: The minimum gap in ticks (must be >= 0)
        
        Note:
            - If tick_gap < 0, it is clamped to 0
            - Current tick values are automatically re-validated after setting
            - The effective gap is max(tick_gap, tick_step) if allow_zero_range is False
        """
        if tick_gap < 0:
            tick_gap = 0
        self._min_tick_gap = tick_gap
        # Re-validate current values
        self.setTickValue(self._tick_min_value, self._tick_max_value)

    def setShowHandles(self, show: bool) -> None:
        """Set whether to show the slider handles and selection.
        
        When False, only the track is rendered, effectively creating a display-only
        mode. User interactions are also disabled in this mode.
        
        Args:
            show: If True, show handles and enable interactions; if False, display
                  only the track
        """
        self._show_handles = show
        self.update()

    # Backward compatibility methods
    def setRange(self, minimum: int, maximum: int) -> None:
        """Backward compatibility method. Use setTickRange instead.
        
        Args:
            minimum: The minimum tick position
            maximum: The maximum tick position
        
        Note:
            Deprecated: This method is provided for backward compatibility.
            New code should use setTickRange() for clearer tick-based semantics.
        """
        self.setTickRange(minimum, maximum)

    def setValue(self, min_value: int, max_value: int) -> None:
        """Backward compatibility method. Use setTickValue instead.
        
        Args:
            min_value: The minimum tick value
            max_value: The maximum tick value
        
        Note:
            Deprecated: This method is provided for backward compatibility.
            New code should use setTickValue() for clearer tick-based semantics.
        """
        self.setTickValue(min_value, max_value)

    def getRange(self) -> tuple[int, int]:
        """Backward compatibility method. Use getTickRange instead.
        
        Returns:
            A tuple (min_tick_value, max_tick_value) representing the current selection
        
        Note:
            Deprecated: This method is provided for backward compatibility.
            New code should use getTickRange() for clearer tick-based semantics.
        """
        return self.getTickRange()

    def setStep(self, step: int) -> None:
        """Backward compatibility method. Use setTickStep instead.
        
        Args:
            step: The step size between valid tick positions
        
        Note:
            Deprecated: This method is provided for backward compatibility.
            New code should use setTickStep() for clearer tick-based semantics.
        """
        self.setTickStep(step)

    def setMinimumGap(self, gap: int) -> None:
        """Backward compatibility method. Use setMinimumTickGap instead.
        
        Args:
            gap: The minimum gap in ticks between handles
        
        Note:
            Deprecated: This method is provided for backward compatibility.
            New code should use setMinimumTickGap() for clearer tick-based semantics.
        """
        self.setMinimumTickGap(gap)

    ###########################################################################
    # Painting
    ###########################################################################
    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802 (Qt override)
        """Paint the range slider widget.
        
        Rendering layers (bottom to top):
        1. Track (gray background bar)
        2. Selection (colored region between handles)
        3. Min and max handles (circular)
        4. Center handle (rounded rectangle)
        5. Active handle highlight (arc on the edge)
        
        Args:
            event: The QPaintEvent from Qt (unused)
        
        Note:
            If _show_handles is False, only the track is rendered.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = self._track_rect()
        
        # Track
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._track_color)
        painter.drawRoundedRect(track, 2, 2)
        
        # If not showing handles, only draw the track
        if not self._show_handles:
            return
            
        # Selection
        min_handle = self._handle_rect(self._tick_min_value)
        max_handle = self._handle_rect(self._tick_max_value)
        if self._orientation == Qt.Orientation.Horizontal:
            sel = QRect(min_handle.center().x(), track.y(), max_handle.center().x() - min_handle.center().x(), track.height())
        else:
            sel = QRect(track.x(), max_handle.center().y(), track.width(), min_handle.center().y() - max_handle.center().y())
        painter.setBrush(self._range_color)
        painter.drawRoundedRect(sel, 2, 2)
        # Handles
        painter.setPen(QPen(self._handle_border, 1))
        painter.setBrush(self._handle_fill)
        painter.drawEllipse(min_handle)
        painter.drawEllipse(max_handle)
        # Center handle (squircle-like rounded rect), same color as handles
        center = self._center_handle_rect(sel)
        painter.setPen(QPen(self._center_border, 1))
        painter.setBrush(self._center_fill)
        painter.drawRoundedRect(center, center.height() // 2, center.height() // 2)
        # Edge-shine on active handle
        self._draw_edge_shine(painter, min_handle, which="min")
        self._draw_edge_shine(painter, max_handle, which="max")
        if self._active_handle == "center":
            pen = QPen(self._highlight_color, self._highlight_thickness)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(center.adjusted(0, 0, 0, 0), center.height() // 2, center.height() // 2)

    ###########################################################################
    # Mouse handling
    ###########################################################################
    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle mouse press events for initiating drag operations.
        
        Interaction logic:
        1. If clicking on min handle → drag min handle
        2. If clicking on max handle → drag max handle
        3. If clicking on center handle → drag both handles together
        4. If clicking elsewhere → jump nearest handle to that position
        
        Args:
            event: The QMouseEvent from Qt
        
        Note:
            Only left-button clicks are processed. Interactions are disabled
            if _show_handles is False.
        """
        if event.button() != Qt.MouseButton.LeftButton or not self._show_handles:
            return
        pos = event.pos()
        if self._handle_rect(self._tick_min_value).contains(pos):
            self._dragging_min = True
            self._active_handle = "min"
        elif self._handle_rect(self._tick_max_value).contains(pos):
            self._dragging_max = True
            self._active_handle = "max"
        else:
            sel = self._selection_rect()
            if self._center_handle_rect(sel).contains(pos):
                self._dragging_center = True
                self._active_handle = "center"
                self._center_init_min = self._tick_min_value
                self._center_init_max = self._tick_max_value
                self._press_value = self._value_from_pos(pos)
            else:
                # Move nearest handle
                if self._orientation == Qt.Orientation.Horizontal:
                    dist_min = abs(pos.x() - self._handle_rect(self._tick_min_value).center().x())
                    dist_max = abs(pos.x() - self._handle_rect(self._tick_max_value).center().x())
                else:
                    dist_min = abs(pos.y() - self._handle_rect(self._tick_min_value).center().y())
                    dist_max = abs(pos.y() - self._handle_rect(self._tick_max_value).center().y())
                if dist_min <= dist_max:
                    self._dragging_min = True
                    self._active_handle = "min"
                else:
                    self._dragging_max = True
                    self._active_handle = "max"
        self._last_mouse_pos = pos

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle mouse move events during drag operations.
        
        Update behavior:
        - Min handle drag: Adjust min value, respect gap from max
        - Max handle drag: Adjust max value, respect gap from min
        - Center handle drag: Move both handles maintaining their relative distance
        
        All movements are snapped to tick_step increments and clamped to the
        valid tick range.
        
        Args:
            event: The QMouseEvent from Qt
        
        Emits:
            sliderMoved: On every movement during drag
            rangeChanged: On every movement during drag
        
        Note:
            Only processes events if a drag operation is active and handles are visible.
        """
        if not (self._dragging_min or self._dragging_max or self._dragging_center) or not self._show_handles:
            return
        value = self._value_from_pos(event.pos())
        value = (value // self._tick_step) * self._tick_step
        min_value, max_value = self._tick_min_value, self._tick_max_value
        gap = self._required_tick_gap()
        if self._dragging_min:
            min_value = max(self._tick_min_bound, min(value, self._tick_max_value - gap))
        elif self._dragging_max:
            max_value = min(self._tick_max_bound, max(value, self._tick_min_value + gap))
        elif self._dragging_center:
            init_min = self._center_init_min
            init_max = self._center_init_max
            width = init_max - init_min
            delta = ((value - self._press_value) // self._tick_step) * self._tick_step
            delta = max(self._tick_min_bound - init_min, min(delta, self._tick_max_bound - init_max))
            min_value = init_min + delta
            max_value = min_value + width
        if (min_value, max_value) != (self._tick_min_value, self._tick_max_value):
            self._tick_min_value, self._tick_max_value = min_value, max_value
            self.sliderMoved.emit(self._tick_min_value, self._tick_max_value)
            self.rangeChanged.emit(self._tick_min_value, self._tick_max_value)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle mouse release events to end drag operations.
        
        Clears all drag state flags, but does not change which handle is active.
        
        Args:
            event: The QMouseEvent from Qt
        """
        self._dragging_min = False
        self._dragging_max = False
        self._dragging_center = False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle keyboard navigation for the active handle.
        
        Keyboard shortcuts:
        - Arrow keys: Nudge active handle by one tick_step
          (Left/Right for horizontal, Up/Down for vertical)
        - PageUp/PageDown: Nudge active handle by 10 × tick_step
        - Home: Move active handle to minimum extreme (respecting gap)
        - End: Move active handle to maximum extreme (respecting gap)
        
        Args:
            event: The QKeyEvent from Qt
        
        Note:
            Keyboard navigation is disabled if _show_handles is False.
            For center handle, arrow keys move the entire range together.
        """
        if not self._show_handles:
            return
        key = event.key()
        delta = self._tick_step
        if self._orientation == Qt.Orientation.Horizontal:
            if key == Qt.Key.Key_Left:
                self._nudge_active(-delta)
                return
            if key == Qt.Key.Key_Right:
                self._nudge_active(delta)
                return
        else:
            if key == Qt.Key.Key_Down:
                self._nudge_active(-delta)
                return
            if key == Qt.Key.Key_Up:
                self._nudge_active(delta)
                return
        if key == Qt.Key.Key_PageDown:
            self._nudge_active(-10 * delta)
            return
        if key == Qt.Key.Key_PageUp:
            self._nudge_active(10 * delta)
            return
        if key == Qt.Key.Key_Home:
            if self._active_handle == "min":
                self.setTickValue(self._tick_min_bound, self._tick_max_value)
            else:
                self.setTickValue(self._tick_min_value, max(self._tick_min_value + self._required_tick_gap(), self._tick_min_bound))
            return
        if key == Qt.Key.Key_End:
            if self._active_handle == "max":
                self.setTickValue(self._tick_min_value, self._tick_max_bound)
            else:
                self.setTickValue(min(self._tick_max_bound - self._required_tick_gap(), self._tick_max_bound), self._tick_max_value)
            return
        super().keyPressEvent(event)

    def _nudge_active(self, delta: int) -> None:
        """Move the active handle by a delta amount.
        
        Behavior per handle:
        - Min handle: Move min by delta, clamped to valid range
        - Max handle: Move max by delta, clamped to valid range
        - Center handle: Move both handles by delta, maintaining their gap
        
        Args:
            delta: The number of ticks to move (positive or negative)
        
        Note:
            Automatically enforces the required tick gap and clamps to valid range.
        """
        if not self._show_handles:
            return
        if self._active_handle == "min":
            new_min = max(self._tick_min_bound, min(self._tick_min_value + delta, self._tick_max_value - self._required_tick_gap()))
            self.setTickValue(new_min, self._tick_max_value)
        elif self._active_handle == "max":
            new_max = min(self._tick_max_bound, max(self._tick_max_value + delta, self._tick_min_value + self._required_tick_gap()))
            self.setTickValue(self._tick_min_value, new_max)
        else:
            init_min = self._tick_min_value
            init_max = self._tick_max_value
            delta = max(self._tick_min_bound - init_min, min(delta, self._tick_max_bound - init_max))
            self.setTickValue(init_min + delta, init_max + delta)

    ###########################################################################
    # Geometry helpers
    ###########################################################################
    def _track_rect(self) -> QRect:
        """Calculate the rectangle for the slider track.
        
        The track is centered in the widget with margins on both ends to
        accommodate the handle size.
        
        Returns:
            QRect representing the track position and size
        """
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(self._handle_size // 2, (self.height() - self._track_thickness) // 2, self.width() - self._handle_size, self._track_thickness)
        return QRect((self.width() - self._track_thickness) // 2, self._handle_size // 2, self._track_thickness, self.height() - self._handle_size)

    def _handle_rect(self, value: int) -> QRect:
        """Calculate the rectangle for a handle at a given tick value.
        
        Args:
            value: The tick value at which to position the handle
        
        Returns:
            QRect representing the handle's bounding box, or empty QRect if handles hidden
        
        Note:
            For horizontal orientation, handles move left-right along the track.
            For vertical orientation, handles move bottom-top (higher values = higher position).
        """
        if not self._show_handles:
            return QRect()
        track = self._track_rect()
        rng = max(1, self._tick_max_bound - self._tick_min_bound)
        if self._orientation == Qt.Orientation.Horizontal:
            x = track.x() + int((value - self._tick_min_bound) * track.width() / rng)
            return QRect(x - self._handle_size // 2, (self.height() - self._handle_size) // 2, self._handle_size, self._handle_size)
        else:
            y = track.y() + track.height() - int((value - self._tick_min_bound) * track.height() / rng)
            return QRect((self.width() - self._handle_size) // 2, y - self._handle_size // 2, self._handle_size, self._handle_size)

    def _value_from_pos(self, pos: QPoint) -> int:
        """Convert a mouse position to a tick value.
        
        Maps the mouse position onto the track and calculates the corresponding
        tick value. The result is clamped to [0.0, 1.0] relative position before
        scaling to the tick range.
        
        Args:
            pos: The QPoint in widget coordinates
        
        Returns:
            The tick value corresponding to the mouse position
        
        Note:
            For horizontal: left edge = min_tick, right edge = max_tick
            For vertical: bottom edge = min_tick, top edge = max_tick
        """
        track = self._track_rect()
        rng = self._tick_max_bound - self._tick_min_bound
        if rng <= 0:
            return self._tick_min_bound
        if self._orientation == Qt.Orientation.Horizontal:
            rel = (pos.x() - track.x()) / max(1, track.width())
        else:
            rel = 1.0 - (pos.y() - track.y()) / max(1, track.height())
        rel = max(0.0, min(1.0, rel))
        return int(self._tick_min_bound + rel * rng)

    def _required_tick_gap(self) -> int:
        """Calculate the minimum required gap between handles.
        
        Returns:
            The effective minimum gap, which is the maximum of:
            - _min_tick_gap (explicitly set minimum)
            - _tick_step (if allow_zero_range is False)
            - 0 (if allow_zero_range is True and no explicit gap set)
        """
        base = 0 if self._allow_zero_range else self._tick_step
        return max(self._min_tick_gap, base)

    def _selection_rect(self) -> QRect:
        """Calculate the rectangle representing the selected range.
        
        This is the colored region between the min and max handles.
        
        Returns:
            QRect representing the selection region
        
        Note:
            For horizontal: width spans between handle centers
            For vertical: height spans between handle centers
        """
        track = self._track_rect()
        min_handle = self._handle_rect(self._tick_min_value)
        max_handle = self._handle_rect(self._tick_max_value)
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(min_handle.center().x(), track.y(), max_handle.center().x() - min_handle.center().x(), track.height())
        else:
            return QRect(track.x(), max_handle.center().y(), track.width(), min_handle.center().y() - max_handle.center().y())

    def _center_handle_rect(self, selection: QRect) -> QRect:
        """Calculate the rectangle for the center drag handle.
        
        The center handle is a bar perpendicular to the slider orientation,
        positioned at the center of the selection region.
        
        Args:
            selection: The QRect of the selection region (from _selection_rect)
        
        Returns:
            QRect representing the center handle's bounding box
        
        Note:
            For horizontal slider: vertical bar (narrow width, handle height)
            For vertical slider: horizontal bar (narrow height, handle width)
        """
        _ = self._track_rect()
        cx = selection.x() + selection.width() // 2
        cy = selection.y() + selection.height() // 2
        if self._orientation == Qt.Orientation.Horizontal:
            # Vertical bar centered; same vertical size as handle
            w = self._center_bar_width
            h = self._handle_size
            x = cx - w // 2
            y = (self.height() - h) // 2
            return QRect(x, y, w, h)
        else:
            # Horizontal bar centered; same horizontal size as handle
            h = self._center_bar_width
            w = self._handle_size
            y = cy - h // 2
            x = (self.width() - w) // 2
            return QRect(x, y, w, h)

    def _draw_edge_shine(self, painter: QPainter, handle_rect: QRect, which: str) -> None:
        """Draw a highlight arc on the edge of the active handle.
        
        The arc is drawn on the outward-facing edge of the handle to indicate
        which handle is currently active.
        
        Args:
            painter: The QPainter to draw with
            handle_rect: The bounding rectangle of the handle
            which: Either "min" or "max" to identify which handle
        
        Note:
            Only draws if the specified handle is the active one.
            Arc position changes based on orientation and which handle.
        """
        if which not in ("min", "max"):
            return
        if (which == "min" and self._active_handle != "min") or (which == "max" and self._active_handle != "max"):
            return
        pen = QPen(self._highlight_color, self._highlight_thickness)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # Draw a small arc on the outside edge
        start_deg = 0
        span_deg = 60
        if self._orientation == Qt.Orientation.Horizontal:
            if which == "min":
                start_deg = 150
            else:  # max
                start_deg = -30
        else:
            if which == "min":  # bottom
                start_deg = 240
            else:  # top
                start_deg = 60
        painter.drawArc(handle_rect, int(start_deg * 16), int(span_deg * 16))

    # Public customization APIs
    def setCenterBarWidth(self, width: int) -> None:
        """Set the width of the center drag handle bar.
        
        This controls how wide the center handle appears. The value is automatically
        clamped to a reasonable range.
        
        Args:
            width: The desired width in pixels (will be clamped to [4, 64])
        """
        self._center_bar_width = max(4, min(64, width))
        self.update()

    def setHighlightColor(self, color: QColor) -> None:
        """Set the color used for the active handle highlight.
        
        The highlight is drawn as an arc on the edge of the active handle and
        as a border around the center handle when active.
        
        Args:
            color: The QColor to use for highlights
        """
        self._highlight_color = color
        self.update()

    def setHighlightThickness(self, thickness: int) -> None:
        """Set the thickness of the active handle highlight arc.
        
        This controls the pen width used to draw the highlight. The value is
        automatically clamped to a reasonable range.
        
        Args:
            thickness: The desired thickness in pixels (will be clamped to [1, 6])
        """
        self._highlight_thickness = max(1, min(6, thickness))
        self.update()


