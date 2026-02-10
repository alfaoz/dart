"""Multi-column filter proxy model with command syntax."""

import re
from PySide6.QtCore import QSortFilterProxyModel, Qt


class MultiFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.column_filters = {}
        self.global_filter_text = ""

    def setFilterForColumn(self, column: int, text: str):
        self.column_filters[column] = text
        self.invalidateFilter()

    def setGlobalFilter(self, text: str):
        self.global_filter_text = text.strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent):
        model = self.sourceModel()
        for col, ft in self.column_filters.items():
            if not ft:
                continue
            index = model.index(source_row, col, source_parent)
            cell = str(model.data(index, Qt.DisplayRole))
            stripped = ft.strip()
            if stripped.startswith("#"):
                if not self._apply_command(stripped[1:].strip(), cell):
                    return False
            else:
                if stripped.lower() not in cell.lower():
                    return False
        if self.global_filter_text:
            needle = self.global_filter_text.lower()
            for col in range(1, model.columnCount()):
                index = model.index(source_row, col, source_parent)
                if needle in str(model.data(index, Qt.DisplayRole)).lower():
                    return True
            return False
        return True

    @staticmethod
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
