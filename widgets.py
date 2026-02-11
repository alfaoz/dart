"""Reusable DART widgets: filter bar, empty state, loading overlay."""

from PySide6.QtCore import Qt, QPropertyAnimation, QEvent, QPoint, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPixmap
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QFrame, QTableView, QListWidget, QListWidgetItem,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
)

from theme import sys_font_family, THEMES

# ---------------------------------------------------------------------------
# Filter commands definition
# ---------------------------------------------------------------------------

FILTER_COMMANDS = [
    ("#range: ",      "x,y",    "numeric range (inclusive)"),
    ("#notrange: ",   "x,y",    "exclude numeric range"),
    ("#startswith: ",  "text",   "cell begins with text"),
    ("#contains: ",    "text",   "substring search"),
    ("#equals: ",      "text",   "exact match"),
    ("#endswith: ",    "text",   "cell ends with text"),
    ("#not: ",         "text",   "exclude rows containing text"),
    ("#regex: ",       "pattern","regular expression"),
    ("#in: ",          "a, b, c","match any listed value"),
]


# ---------------------------------------------------------------------------
# Filter input with autocomplete
# ---------------------------------------------------------------------------

class FilterInput(QLineEdit):
    """QLineEdit with # command autocomplete popup and debounced output."""

    _popup = None  # shared popup across all instances
    debounced_text = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("colFilter")
        self.setFixedHeight(24)
        self.setPlaceholderText("# to filter...")
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(
            lambda: self.debounced_text.emit(self.text()))
        self.textChanged.connect(self._on_text_changed)
        self.textChanged.connect(lambda _: self._debounce_timer.start())

    def _get_popup(self):
        """Lazy-create a single shared popup (re-parented on use)."""
        if FilterInput._popup is None:
            FilterInput._popup = _CommandPopup()
            FilterInput._popup.item_picked.connect(self._noop)
        return FilterInput._popup

    @staticmethod
    def _noop(text):
        pass

    def _on_text_changed(self, text):
        popup = self._get_popup()
        stripped = text.strip()

        if stripped == "#" or (stripped.startswith("#") and ":" not in stripped):
            # Show popup filtered by what they've typed so far
            query = stripped[1:]  # everything after #
            popup.show_for(self, query)
        else:
            popup.hide()

    def keyPressEvent(self, event):
        popup = self._get_popup()
        if popup.isVisible():
            if event.key() in (Qt.Key_Down, Qt.Key_Up):
                popup.handle_arrow(event.key())
                return
            if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
                popup.pick_current(self)
                return
            if event.key() == Qt.Key_Escape:
                popup.hide()
                return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        popup = self._get_popup()
        # Small delay so clicking the popup item works
        from PySide6.QtCore import QTimer
        QTimer.singleShot(150, lambda: self._maybe_hide_popup())

    def _maybe_hide_popup(self):
        popup = self._get_popup()
        if popup._owner is not self:
            return
        if not self.hasFocus():
            popup.hide()


class _CommandPopup(QWidget):
    """Floating popup showing filter command suggestions."""

    from PySide6.QtCore import Signal
    item_picked = Signal(str)

    def __init__(self):
        super().__init__(None, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.NoFocus)
        self._owner = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        self._list = QListWidget()
        self._list.setFocusPolicy(Qt.NoFocus)
        self._list.setMouseTracking(True)
        self._list.itemClicked.connect(self._on_click)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self._list)

        self.setFixedWidth(280)
        self._apply_style()

    def _apply_style(self, theme_name="dark"):
        t = THEMES[theme_name]
        self.setStyleSheet(f"""
            _CommandPopup {{
                background: {t['bg_elevated']};
                border: 1px solid {t['border_default']};
                border-radius: 8px;
            }}
            QListWidget {{
                background: {t['bg_elevated']};
                border: none;
                outline: none;
                font-size: 12px;
                color: {t['text_primary']};
            }}
            QListWidget::item {{
                padding: 6px 10px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background: {t['bg_overlay']};
            }}
            QListWidget::item:selected {{
                background: {t['accent_muted']};
                color: {t['text_primary']};
            }}
        """)

    def show_for(self, owner: FilterInput, query: str):
        self._owner = owner

        self._list.clear()
        q = query.lower()
        for cmd, args, desc in FILTER_COMMANDS:
            name = cmd.strip().rstrip(": ")
            if q and q not in name.lower():
                continue
            item = QListWidgetItem()
            item.setText(f"{cmd}{args}    {desc}")
            item.setData(Qt.UserRole, cmd)
            self._list.addItem(item)

        if self._list.count() == 0:
            self.hide()
            return

        self._list.setCurrentRow(0)
        row_h = 30
        h = min(self._list.count() * row_h + 10, 260)
        self.setFixedHeight(h)

        # Position below the input
        global_pos = owner.mapToGlobal(QPoint(0, owner.height()))
        self.move(global_pos)
        self.show()

    def handle_arrow(self, key):
        cur = self._list.currentRow()
        if key == Qt.Key_Down:
            self._list.setCurrentRow(min(cur + 1, self._list.count() - 1))
        else:
            self._list.setCurrentRow(max(cur - 1, 0))

    def pick_current(self, owner: FilterInput):
        item = self._list.currentItem()
        if item:
            cmd = item.data(Qt.UserRole)
            owner.blockSignals(True)
            owner.setText(cmd)
            owner.blockSignals(False)
            owner.textChanged.emit(cmd)
            # Move cursor to end
            owner.setCursorPosition(len(cmd))
        self.hide()

    def _on_click(self, item):
        if self._owner:
            cmd = item.data(Qt.UserRole)
            self._owner.blockSignals(True)
            self._owner.setText(cmd)
            self._owner.blockSignals(False)
            self._owner.textChanged.emit(cmd)
            self._owner.setCursorPosition(len(cmd))
            self._owner.setFocus()
        self.hide()


