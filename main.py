import sys
import csv
import json
import re
from PySide6.QtCore import QSortFilterProxyModel, Qt, QPropertyAnimation
from PySide6.QtGui import QStandardItem, QStandardItemModel, QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QFrame,
    QMenu,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QAbstractItemView,
    QTextBrowser,
    QDialogButtonBox,
    QGraphicsOpacityEffect,
)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setFixedSize(500, 300)
        self.setup_ui()
        self.start_animation()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title label
        title = QLabel("<h1 style='margin:0;'>CSV Filter & Sorter</h1>", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Info text
        info = QLabel(
            "<p style='font-size:14px; line-height:1.5;'>"
            "Version 0.3b<br><br>"
            "Data reformatting made easy.<br><br>"
            "Developed by Alfa Ozaltin @ VXCO<br><br>"
            "#dartftw"
            "</p>",
            self)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def start_animation(self):
        # Set up an opacity effect and animate from 0 (transparent) to 1 (fully opaque)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(1000)  # Animation duration: 1 second
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()


class MultiFilterProxyModel(QSortFilterProxyModel):
    """

    Supported commands:
      - "#range: x,y"       : Only show rows where the cell's numeric value is between x and y.
      - "#startswith: text" : Only show rows where the cell starts with 'text'.
      - "#contains: text"   : Only show rows where the cell contains 'text'.
      - "#equals: text"     : Only show rows where the cell exactly equals 'text'.
      - "#endswith: text"   : Only show rows where the cell ends with 'text'.
      - "#not: text"        : Exclude rows where the cell contains 'text'.
      - "#regex: pattern"   : Only show rows where the cell matches the regular expression.
      - "#in: v1, v2, ..."  : Only show rows where the cell equals one of the comma‑separated values.

    Without a '#' prefix, a simple case‑insensitive substring search is performed.
    """

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
        for col, filterText in self.column_filters.items():
            if filterText:
                index = model.index(source_row, col, source_parent)
                cellData = model.data(index, Qt.DisplayRole)
                cellStr = str(cellData)
                filterTextStripped = filterText.strip()
                if filterTextStripped.startswith("#"):
                    command_text = filterTextStripped[1:].strip()
                    lower_command = command_text.lower()
                    if lower_command.startswith("range:"):
                        try:
                            range_args = command_text[6:].strip()
                            parts = range_args.split(',')
                            if len(parts) != 2:
                                return False
                            lower_bound = float(parts[0].strip())
                            upper_bound = float(parts[1].strip())
                            cell_value = float(cellStr)
                            if not (lower_bound <= cell_value <= upper_bound):
                                return False
                        except Exception:
                            return False
                    elif lower_command.startswith("startswith:"):
                        prefix = command_text[len("startswith:"):].strip()
                        if not cellStr.lower().startswith(prefix.lower()):
                            return False
                    elif lower_command.startswith("contains:"):
                        substring = command_text[len("contains:"):].strip()
                        if substring.lower() not in cellStr.lower():
                            return False
                    elif lower_command.startswith("equals:"):
                        value = command_text[len("equals:"):].strip()
                        if cellStr.lower() != value.lower():
                            return False
                    elif lower_command.startswith("endswith:"):
                        suffix = command_text[len("endswith:"):].strip()
                        if not cellStr.lower().endswith(suffix.lower()):
                            return False
                    elif lower_command.startswith("not:"):
                        value = command_text[len("not:"):].strip()
                        if value.lower() in cellStr.lower():
                            return False
                    elif lower_command.startswith("regex:"):
                        pattern = command_text[len("regex:"):].strip()
                        try:
                            if not re.search(pattern, cellStr, re.IGNORECASE):
                                return False
                        except Exception:
                            return False
                    elif lower_command.startswith("in:"):
                        values = [v.strip().lower() for v in command_text[len("in:"):].split(",")]
                        if cellStr.lower() not in values:
                            return False
                    else:
                        return False
                else:
                    if filterTextStripped.lower() not in cellStr.lower():
                        return False

        if self.global_filter_text:
            found = False
            for col in range(1, model.columnCount()):
                index = model.index(source_row, col, source_parent)
                cellData = model.data(index, Qt.DisplayRole)
                if self.global_filter_text.lower() in str(cellData).lower():
                    found = True
                    break
            if not found:
                return False

        return True


class StatsDialog(QDialog):


    def __init__(self, proxy_model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stats")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        layout.addWidget(self.table)
        self.populate_stats(proxy_model)

    def populate_stats(self, proxy_model):
        model = proxy_model.sourceModel()
        col_count = model.columnCount()
        stats = []
        for col in range(1, col_count):
            header = model.headerData(col, Qt.Horizontal)
            values = []
            for row in range(proxy_model.rowCount()):
                index = proxy_model.index(row, col)
                cellData = proxy_model.data(index, Qt.DisplayRole)
                try:
                    val = float(cellData)
                    values.append(val)
                except Exception:
                    pass
            if values:
                min_val = min(values)
                max_val = max(values)
                avg_val = sum(values) / len(values)
                count_val = len(values)
                stats.append((header, "Numeric", count_val, min_val, max_val, avg_val))
            else:
                stats.append((header, "Non-numeric", proxy_model.rowCount(), "-", "-", "-"))

        self.table.setRowCount(len(stats))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Column", "Type", "Count", "Min", "Max", "Average"])
        for row, stat in enumerate(stats):
            for col, value in enumerate(stat):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)


class HelpDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DART Help")
        self.resize(700, 500)
        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setReadOnly(True)
        help_html = """
        <html>
        <head>
            <style>
                body { font-family: "Segoe UI", sans-serif; font-size: 14px; background-color: #121212; color: #e0e0e0; margin: 10px; }
                h1 { font-size: 24px; margin-bottom: 10px; }
                h2 { font-size: 20px; margin-bottom: 8px; }
                p, li { line-height: 1.5; }
                ul { margin-left: 20px; }
                .code { font-family: "Consolas", monospace; background-color: #2c2c2c; padding: 2px 4px; border-radius: 4px; }
                a { color: #80cbc4; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>DART Help</h1>
            <p>Welcome to the DART App! This tool allows you to load CSV data, filter and sort it using commands, and export the formatted data.</p>
            <h2>Filter Commands</h2>
            <p>Enter filter commands in the column filter fields. All commands must start with a <span class="code">#</span> symbol. If you do not use a command, a simple case‑insensitive substring search is performed.</p>
            <ul>
                <li><span class="code">#range: x,y</span> &mdash; Show rows where the cell's numeric value is between <em>x</em> and <em>y</em>.</li>
                <li><span class="code">#startswith: text</span> &mdash; Show rows where the cell starts with <em>text</em>.</li>
                <li><span class="code">#contains: text</span> &mdash; Show rows where the cell contains <em>text</em>.</li>
                <li><span class="code">#equals: text</span> &mdash; Show rows where the cell exactly equals <em>text</em>.</li>
                <li><span class="code">#endswith: text</span> &mdash; Show rows where the cell ends with <em>text</em>.</li>
                <li><span class="code">#not: text</span> &mdash; Exclude rows where the cell contains <em>text</em>.</li>
                <li><span class="code">#regex: pattern</span> &mdash; Show rows where the cell matches the regular expression <em>pattern</em> (case‑insensitive).</li>
                <li><span class="code">#in: value1, value2, ...</span> &mdash; Show rows where the cell exactly equals one of the specified values.</li>
            </ul>
            <h2>Global Search</h2>
            <p>The global search bar filters rows across all columns.</p>
            <h2>Useful Buttons</h2>
            <ul>
                <li><strong>Reset Sorting:</strong> Reverts to the original CSV order.</li>
                <li><strong>Resize Columns:</strong> Adjusts column widths to automatically fit their content.</li>
                <li><strong>Statistics:</strong> Displays summary statistics for numeric columns.</li>
            </ul>
            <p>For more information, visit our github page: github.com/vxco/dart</p>
        </body>
        </html>
        """
        self.text_browser.setHtml(help_html)
        layout.addWidget(self.text_browser)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class CSVFilterSortApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DART | Data Access and Reformatting Tool")
        self.resize(1200, 700)
        self.dark_mode = True
        self.init_ui()

    def init_ui(self):
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self.splitter)

        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        self.splitter.addWidget(self.left_panel)

        search_layout = QHBoxLayout()
        search_label = QLabel("Global Search:")
        self.global_search_edit = QLineEdit()
        self.global_search_edit.setPlaceholderText("Search all columns...")
        self.global_search_edit.textChanged.connect(self.update_global_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.global_search_edit)
        left_layout.addLayout(search_layout)

        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.open_context_menu)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        left_layout.addWidget(self.table_view)

        self.filter_panel = QFrame()
        self.filter_panel.setFrameShape(QFrame.StyledPanel)
        self.filter_panel.setMinimumWidth(300)
        self.filter_layout = QVBoxLayout(self.filter_panel)
        self.splitter.addWidget(self.filter_panel)

        self.clear_filters_btn = QPushButton("Clear All Filters")
        self.clear_filters_btn.clicked.connect(self.clear_filters)
        self.filter_layout.addWidget(self.clear_filters_btn)

        self.filter_form = QFormLayout()
        self.filter_layout.addLayout(self.filter_form)
        self.filter_layout.addStretch()

        self.statusBar().showMessage("Ready")

        self.model = QStandardItemModel(self)
        self.proxy_model = MultiFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)

        self.filter_editors = {}
        self.create_menus_and_toolbar()
        self.apply_dark_mode()

    def create_menus_and_toolbar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        open_action = QAction("Open CSV", self)
        open_action.triggered.connect(self.open_csv)
        file_menu.addAction(open_action)

        export_action = QAction("Export CSV", self)
        export_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        save_settings_action = QAction("Save Settings", self)
        save_settings_action.triggered.connect(self.save_settings)
        file_menu.addAction(save_settings_action)

        load_settings_action = QAction("Load Settings", self)
        load_settings_action.triggered.connect(self.load_settings)
        file_menu.addAction(load_settings_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("&Help")
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(open_action)
        toolbar.addAction(export_action)
        toolbar.addAction(save_settings_action)
        toolbar.addAction(load_settings_action)

        clear_filters_action = QAction("Clear Filters", self)
        clear_filters_action.triggered.connect(self.clear_filters)
        toolbar.addAction(clear_filters_action)

        reset_sort_action = QAction("Reset Sorting", self)
        reset_sort_action.triggered.connect(self.reset_sorting)
        toolbar.addAction(reset_sort_action)

        resize_columns_action = QAction("Resize Columns", self)
        resize_columns_action.triggered.connect(self.resize_columns)
        toolbar.addAction(resize_columns_action)

        stats_action = QAction("Show Stats", self)
        stats_action.triggered.connect(self.show_stats)
        toolbar.addAction(stats_action)

        toggle_dark_action = QAction("Toggle Dark Mode", self)
        toggle_dark_action.triggered.connect(self.toggle_dark_mode)
        toolbar.addAction(toggle_dark_action)

    def show_help(self):
        dlg = HelpDialog(self)
        dlg.exec()

    def apply_dark_mode(self):
        dark_style = """
        QMainWindow { background-color: #121212; }
        QWidget { background-color: #121212; color: #e0e0e0; }
        QTableView { background-color: #1e1e1e; color: #e0e0e0; gridline-color: #444444; }
        QHeaderView::section { background-color: #2c2c2c; color: #ffffff; padding: 4px; border: none; }
        QLineEdit { background-color: #2c2c2c; color: #e0e0e0; border: 1px solid #555555; border-radius: 4px; padding: 4px; }
        QPushButton { background-color: #3a3a3a; color: #ffffff; border: 1px solid #555555; border-radius: 4px; padding: 6px; }
        QPushButton:hover { background-color: #4a4a4a; }
        QToolBar { background-color: #2c2c2c; border-bottom: 1px solid #555555; }
        QMenu { background-color: #2c2c2c; color: #ffffff; }
        QMenu::item:selected { background-color: #3a3a4a; }
        QStatusBar { background-color: #2c2c2c; color: #e0e0e0; }
        """
        self.setStyleSheet(dark_style)

    def apply_light_mode(self):
        light_style = """
        QMainWindow { background-color: #f0f0f0; }
        QWidget { background-color: #f0f0f0; color: #000000; }
        QTableView { background-color: #ffffff; color: #000000; gridline-color: #cccccc; }
        QHeaderView::section { background-color: #e0e0e0; color: #000000; padding: 4px; border: none; }
        QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #c0c0c0; border-radius: 4px; padding: 4px; }
        QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 4px; padding: 6px; }
        QPushButton:hover { background-color: #45a049; }
        QToolBar { background-color: #e0e0e0; border-bottom: 1px solid #c0c0c0; }
        QMenu { background-color: #ffffff; color: #000000; }
        QMenu::item:selected { background-color: #dddddd; }
        QStatusBar { background-color: #e0e0e0; color: #000000; }
        """
        self.setStyleSheet(light_style)

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()
        self.statusBar().showMessage("Dark mode enabled" if self.dark_mode else "Light mode enabled", 3000)

    def update_global_search(self, text):
        self.proxy_model.setGlobalFilter(text)

    def open_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                with open(file_name, newline="", encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile)
                    data = list(reader)
                if not data:
                    QMessageBox.warning(self, "Empty File", "The CSV file is empty.")
                    return

                headers = data[0]
                self.model.clear()

                new_headers = ["_index_"] + headers
                self.model.setColumnCount(len(new_headers))
                self.model.setHorizontalHeaderLabels(new_headers)

                for idx, row in enumerate(data[1:]):
                    index_item = QStandardItem()
                    index_item.setData(idx, Qt.DisplayRole)  #int
                    items = [index_item] + [QStandardItem(field) for field in row]
                    self.model.appendRow(items)

                self.table_view.setColumnHidden(0, True)
                self.statusBar().showMessage(f"Loaded {file_name}")
                self.setup_filters(headers)
                self.resize_columns()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load CSV file:\n{e}")

    def setup_filters(self, headers):
        while self.filter_form.rowCount() > 0:
            self.filter_form.removeRow(0)
        self.filter_editors.clear()

        for col, header in enumerate(headers, start=1):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Filter {header} (#range, #startswith, etc.)")
            line_edit.textChanged.connect(lambda text, col=col: self.proxy_model.setFilterForColumn(col, text))
            self.filter_form.addRow(header, line_edit)
            self.filter_editors[col] = line_edit

    def clear_filters(self):
        for editor in self.filter_editors.values():
            editor.clear()
        self.global_search_edit.clear()
        self.statusBar().showMessage("Filters cleared", 3000)

    def reset_sorting(self):
        self.table_view.sortByColumn(0, Qt.AscendingOrder)
        self.statusBar().showMessage("Sorting reset to original order", 3000)

    def resize_columns(self):
        self.table_view.resizeColumnsToContents()
        self.statusBar().showMessage("Columns resized", 3000)

    def export_csv(self):
        if self.model.rowCount() == 0:
            QMessageBox.information(self, "No Data", "No data to export.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Export CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    headers = [self.model.headerData(i, Qt.Horizontal) for i in range(1, self.model.columnCount())]
                    writer.writerow(headers)
                    for row in range(self.proxy_model.rowCount()):
                        row_data = []
                        for col in range(1, self.proxy_model.columnCount()):
                            index = self.proxy_model.index(row, col)
                            row_data.append(self.proxy_model.data(index, Qt.DisplayRole))
                        writer.writerow(row_data)
                self.statusBar().showMessage(f"Exported data to {file_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export CSV file:\n{e}")

    def save_settings(self):
        if self.model.columnCount() <= 1:
            QMessageBox.information(self, "No Data", "No settings to save without loaded data.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "JSON Files (*.json)")
        if file_name:
            try:
                settings = {}
                filter_settings = {str(col): editor.text() for col, editor in self.filter_editors.items()}
                settings["filters"] = filter_settings

                header = self.table_view.horizontalHeader()
                sort_section = header.sortIndicatorSection()
                sort_order = header.sortIndicatorOrder()
                settings["sort"] = {"section": sort_section, "order": int(sort_order)}
                with open(file_name, "w", encoding="utf-8") as jsonfile:
                    json.dump(settings, jsonfile, indent=4)
                self.statusBar().showMessage(f"Settings saved to {file_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save settings:\n{e}")

    def load_settings(self):
        if self.model.columnCount() <= 1:
            QMessageBox.information(self, "No Data", "Load a CSV before loading settings.")
            return

        file_name, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as jsonfile:
                    settings = json.load(jsonfile)
                filter_settings = settings.get("filters", {})
                for col_str, text in filter_settings.items():
                    col = int(col_str)
                    if col in self.filter_editors:
                        self.filter_editors[col].setText(text)
                sort_settings = settings.get("sort", {})
                section = sort_settings.get("section", -1)
                order = sort_settings.get("order", int(Qt.AscendingOrder))
                if section >= 0 and section < self.model.columnCount():
                    self.table_view.sortByColumn(section, Qt.SortOrder(order))
                self.statusBar().showMessage(f"Settings loaded from {file_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load settings:\n{e}")

    def show_stats(self):
        dialog = StatsDialog(self.proxy_model, self)
        dialog.exec()

    def open_context_menu(self, position):
        index = self.table_view.indexAt(position)
        if not index.isValid():
            return
        menu = QMenu()
        copy_action = QAction("Copy Cell", self)
        copy_action.triggered.connect(
            lambda: QApplication.clipboard().setText(str(self.proxy_model.data(index, Qt.DisplayRole))))
        menu.addAction(copy_action)
        menu.exec(self.table_view.viewport().mapToGlobal(position))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("DART")
    window = CSVFilterSortApp()
    window.show()
    sys.exit(app.exec())
