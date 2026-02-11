"""DART dialog windows."""

import csv
from PySide6.QtCore import Qt, QPropertyAnimation, QObject, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsOpacityEffect, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFileDialog, QScrollArea,
    QWidget, QFrame, QGridLayout,
)

from theme import THEMES, sys_font_family


class BaseDialog(QDialog):
    """Frameless, draggable dialog with fade-in."""

    def __init__(self, parent=None, title="", width=500, height=400):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setFixedSize(width, height)

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(24, 20, 24, 20)
        self._outer.setSpacing(16)

        if title:
            lbl = QLabel(title)
            lbl.setObjectName("dialogTitle")
            lbl.setFont(QFont(sys_font_family(), 18, QFont.DemiBold))
            self._outer.addWidget(lbl)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        self._outer.addLayout(self.content_layout)

        self._btn_row = QHBoxLayout()
        self._btn_row.addStretch()
        self._outer.addLayout(self._btn_row)

        self._fade_in()

    def _fade_in(self):
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._anim = QPropertyAnimation(self._opacity, b"opacity")
        self._anim.setDuration(200)
        self._anim.setStartValue(0)
        self._anim.setEndValue(1)
        self._anim.start()

    def add_close_button(self):
        btn = QPushButton("Close")
        btn.setObjectName("actionButton")
        btn.clicked.connect(self.reject)
        self._btn_row.addWidget(btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, "_drag_pos"):
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if hasattr(self, "_drag_pos"):
            del self._drag_pos


# -----------------------------------------------------------------------
# About
# -----------------------------------------------------------------------

class AboutDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="", width=420, height=260)

        name = QLabel("DART")
        name.setFont(QFont(sys_font_family(), 28, QFont.Bold))
        name.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(name)

        sub = QLabel("Data Access and Reformatting Tool")
        sub.setObjectName("textSecondary")
        sub.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(sub)

        ver = QLabel("v2.2 Petra")
        ver.setObjectName("versionPill")
        ver.setAlignment(Qt.AlignCenter)
        ver.setFixedWidth(130)
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.addWidget(ver)
        self.content_layout.addLayout(row)

        self.content_layout.addStretch()

        author = QLabel('developed by <a href="https://alfaoz.dev" style="color: #3aab4e; text-decoration: none;">alfaoz</a>')
        author.setObjectName("textTertiary")
        author.setAlignment(Qt.AlignCenter)
        author.setOpenExternalLinks(True)
        self.content_layout.addWidget(author)

        gh = QLabel('<a href="https://github.com/alfaoz/dart" style="color: #5a6e60; text-decoration: none;">github.com/alfaoz/dart</a>')
        gh.setObjectName("textTertiary")
        gh.setAlignment(Qt.AlignCenter)
        gh.setOpenExternalLinks(True)
        self.content_layout.addWidget(gh)

        self.add_close_button()


# -----------------------------------------------------------------------
# Help  (native widgets, no HTML)
# -----------------------------------------------------------------------

