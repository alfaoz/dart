"""DART splash screen shown instantly on startup."""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QApplication,
)

from theme import sys_font_family


class SplashScreen(QWidget):
    """Frameless, dark splash with logo + app name. Fades out when done."""

    def __init__(self, logo_path: str = ""):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(360, 280)

        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                geo.x() + (geo.width() - self.width()) // 2,
                geo.y() + (geo.height() - self.height()) // 2,
            )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(40, 40, 40, 40)

        # Logo
        if logo_path:
            logo_lbl = QLabel()
            px = QPixmap(logo_path)
            if not px.isNull():
                logo_lbl.setPixmap(
                    px.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logo_lbl.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_lbl)

        # Title
        title = QLabel("DART")
        title.setFont(QFont(sys_font_family(), 26, QFont.Bold))
        title.setStyleSheet("color: #e2e8e4;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        sub = QLabel("Data Access and Reformatting Tool")
        sub.setFont(QFont(sys_font_family(), 11))
        sub.setStyleSheet("color: #6a7e6e;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        # Loading dots
        self._dots = QLabel("Loading...")
        self._dots.setFont(QFont(sys_font_family(), 10))
        self._dots.setStyleSheet("color: #3aab4e;")
        self._dots.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._dots)

        # Opacity for fade-out
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#0f1214"))
        p.setPen(QColor("#243028"))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)

    def fade_out(self, on_done=None):
        anim = QPropertyAnimation(self._opacity, b"opacity")
        anim.setDuration(400)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        if on_done:
            anim.finished.connect(on_done)
        anim.finished.connect(self.close)
        anim.start()
        self._fade_anim = anim