# ---------------------------------------------------------------------------
# Column filter bar
# ---------------------------------------------------------------------------

class ColumnFilterBar(QWidget):
    """Row of FilterInputs positioned to match table column headers."""

    def __init__(self, table_view: QTableView, parent=None):
        super().__init__(parent)
        self.setObjectName("columnFilterBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.table_view = table_view
        self.setFixedHeight(30)
        self.inputs: list[FilterInput] = []
        self.hide()

        header = self.table_view.horizontalHeader()
        header.sectionResized.connect(self._reposition)
        header.geometriesChanged.connect(self._reposition)
        self.table_view.horizontalScrollBar().valueChanged.connect(self._reposition)

    def rebuild(self, headers: list[str]):
        for inp in self.inputs:
            inp.deleteLater()
        self.inputs.clear()
        for hdr in headers:
            le = FilterInput(self)
            le.setToolTip(f'Filter "{hdr}" - type # for commands')
            le.show()
            self.inputs.append(le)
        self._reposition()
        self.show()

    def _reposition(self, *_a):
        header = self.table_view.horizontalHeader()
        offset = self.table_view.horizontalScrollBar().value()
        for i, inp in enumerate(self.inputs):
            col = i + 1
            x = header.sectionPosition(col) - offset
            w = header.sectionSize(col)
            inp.setGeometry(x, 3, max(w - 1, 20), 24)

    def clear_all(self):
        for inp in self.inputs:
            inp.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition()


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

class EmptyState(QWidget):
    def __init__(self, logo_path: str, on_open, parent=None):
        super().__init__(parent)
        self.setObjectName("emptyState")
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        if logo_path:
            logo_lbl = QLabel()
            px = QPixmap(logo_path)
            if not px.isNull():
                logo_lbl.setPixmap(
                    px.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logo_lbl.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_lbl)

        title = QLabel("Open a CSV file to get started")
        title.setObjectName("emptyTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        hint = QLabel("Ctrl+O  or  drag and drop")
        hint.setObjectName("emptyHint")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        btn = QPushButton("Load Data")
        btn.setObjectName("primaryButton")
        btn.setFixedWidth(140)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(on_open)
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.addWidget(btn)
        layout.addLayout(row)


# ---------------------------------------------------------------------------
# Loading overlay
# ---------------------------------------------------------------------------

class LoadingOverlay(QWidget):
    """Semi-transparent overlay shown during data loading."""

    def __init__(self, logo_path: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("loadingOverlay")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        if logo_path:
            logo_lbl = QLabel()
            px = QPixmap(logo_path)
            if not px.isNull():
                logo_lbl.setPixmap(
                    px.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logo_lbl.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_lbl)

        self._text = QLabel("Loading...")
        self._text.setObjectName("loadingText")
        self._text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._text)

        self._opacity_fx = QGraphicsOpacityEffect(self)
        self._opacity_fx.setOpacity(0)
        self.setGraphicsEffect(self._opacity_fx)
        self.hide()

    def show_overlay(self, text="Loading..."):
        self._text.setText(text)
        self.raise_()
        self.show()
        anim = QPropertyAnimation(self._opacity_fx, b"opacity")
        anim.setDuration(150)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        self._show_anim = anim

    def hide_overlay(self):
        anim = QPropertyAnimation(self._opacity_fx, b"opacity")
        anim.setDuration(150)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.finished.connect(self.hide)
        anim.start()
        self._hide_anim = anim


# ---------------------------------------------------------------------------
# Search bar with focus glow
# ---------------------------------------------------------------------------

class SearchBar(QWidget):
    """Global search bar with animated focus glow and debounced output."""

    debounced_text = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("searchBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(44)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 6, 16, 6)

        self.input = QLineEdit()
        self.input.setObjectName("globalSearch")
        self.input.setPlaceholderText("Search all columns...    Ctrl+F")
        self.input.setClearButtonEnabled(True)
        self.input.setMinimumHeight(32)

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(
            lambda: self.debounced_text.emit(self.input.text()))
        self.input.textChanged.connect(lambda _: self._debounce_timer.start())

        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor("#3aab4e"))
        self._shadow.setOffset(0, 0)
        self.input.setGraphicsEffect(self._shadow)
        self.input.installEventFilter(self)

        lay.addWidget(self.input)

    def eventFilter(self, obj, event):
        if obj is self.input:
            if event.type() == QEvent.FocusIn:
                self._glow(12)
            elif event.type() == QEvent.FocusOut:
                self._glow(0)
        return super().eventFilter(obj, event)

    def _glow(self, end):
        anim = QPropertyAnimation(self._shadow, b"blurRadius")
        anim.setDuration(150)
        anim.setStartValue(self._shadow.blurRadius())
        anim.setEndValue(end)
        anim.start()
        self._glow_anim = anim