class HelpDialog(BaseDialog):
    def __init__(self, theme_name="dark", parent=None):
        super().__init__(parent, title="Help", width=580, height=520)
        t = THEMES[theme_name]

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 12, 0)
        lay.setSpacing(18)

        # --- Filter commands ---
        lay.addWidget(self._section("Filter Commands"))
        lay.addWidget(self._caption(
            "Type in the per-column filter inputs below column headers. "
            "Prefix with #. Without a prefix a case-insensitive substring "
            "search is used."))

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        commands = [
            ("#range: x,y",       "Numeric range (inclusive)"),
            ("#notrange: x,y",    "Exclude numeric range"),
            ("#startswith: text",  "Cell begins with text"),
            ("#contains: text",   "Substring search"),
            ("#equals: text",     "Exact match"),
            ("#endswith: text",   "Cell ends with text"),
            ("#not: text",        "Exclude rows containing text"),
            ("#regex: pattern",   "Regular expression"),
            ("#in: a, b, c",     "Match any listed value"),
        ]
        for i, (cmd, desc) in enumerate(commands):
            code = QLabel(cmd)
            code.setObjectName("helpCode")
            code.setFont(QFont("monospace", 11))
            grid.addWidget(code, i, 0)
            grid.addWidget(QLabel(desc), i, 1)
        lay.addLayout(grid)

        # --- Keyboard shortcuts ---
        lay.addWidget(self._section("Keyboard Shortcuts"))
        sg = QGridLayout()
        sg.setHorizontalSpacing(16)
        sg.setVerticalSpacing(6)
        shortcuts = [
            ("Ctrl+O",        "Open file"),
            ("Ctrl+Shift+E",  "Export CSV"),
            ("Ctrl+F",        "Focus search"),
            ("Ctrl+ =  /  -", "Zoom in / out"),
            ("Ctrl+0",        "Reset zoom"),
            ("Ctrl+I",        "Statistics"),
            ("Ctrl+Shift+T",  "Toggle theme"),
            ("F1",            "This help"),
        ]
        for i, (key, desc) in enumerate(shortcuts):
            k = QLabel(key)
            k.setObjectName("helpCode")
            k.setFont(QFont("monospace", 11))
            sg.addWidget(k, i, 0)
            sg.addWidget(QLabel(desc), i, 1)
        lay.addLayout(sg)

        # --- Tips ---
        lay.addWidget(self._section("Tips"))
        tips = [
            "Click column headers to sort. Click again to reverse.",
            "Drag and drop a .csv file onto the window to open it.",
            "Right-click a cell to copy its value.",
            "Use File > Save Settings to persist your filters.",
        ]
        for tip in tips:
            bullet = QLabel(f"  {tip}")
            bullet.setWordWrap(True)
            lay.addWidget(bullet)

        lay.addStretch()
        scroll.setWidget(inner)
        self.content_layout.addWidget(scroll)
        self.add_close_button()

        self._apply_help_styles(t)

    def _section(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("helpSection")
        lbl.setFont(QFont(sys_font_family(), 14, QFont.DemiBold))
        return lbl

    def _caption(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("textSecondary")
        lbl.setWordWrap(True)
        return lbl

    def _apply_help_styles(self, t):
        self.setStyleSheet(self.styleSheet() + f"""
            QLabel#helpSection {{ color: {t['text_primary']}; }}
            QLabel#helpCode {{
                background: {t['bg_overlay']};
                color: {t['accent']};
                padding: 2px 6px;
                border-radius: 4px;
            }}
        """)


# -----------------------------------------------------------------------
# Stats worker (runs on QThread)
# -----------------------------------------------------------------------

class StatsWorker(QObject):
    """Compute column statistics off the main thread."""
    progress = Signal(int)   # percentage 0-100
    finished = Signal(list)  # list of tuples

    def __init__(self, headers, raw_data, visible_indices):
        super().__init__()
        self._headers = headers
        self._data = raw_data
        self._indices = visible_indices

    def run(self):
        results: list[tuple] = []
        total_cells = len(self._indices) * len(self._headers)
        cells_done = 0
        last_pct = -1

        for col_idx, hdr in enumerate(self._headers):
            nums: list[float] = []
            for src_row in self._indices:
                row_data = self._data[src_row]
                cell = row_data[col_idx] if col_idx < len(row_data) else ""
                try:
                    nums.append(float(cell))
                except (ValueError, TypeError):
                    pass
                cells_done += 1
                if cells_done % 100_000 == 0:
                    pct = int(cells_done / total_cells * 100) if total_cells else 100
                    if pct != last_pct:
                        self.progress.emit(pct)
                        last_pct = pct

            if nums:
                results.append((
                    hdr, "Numeric", str(len(nums)),
                    f"{min(nums):.2f}", f"{max(nums):.2f}",
                    f"{sum(nums)/len(nums):.2f}"))
            else:
                results.append((
                    hdr, "Text", str(len(self._indices)), "-", "-", "-"))

        self.finished.emit(results)


# -----------------------------------------------------------------------
# Stats (with CSV export) — async
# -----------------------------------------------------------------------

class StatsDialog(BaseDialog):
    def __init__(self, source_model, proxy_model, parent=None):
        super().__init__(parent, title="Statistics", width=660, height=440)
        self._stats_data: list[tuple] = []

        # Progress label (shown while computing)
        self._progress_label = QLabel("Computing statistics...")
        self._progress_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self._progress_label)

        # Table (hidden until done)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.hide()
        self.content_layout.addWidget(self.table)

        # Export button (disabled until done)
        self._export_btn = QPushButton("Export Stats")
        self._export_btn.setObjectName("primaryButton")
        self._export_btn.setCursor(Qt.PointingHandCursor)
        self._export_btn.clicked.connect(self._export)
        self._export_btn.setEnabled(False)
        self._btn_row.insertWidget(0, self._export_btn)

        self.add_close_button()

        # Launch worker
        headers = list(source_model.raw_headers())
        raw_data = source_model.raw_data()
        visible_indices = list(proxy_model._visible_indices)

        self._worker = StatsWorker(headers, raw_data, visible_indices)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._thread.started.connect(self._worker.run)
        self._thread.start()

    def _on_progress(self, pct):
        self._progress_label.setText(f"Computing statistics... {pct}%")

    def _on_finished(self, results):
        self._stats_data = results
        self._progress_label.hide()
        self.table.show()
        self._export_btn.setEnabled(True)

        headers = ["Column", "Type", "Count", "Min", "Max", "Average"]
        self.table.setRowCount(len(self._stats_data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        for r, row in enumerate(self._stats_data):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(val))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Statistics", "stats.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Column", "Type", "Count", "Min", "Max", "Average"])
                for row in self._stats_data:
                    w.writerow(row)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not export stats:\n{e}")

    def reject(self):
        self._thread.quit()
        self._thread.wait(2000)
        super().reject()
