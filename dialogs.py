"""DART dialog windows."""

import csv
from PySide6.QtCore import Qt, QPropertyAnimation, QObject, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsOpacityEffect, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFileDialog, QScrollArea,
    QWidget, QFrame, QGridLayout, QCheckBox,
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

    def __init__(
        self,
        headers,
        raw_data,
        visible_indices,
        case_sensitive=False,
        trim_whitespace=True,
        ignore_empty=True,
    ):
        super().__init__()
        self._headers = headers
        self._data = raw_data
        self._indices = visible_indices
        self._case_sensitive = case_sensitive
        self._trim_whitespace = trim_whitespace
        self._ignore_empty = ignore_empty

    def _normalize_text(self, value):
        txt = "" if value is None else str(value)
        if self._trim_whitespace:
            txt = txt.strip()
        key = txt if self._case_sensitive else txt.casefold()
        return key, txt

    def run(self):
        results: list[tuple] = []
        total_cells = len(self._indices) * len(self._headers)
        cells_done = 0
        last_pct = -1

        for col_idx, hdr in enumerate(self._headers):
            nums: list[float] = []
            text_counts: dict[str, int] = {}
            text_display: dict[str, str] = {}
            unique_values: set[tuple[str, object]] = set()
            for src_row in self._indices:
                row_data = self._data[src_row]
                cell = row_data[col_idx] if col_idx < len(row_data) else ""
                try:
                    num = float(cell)
                    nums.append(num)
                    unique_values.add(("n", num))
                except (ValueError, TypeError):
                    key, display = self._normalize_text(cell)
                    if not (self._ignore_empty and key == ""):
                        text_counts[key] = text_counts.get(key, 0) + 1
                        unique_values.add(("t", key))
                        if key not in text_display:
                            text_display[key] = display
                cells_done += 1
                if cells_done % 100_000 == 0:
                    pct = int(cells_done / total_cells * 100) if total_cells else 100
                    if pct != last_pct:
                        self.progress.emit(pct)
                        last_pct = pct

            if nums and text_counts:
                col_type = "Mixed"
            elif nums:
                col_type = "Numeric"
            else:
                col_type = "Text"

            if nums:
                min_val = f"{min(nums):.2f}"
                max_val = f"{max(nums):.2f}"
                avg_val = f"{sum(nums)/len(nums):.2f}"
            else:
                min_val = "-"
                max_val = "-"
                avg_val = "-"

            if text_counts:
                top_key = min(
                    text_counts.keys(),
                    key=lambda k: (-text_counts[k], k),
                )
                top_text = text_display.get(top_key, top_key)
                if top_text == "":
                    top_text = "(empty)"
                unique_text = str(len(text_counts))
                top_count = str(text_counts[top_key])
            else:
                unique_text = "0"
                top_text = "-"
                top_count = "-"

            results.append((
                hdr,
                col_type,
                str(len(self._indices)),
                str(len(unique_values)),
                min_val,
                max_val,
                avg_val,
                unique_text,
                top_text,
                top_count,
            ))

        if last_pct != 100:
            self.progress.emit(100)

        self.finished.emit(results)


# -----------------------------------------------------------------------
# Stats (with CSV export) — async
# -----------------------------------------------------------------------

class StatsDialog(BaseDialog):
    def __init__(self, source_model, proxy_model, parent=None):
        super().__init__(parent, title="Statistics", width=920, height=500)
        self._stats_data: list[tuple] = []
        self._thread = None
        self._worker = None

        self._headers = list(source_model.raw_headers())
        self._raw_data = source_model.raw_data()
        self._visible_indices = list(proxy_model._visible_indices)

        # Text stats options
        opts = QHBoxLayout()
        opts.setSpacing(12)

        self._case_sensitive_cb = QCheckBox("Case sensitive text")
        self._trim_ws_cb = QCheckBox("Trim whitespace")
        self._trim_ws_cb.setChecked(True)
        self._ignore_empty_cb = QCheckBox("Ignore empty values")
        self._ignore_empty_cb.setChecked(True)

        self._recompute_btn = QPushButton("Recompute")
        self._recompute_btn.setObjectName("actionButton")
        self._recompute_btn.setCursor(Qt.PointingHandCursor)
        self._recompute_btn.clicked.connect(self._start_worker)

        opts.addWidget(self._case_sensitive_cb)
        opts.addWidget(self._trim_ws_cb)
        opts.addWidget(self._ignore_empty_cb)
        opts.addStretch()
        opts.addWidget(self._recompute_btn)
        self.content_layout.addLayout(opts)

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

        self._start_worker()

    def _set_busy(self, busy):
        self._case_sensitive_cb.setEnabled(not busy)
        self._trim_ws_cb.setEnabled(not busy)
        self._ignore_empty_cb.setEnabled(not busy)
        self._recompute_btn.setEnabled(not busy)
        if busy:
            self._export_btn.setEnabled(False)

    def _start_worker(self):
        if self._thread is not None and self._thread.isRunning():
            return

        self._set_busy(True)
        self._progress_label.setText("Computing statistics...")
        self._progress_label.show()
        self.table.hide()

        self._worker = StatsWorker(
            self._headers,
            self._raw_data,
            self._visible_indices,
            case_sensitive=self._case_sensitive_cb.isChecked(),
            trim_whitespace=self._trim_ws_cb.isChecked(),
            ignore_empty=self._ignore_empty_cb.isChecked(),
        )
        self._thread = QThread(self)
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.started.connect(self._worker.run)
        self._thread.start()

    def _on_thread_finished(self):
        self._worker = None
        self._thread = None

    def _on_progress(self, pct):
        self._progress_label.setText(f"Computing statistics... {pct}%")

    def _on_finished(self, results):
        self._stats_data = results
        self._progress_label.hide()
        self.table.show()
        self._export_btn.setEnabled(True)
        self._set_busy(False)

        headers = [
            "Column",
            "Type",
            "Count",
            "Unique Count",
            "Min",
            "Max",
            "Average",
            "Unique Text",
            "Most Common Text",
            "Most Common Count",
        ]
        self.table.setRowCount(len(self._stats_data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        for r, row in enumerate(self._stats_data):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(val))
        self._fit_stats_columns(headers)

    def _fit_stats_columns(self, headers):
        """Size columns so header text stays readable without clipping."""
        hdr = self.table.horizontalHeader()
        hdr_metrics = hdr.fontMetrics()
        cell_metrics = self.table.fontMetrics()
        sample_rows = min(self.table.rowCount(), 250)

        for col, title in enumerate(headers):
            width = hdr_metrics.horizontalAdvance(title) + 28
            for row in range(sample_rows):
                item = self.table.item(row, col)
                if item is None:
                    continue
                txt = item.text()
                if len(txt) > 120:
                    txt = txt[:120]
                width = max(width, cell_metrics.horizontalAdvance(txt) + 24)

            # Keep headers legible while avoiding extremely wide columns.
            width = max(84, min(width, 260))
            self.table.setColumnWidth(col, width)
            hdr.setSectionResizeMode(col, QHeaderView.Interactive)

        hdr.setStretchLastSection(False)

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Statistics", "stats.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([
                    "Column",
                    "Type",
                    "Count",
                    "Unique Count",
                    "Min",
                    "Max",
                    "Average",
                    "Unique Text",
                    "Most Common Text",
                    "Most Common Count",
                ])
                for row in self._stats_data:
                    w.writerow(row)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not export stats:\n{e}")

    def reject(self):
        if self._thread is not None and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)
        super().reject()
