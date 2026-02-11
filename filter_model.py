"""Filtered table model with background worker for large datasets."""

import re
from PySide6.QtCore import (
    QAbstractTableModel, QModelIndex, QObject, Qt, QThread, Signal,
)


# ---------------------------------------------------------------------------
# Module-level filter command logic (used by worker thread)
# ---------------------------------------------------------------------------

def _apply_command(cmd_text: str, cell: str) -> bool:
    lc = cmd_text.lower()
    if lc.startswith("range:"):
        try:
            parts = cmd_text[6:].strip().split(",")
            if len(parts) != 2:
                return False
            lo, hi = float(parts[0]), float(parts[1])
            return lo <= float(cell) <= hi
        except Exception:
            return False
    elif lc.startswith("notrange:"):
        try:
            parts = cmd_text[9:].strip().split(",")
            if len(parts) != 2:
                return False
            lo, hi = float(parts[0]), float(parts[1])
            return not (lo <= float(cell) <= hi)
        except Exception:
            return False
    elif lc.startswith("startswith:"):
        return cell.lower().startswith(cmd_text[11:].strip().lower())
    elif lc.startswith("contains:"):
        return cmd_text[9:].strip().lower() in cell.lower()
    elif lc.startswith("equals:"):
        return cell.lower() == cmd_text[7:].strip().lower()
    elif lc.startswith("endswith:"):
        return cell.lower().endswith(cmd_text[9:].strip().lower())
    elif lc.startswith("not:"):
        return cmd_text[4:].strip().lower() not in cell.lower()
    elif lc.startswith("regex:"):
        try:
            return bool(re.search(cmd_text[6:].strip(), cell, re.IGNORECASE))
        except Exception:
            return False
    elif lc.startswith("in:"):
        vals = [v.strip().lower() for v in cmd_text[3:].split(",")]
        return cell.lower() in vals
    return False


def _row_accepted(row_data: list[str], column_filters: dict[int, str],
                  global_text: str, col_count: int) -> bool:
    """Return True if *row_data* passes all column filters + global search."""
    for col, ft in column_filters.items():
        if not ft:
            continue
        # col is 1-based (col-1 indexes into row_data)
        idx = col - 1
        if idx < 0 or idx >= len(row_data):
            return False
        cell = row_data[idx]
        stripped = ft.strip()
        if stripped.startswith("#"):
            after_hash = stripped[1:].strip()
            if ":" not in after_hash:
                continue
            cmd_name, _, arg = after_hash.partition(":")
            if not arg.strip():
                continue
            if not _apply_command(after_hash, cell):
                return False
        else:
            if stripped.lower() not in cell.lower():
                return False

    if global_text:
        needle = global_text.lower()
        for cell in row_data:
            if needle in cell.lower():
                return True
        return False

    return True


# ---------------------------------------------------------------------------
# FilterWorker — runs on a dedicated QThread
# ---------------------------------------------------------------------------

class FilterWorker(QObject):
    """Performs filtering + sorting off the main thread."""

    finished = Signal(int, list)  # (generation, visible_indices)

    def __init__(self):
        super().__init__()
        self._data: list[list[str]] = []
        self._headers: list[str] = []
        self._column_filters: dict[int, str] = {}
        self._global_text: str = ""
        self._sort_col: int = 0
        self._sort_order: Qt.SortOrder = Qt.AscendingOrder
        self._generation: int = 0

    def run_filter(self, generation: int):
        """Called via signal from main thread."""
        data = self._data
        col_filters = dict(self._column_filters)
        global_text = self._global_text
        sort_col = self._sort_col
        sort_order = self._sort_order
        col_count = len(self._headers)

        indices: list[int] = []
        for i, row in enumerate(data):
            # Check for stale generation every 50k rows
            if i & 0xFFFF == 0 and generation != self._generation:
                return
            if _row_accepted(row, col_filters, global_text, col_count):
                indices.append(i)

        # Check stale before sorting
        if generation != self._generation:
            return

        # Sort
        if sort_col > 0:
            data_col = sort_col - 1
            reverse = sort_order == Qt.DescendingOrder

            def sort_key(idx):
                val = data[idx][data_col] if data_col < len(data[idx]) else ""
                try:
                    return (0, float(val))
                except (ValueError, TypeError):
                    return (1, val.lower())

            indices.sort(key=sort_key, reverse=reverse)
        elif sort_col == 0 and sort_order == Qt.AscendingOrder:
            pass  # natural order, already correct
        elif sort_col == 0 and sort_order == Qt.DescendingOrder:
            indices.reverse()

        if generation != self._generation:
            return

        self.finished.emit(generation, indices)


