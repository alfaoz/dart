#!/usr/bin/env python3
"""DART - Data Access and Reformatting Tool.

Entry point with instant splash screen.
"""

import sys
import os

# Ensure the project root is on the path so local imports work.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer

from theme import sys_font_family
from splash import SplashScreen

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DART")
    app.setFont(QFont(sys_font_family(), 13))

    # Show splash immediately
    splash = SplashScreen(LOGO_PATH)
    splash.show()
    app.processEvents()

    # Import & build the heavy window after splash is visible
    from app import CSVFilterSortApp

    window = CSVFilterSortApp()

    def finish():
        window.show()
        splash.fade_out()

    # Small delay so the splash is visible even on fast machines
    QTimer.singleShot(600, finish)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
