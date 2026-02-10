"""Reusable DART widgets: filter bar, empty state, loading overlay."""

from PySide6.QtCore import Qt, QPropertyAnimation, QEvent
from PySide6.QtGui import QFont, QColor, QPixmap
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QFrame, QTableView,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
)

from theme import sys_font_family


# ---------------------------------------------------------------------------
# Column filter bar  (absolute-positioned inputs, clipped by parent bounds)
# ---------------------------------------------------------------------------

class ColumnFilterBar(QWidget):
    """Row of QLineEdits positioned to match table column headers exactly."""

    def __init__(self, table_view: QTableView, parent=None):
        super().__init__(parent)
        self.setObjectName("columnFilterBar")
        self.table_view = table_view
        self.setFixedHeight(30)
        self.inputs: list[QLineEdit] = []
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
            le = QLineEdit(self)  # parented directly, no layout
            le.setObjectName("colFilter")
            le.setPlaceholderText("Filter...")
            le.setToolTip(f'Filter "{hdr}" - #range:, #contains:, etc.')
            le.setFixedHeight(24)
            le.show()
            self.inputs.append(le)
        self._reposition()
        self.show()

    def _reposition(self, *_a):
        header = self.table_view.horizontalHeader()
        offset = self.table_view.horizontalScrollBar().value()
        for i, inp in enumerate(self.inputs):
            col = i + 1  # skip hidden _index_ col
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
    """Global search bar with animated focus glow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("searchBar")
        self.setFixedHeight(44)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 6, 16, 6)

        self.input = QLineEdit()
        self.input.setObjectName("globalSearch")
        self.input.setPlaceholderText("Search all columns...    Ctrl+F")
        self.input.setClearButtonEnabled(True)
        self.input.setMinimumHeight(32)

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
