from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt, Signal, QRect, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QMouseEvent, QPaintEvent
from PySide6.QtWidgets import QWidget


class GuardedRangeSlider(QWidget):
    """A compact two-handle range slider rendered in a single widget.

    This widget operates on a tick-based system where values are discrete integer positions.
    
    Primary API (tick-based nomenclature):
    - setTickRange(min_tick, max_tick) - Set the range of available ticks
    - setTickValue(min_tick_value, max_tick_value) - Set current tick values
    - getTickRange() -> (min_tick_value, max_tick_value) - Get current tick values
    - setTickStep(tick_step) - Set the step size between ticks
    - setMinimumTickGap(tick_gap) - Set minimum gap between min and max ticks
    
    Emits:
    - rangeChanged(min_tick_value, max_tick_value) whenever the range changes
    - sliderMoved(min_tick_value, max_tick_value) while dragging
    
    Backward compatibility methods are also available (setRange, setValue, etc.)
    """

    rangeChanged: Signal = Signal(int, int)
    sliderMoved: Signal = Signal(int, int)

    def __init__(self, owner: QWidget, orientation: Qt.Orientation = Qt.Orientation.Horizontal) -> None:
        super().__init__(owner)
        self._owner = owner
        self._orientation = orientation

        # Tick domain - all values are discrete integer positions
        self._min_tick = 0  # minimum available tick position
        self._max_tick = 100  # maximum available tick position
        self._min_tick_value = 0  # current minimum tick value
        self._max_tick_value = 100  # current maximum tick value
        self._tick_step = 1  # step size between ticks
        self._allow_zero_range = True  # whether min and max can be equal
        self._min_tick_gap = 0  # minimal gap between max and min tick values
        self._show_handles = True  # whether to show handles and selection

        # Drag state
        self._dragging_min = False
        self._dragging_max = False
        self._dragging_center = False
        self._active_handle: Literal["min", "max", "center"] = "min"
        self._last_mouse_pos = QPoint()
        self._center_init_min = 0
        self._center_init_max = 0
        self._press_value = 0

        # Visuals
        self._handle_size = 14
        self._track_thickness = 4
        self._track_color = QColor(200, 200, 200)
        self._range_color = QColor(120, 170, 230)
        self._handle_fill = QColor(245, 245, 245)
        self._handle_border = QColor(160, 160, 160)
        # Center handle uses same colors as end handles
        self._center_fill = self._handle_fill
        self._center_border = self._handle_border
        # Center handle sizing (for horizontal slider: vertical bar; for vertical slider: horizontal bar)
        self._center_bar_width = 12
        self._center_bar_extra = 0  # match handle length
        self._highlight_color = QColor(80, 140, 255, 200)
        self._highlight_thickness = 2

        # Basic size
        if self._orientation == Qt.Orientation.Horizontal:
            self.setMinimumHeight(32)
        else:
            self.setMinimumWidth(32)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    ###########################################################################
    # Public API
    ###########################################################################
    def setTickRange(self, min_tick: int, max_tick: int) -> None:
        if min_tick >= max_tick:
            return
        self._min_tick = min_tick
        self._max_tick = max_tick
        # Clamp current values
        self._min_tick_value = max(self._min_tick, min(self._min_tick_value, self._max_tick))
        self._max_tick_value = max(self._min_tick_value, min(self._max_tick_value, self._max_tick))
        self.update()

    def setTickStep(self, tick_step: int) -> None:
        if tick_step <= 0:
            tick_step = 1
        self._tick_step = tick_step

    def setAllowZeroRange(self, allow: bool) -> None:
        self._allow_zero_range = allow

    def setTickValue(self, min_tick_value: int, max_tick_value: int) -> None:
        if min_tick_value > max_tick_value:
            min_tick_value, max_tick_value = max_tick_value, min_tick_value
        min_tick_value = max(self._min_tick, min(self._max_tick, min_tick_value))
        max_tick_value = max(self._min_tick, min(self._max_tick, max_tick_value))
        required_gap = self._required_tick_gap()
        if max_tick_value - min_tick_value < required_gap:
            # Expand toward active handle direction when possible
            if self._active_handle == "min":
                min_tick_value = max(self._min_tick, max_tick_value - required_gap)
            else:
                max_tick_value = min(self._max_tick, min_tick_value + required_gap)
        if min_tick_value == self._min_tick_value and max_tick_value == self._max_tick_value:
            return
        self._min_tick_value = min_tick_value
        self._max_tick_value = max_tick_value
        self.rangeChanged.emit(self._min_tick_value, self._max_tick_value)
        self.update()

    def getTickRange(self) -> tuple[int, int]:
        return self._min_tick_value, self._max_tick_value

    def setMinimumTickGap(self, tick_gap: int) -> None:
        if tick_gap < 0:
            tick_gap = 0
        self._min_tick_gap = tick_gap
        # Re-validate current values
        self.setTickValue(self._min_tick_value, self._max_tick_value)

    def setShowHandles(self, show: bool) -> None:
        """Set whether to show the slider handles and selection."""
        self._show_handles = show
        self.update()

    # Backward compatibility methods
    def setRange(self, minimum: int, maximum: int) -> None:
        """Backward compatibility method. Use setTickRange instead."""
        self.setTickRange(minimum, maximum)

    def setValue(self, min_value: int, max_value: int) -> None:
        """Backward compatibility method. Use setTickValue instead."""
        self.setTickValue(min_value, max_value)

    def getRange(self) -> tuple[int, int]:
        """Backward compatibility method. Use getTickRange instead."""
        return self.getTickRange()

    def setStep(self, step: int) -> None:
        """Backward compatibility method. Use setTickStep instead."""
        self.setTickStep(step)

    def setMinimumGap(self, gap: int) -> None:
        """Backward compatibility method. Use setMinimumTickGap instead."""
        self.setMinimumTickGap(gap)

    ###########################################################################
    # Painting
    ###########################################################################
    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802 (Qt override)
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
        min_handle = self._handle_rect(self._min_tick_value)
        max_handle = self._handle_rect(self._max_tick_value)
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
        if event.button() != Qt.MouseButton.LeftButton or not self._show_handles:
            return
        pos = event.pos()
        if self._handle_rect(self._min_tick_value).contains(pos):
            self._dragging_min = True
            self._active_handle = "min"
        elif self._handle_rect(self._max_tick_value).contains(pos):
            self._dragging_max = True
            self._active_handle = "max"
        else:
            sel = self._selection_rect()
            if self._center_handle_rect(sel).contains(pos):
                self._dragging_center = True
                self._active_handle = "center"
                self._center_init_min = self._min_tick_value
                self._center_init_max = self._max_tick_value
                self._press_value = self._value_from_pos(pos)
            else:
                # Move nearest handle
                if self._orientation == Qt.Orientation.Horizontal:
                    dist_min = abs(pos.x() - self._handle_rect(self._min_tick_value).center().x())
                    dist_max = abs(pos.x() - self._handle_rect(self._max_tick_value).center().x())
                else:
                    dist_min = abs(pos.y() - self._handle_rect(self._min_tick_value).center().y())
                    dist_max = abs(pos.y() - self._handle_rect(self._max_tick_value).center().y())
                if dist_min <= dist_max:
                    self._dragging_min = True
                    self._active_handle = "min"
                else:
                    self._dragging_max = True
                    self._active_handle = "max"
        self._last_mouse_pos = pos

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if not (self._dragging_min or self._dragging_max or self._dragging_center) or not self._show_handles:
            return
        value = self._value_from_pos(event.pos())
        value = (value // self._tick_step) * self._tick_step
        min_value, max_value = self._min_tick_value, self._max_tick_value
        gap = self._required_tick_gap()
        if self._dragging_min:
            min_value = max(self._min_tick, min(value, self._max_tick_value - gap))
        elif self._dragging_max:
            max_value = min(self._max_tick, max(value, self._min_tick_value + gap))
        elif self._dragging_center:
            init_min = self._center_init_min
            init_max = self._center_init_max
            width = init_max - init_min
            delta = ((value - self._press_value) // self._tick_step) * self._tick_step
            delta = max(self._min_tick - init_min, min(delta, self._max_tick - init_max))
            min_value = init_min + delta
            max_value = min_value + width
        if (min_value, max_value) != (self._min_tick_value, self._max_tick_value):
            self._min_tick_value, self._max_tick_value = min_value, max_value
            self.sliderMoved.emit(self._min_tick_value, self._max_tick_value)
            self.rangeChanged.emit(self._min_tick_value, self._max_tick_value)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._dragging_min = False
        self._dragging_max = False
        self._dragging_center = False

    def keyPressEvent(self, event) -> None:  # noqa: N802
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
                self.setTickValue(self._min_tick, self._max_tick_value)
            else:
                self.setTickValue(self._min_tick_value, max(self._min_tick_value + self._required_tick_gap(), self._min_tick))
            return
        if key == Qt.Key.Key_End:
            if self._active_handle == "max":
                self.setTickValue(self._min_tick_value, self._max_tick)
            else:
                self.setTickValue(min(self._max_tick - self._required_tick_gap(), self._max_tick), self._max_tick_value)
            return
        super().keyPressEvent(event)

    def _nudge_active(self, delta: int) -> None:
        if not self._show_handles:
            return
        if self._active_handle == "min":
            new_min = max(self._min_tick, min(self._min_tick_value + delta, self._max_tick_value - self._required_tick_gap()))
            self.setTickValue(new_min, self._max_tick_value)
        elif self._active_handle == "max":
            new_max = min(self._max_tick, max(self._max_tick_value + delta, self._min_tick_value + self._required_tick_gap()))
            self.setTickValue(self._min_tick_value, new_max)
        else:
            init_min = self._min_tick_value
            init_max = self._max_tick_value
            delta = max(self._min_tick - init_min, min(delta, self._max_tick - init_max))
            self.setTickValue(init_min + delta, init_max + delta)

    ###########################################################################
    # Geometry helpers
    ###########################################################################
    def _track_rect(self) -> QRect:
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(self._handle_size // 2, (self.height() - self._track_thickness) // 2, self.width() - self._handle_size, self._track_thickness)
        return QRect((self.width() - self._track_thickness) // 2, self._handle_size // 2, self._track_thickness, self.height() - self._handle_size)

    def _handle_rect(self, value: int) -> QRect:
        if not self._show_handles:
            return QRect()
        track = self._track_rect()
        rng = max(1, self._max_tick - self._min_tick)
        if self._orientation == Qt.Orientation.Horizontal:
            x = track.x() + int((value - self._min_tick) * track.width() / rng)
            return QRect(x - self._handle_size // 2, (self.height() - self._handle_size) // 2, self._handle_size, self._handle_size)
        else:
            y = track.y() + track.height() - int((value - self._min_tick) * track.height() / rng)
            return QRect((self.width() - self._handle_size) // 2, y - self._handle_size // 2, self._handle_size, self._handle_size)

    def _value_from_pos(self, pos: QPoint) -> int:
        track = self._track_rect()
        rng = self._max_tick - self._min_tick
        if rng <= 0:
            return self._min_tick
        if self._orientation == Qt.Orientation.Horizontal:
            rel = (pos.x() - track.x()) / max(1, track.width())
        else:
            rel = 1.0 - (pos.y() - track.y()) / max(1, track.height())
        rel = max(0.0, min(1.0, rel))
        return int(self._min_tick + rel * rng)

    def _required_tick_gap(self) -> int:
        base = 0 if self._allow_zero_range else self._tick_step
        return max(self._min_tick_gap, base)

    def _selection_rect(self) -> QRect:
        track = self._track_rect()
        min_handle = self._handle_rect(self._min_tick_value)
        max_handle = self._handle_rect(self._max_tick_value)
        if self._orientation == Qt.Orientation.Horizontal:
            return QRect(min_handle.center().x(), track.y(), max_handle.center().x() - min_handle.center().x(), track.height())
        else:
            return QRect(track.x(), max_handle.center().y(), track.width(), min_handle.center().y() - max_handle.center().y())

    def _center_handle_rect(self, selection: QRect) -> QRect:
        track = self._track_rect()
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
        self._center_bar_width = max(4, min(64, width))
        self.update()

    def setHighlightColor(self, color: QColor) -> None:
        self._highlight_color = color
        self.update()

    def setHighlightThickness(self, thickness: int) -> None:
        self._highlight_thickness = max(1, min(6, thickness))
        self.update()