# ---------------------------------------------------------------------------
# Signal dispatcher (avoids QMetaObject.invokeMethod)
# ---------------------------------------------------------------------------

class _FilterDispatcher(QObject):
    trigger = Signal(int)


# ---------------------------------------------------------------------------
# FilteredTableModel — displayed by QTableView
# ---------------------------------------------------------------------------

class FilteredTableModel(QAbstractTableModel):
    """Proxy-like model backed by visible-index list, updated by FilterWorker."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source = None
        self._visible_indices: list[int] = []
        self._column_filters: dict[int, str] = {}
        self._global_text: str = ""
        self._sort_col: int = 0
        self._sort_order: Qt.SortOrder = Qt.AscendingOrder
        self._generation: int = 0

        # Worker setup
        self._worker = FilterWorker()
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._dispatcher = _FilterDispatcher()
        self._dispatcher.trigger.connect(
            self._worker.run_filter, Qt.QueuedConnection)
        self._worker.finished.connect(self._on_filter_done, Qt.QueuedConnection)
        self._thread.start()

    def set_source(self, source):
        self._source = source

    # -- QAbstractTableModel interface --

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._visible_indices)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid() or self._source is None:
            return 0
        return self._source.columnCount()

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole or not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if row < 0 or row >= len(self._visible_indices):
            return None
        src_row = self._visible_indices[row]
        if col == 0:
            return src_row
        data_col = col - 1
        src_data = self._source.raw_data()
        if src_row < len(src_data) and data_col < len(src_data[src_row]):
            return src_data[src_row][data_col]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if self._source is not None:
            return self._source.headerData(section, orientation, role)
        return None

    # -- Filter / sort API (called from main thread) --

    def setFilterForColumn(self, column: int, text: str):
        self._column_filters[column] = text
        self._schedule_filter()

    def setGlobalFilter(self, text: str):
        self._global_text = text.strip()
        self._schedule_filter()

    def sort(self, column: int, order=Qt.AscendingOrder):
        self._sort_col = column
        self._sort_order = order
        self._schedule_filter()

    def reset_all(self):
        """Full reset after new data load — show all rows in natural order."""
        self._column_filters.clear()
        self._global_text = ""
        self._sort_col = 0
        self._sort_order = Qt.AscendingOrder
        if self._source is not None:
            indices = list(range(len(self._source.raw_data())))
            self.beginResetModel()
            self._visible_indices = indices
            self.endResetModel()

    # -- Internal scheduling --

    def _schedule_filter(self):
        self._generation += 1
        gen = self._generation
        # Push params to worker (atomic-ish — worker reads at start of run)
        w = self._worker
        w._data = self._source.raw_data() if self._source else []
        w._headers = self._source.raw_headers() if self._source else []
        w._column_filters = dict(self._column_filters)
        w._global_text = self._global_text
        w._sort_col = self._sort_col
        w._sort_order = self._sort_order
        w._generation = gen
        self._dispatcher.trigger.emit(gen)

    def _on_filter_done(self, generation: int, indices: list[int]):
        if generation != self._generation:
            return  # stale result
        self.beginResetModel()
        self._visible_indices = indices
        self.endResetModel()

    # -- Cleanup --

    def shutdown(self):
        self._thread.quit()
        self._thread.wait(2000)
