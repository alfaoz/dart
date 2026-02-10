"""DART color tokens and stylesheet builder."""

import platform

THEMES = {
    "dark": {
        "bg_base":        "#0f1214",
        "bg_surface":     "#151a1e",
        "bg_elevated":    "#1b2228",
        "bg_overlay":     "#212a30",
        "border_subtle":  "#243028",
        "border_default": "#2e3d33",
        "border_strong":  "#3b4e42",
        "text_primary":   "#e2e8e4",
        "text_secondary": "#8a9b90",
        "text_tertiary":  "#5a6e60",
        "accent":         "#3aab4e",
        "accent_hover":   "#2f9240",
        "accent_muted":   "rgba(58,171,78,0.12)",
        "accent_surface": "rgba(58,171,78,0.08)",
        "row_alt":        "#121a1c",
        "row_hover":      "#1a2824",
        "selection_bg":   "rgba(58,171,78,0.18)",
        "selection_text": "#e2e8e4",
        "header_bg":      "#151a1e",
        "header_text":    "#8a9b90",
        "header_hover":   "#1b2228",
        "scrollbar_bg":   "transparent",
        "scrollbar_handle": "#2e3d33",
        "scrollbar_hover":  "#3b4e42",
    },
    "light": {
        "bg_base":        "#f5f8f6",
        "bg_surface":     "#ffffff",
        "bg_elevated":    "#ffffff",
        "bg_overlay":     "#edf2ee",
        "border_subtle":  "#dce5de",
        "border_default": "#c4d1c7",
        "border_strong":  "#a5b8a9",
        "text_primary":   "#141c16",
        "text_secondary": "#4e6252",
        "text_tertiary":  "#7a917e",
        "accent":         "#2f9240",
        "accent_hover":   "#267a34",
        "accent_muted":   "rgba(47,146,64,0.10)",
        "accent_surface": "rgba(47,146,64,0.06)",
        "row_alt":        "#f0f5f1",
        "row_hover":      "#e6ede8",
        "selection_bg":   "rgba(47,146,64,0.12)",
        "selection_text": "#141c16",
        "header_bg":      "#f0f5f1",
        "header_text":    "#4e6252",
        "header_hover":   "#e2eae4",
        "scrollbar_bg":   "transparent",
        "scrollbar_handle": "#c4d1c7",
        "scrollbar_hover":  "#a5b8a9",
    },
}


def sys_font_family():
    s = platform.system()
    if s == "Darwin":
        return ".AppleSystemUIFont"
    if s == "Windows":
        return "Segoe UI"
    return "Inter"


def build_stylesheet(theme: str) -> str:
    t = THEMES[theme]
    return f"""
    QMainWindow {{ background-color: {t['bg_base']}; }}
    QWidget {{ background-color: transparent; color: {t['text_primary']}; }}

    /* Menu bar */
    QMenuBar {{
        background-color: {t['bg_surface']};
        color: {t['text_secondary']};
        border-bottom: 1px solid {t['border_subtle']};
        padding: 2px 4px; font-size: 12px;
    }}
    QMenuBar::item {{ background: transparent; padding: 4px 10px; border-radius: 4px; }}
    QMenuBar::item:selected {{ background: {t['bg_overlay']}; color: {t['text_primary']}; }}

    /* Menus */
    QMenu {{
        background-color: {t['bg_elevated']};
        border: 1px solid {t['border_default']};
        border-radius: 8px; padding: 4px;
    }}
    QMenu::item {{ padding: 6px 28px 6px 12px; border-radius: 4px; color: {t['text_primary']}; }}
    QMenu::item:selected {{ background-color: {t['accent_muted']}; }}
    QMenu::separator {{ height: 1px; background: {t['border_subtle']}; margin: 4px 8px; }}

    /* Search bar */
    QWidget#searchBar {{
        background: {t['bg_surface']};
        border-bottom: 1px solid {t['border_subtle']};
    }}
    QLineEdit#globalSearch {{
        background: {t['bg_elevated']};
        border: 1px solid {t['border_default']};
        border-radius: 8px; padding: 6px 14px;
        font-size: 13px; color: {t['text_primary']};
        selection-background-color: {t['accent']};
    }}
    QLineEdit#globalSearch:focus {{ border: 1.5px solid {t['accent']}; }}

    /* Action bar */
    QWidget#actionBar {{
        background: {t['bg_surface']};
        border-bottom: 1px solid {t['border_subtle']};
    }}
    QPushButton#actionButton {{
        background: transparent; border: none; border-radius: 6px;
        padding: 4px 10px; font-size: 12px; font-weight: 500;
        color: {t['text_secondary']};
    }}
    QPushButton#actionButton:hover {{ background: {t['bg_overlay']}; color: {t['text_primary']}; }}
    QPushButton#actionButton:pressed {{ background: {t['border_subtle']}; }}
    QFrame#toolSep {{ color: {t['border_subtle']}; background: {t['border_subtle']}; }}

    /* Table */
    QTableView {{
        background-color: {t['bg_surface']};
        alternate-background-color: {t['row_alt']};
        color: {t['text_primary']};
        gridline-color: {t['border_subtle']};
        border: none; outline: none; font-size: 13px;
    }}
    QTableView::item {{
        padding: 0px 10px;
        border-bottom: 1px solid {t['border_subtle']};
    }}
    QTableView::item:hover {{ background-color: {t['row_hover']}; }}
    QTableView::item:selected {{
        background-color: {t['selection_bg']};
        color: {t['selection_text']};
    }}

    /* Table header */
    QHeaderView {{ background-color: {t['header_bg']}; border: none; }}
    QHeaderView::section {{
        background-color: {t['header_bg']};
        color: {t['header_text']};
        padding: 8px 10px; border: none;
        border-bottom: 1px solid {t['border_default']};
        border-right: 1px solid {t['border_subtle']};
        font-size: 11px; font-weight: 600;
    }}
    QHeaderView::section:hover {{ background-color: {t['header_hover']}; color: {t['text_primary']}; }}

    /* Column filter bar */
    QWidget#columnFilterBar {{ background: {t['bg_surface']}; border-bottom: 1px solid {t['border_subtle']}; }}
    QLineEdit#colFilter {{
        background: {t['bg_base']}; border: 1px solid {t['border_subtle']};
        border-radius: 4px; padding: 3px 6px; font-size: 11px;
        color: {t['text_primary']};
    }}
    QLineEdit#colFilter:focus {{ border: 1px solid {t['accent']}; }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background: {t['scrollbar_bg']}; width: 8px; margin: 0; border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {t['scrollbar_handle']}; min-height: 30px; border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {t['scrollbar_hover']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; border: none; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
    QScrollBar:horizontal {{
        background: {t['scrollbar_bg']}; height: 8px; margin: 0; border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {t['scrollbar_handle']}; min-width: 30px; border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{ background: {t['scrollbar_hover']}; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; border: none; }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

    /* Status bar */
    QStatusBar {{
        background: {t['bg_surface']}; color: {t['text_tertiary']};
        border-top: 1px solid {t['border_subtle']};
        font-size: 11px; padding: 2px 12px;
    }}
    QStatusBar QLabel {{ color: {t['text_tertiary']}; font-size: 11px; padding: 0 8px; }}

    /* General inputs */
    QLineEdit {{
        background: {t['bg_elevated']}; border: 1px solid {t['border_default']};
        border-radius: 6px; padding: 6px 10px;
        color: {t['text_primary']}; selection-background-color: {t['accent']};
    }}
    QLineEdit:focus {{ border: 1.5px solid {t['accent']}; }}

    /* General buttons */
    QPushButton {{
        background: {t['bg_elevated']}; border: 1px solid {t['border_default']};
        border-radius: 6px; padding: 6px 14px;
        color: {t['text_primary']}; font-weight: 500;
    }}
    QPushButton:hover {{ background: {t['bg_overlay']}; border-color: {t['border_strong']}; }}
    QPushButton:pressed {{ background: {t['border_subtle']}; }}
    QPushButton#primaryButton {{
        background: {t['accent']}; border: none; color: #ffffff;
        border-radius: 8px; padding: 8px 20px; font-size: 13px; font-weight: 600;
    }}
    QPushButton#primaryButton:hover {{ background: {t['accent_hover']}; }}

    /* Dialogs */
    QDialog {{ background: {t['bg_elevated']}; }}

    /* Tooltips */
    QToolTip {{
        background: {t['bg_elevated']}; color: {t['text_primary']};
        border: 1px solid {t['border_default']}; border-radius: 6px;
        padding: 6px 10px; font-size: 12px;
    }}

    /* Empty state */
    QLabel#emptyTitle {{ color: {t['text_secondary']}; font-size: 16px; }}
    QLabel#emptyHint {{ color: {t['text_tertiary']}; font-size: 12px; }}

    /* Dialog labels */
    QLabel#dialogTitle {{ color: {t['text_primary']}; }}
    QLabel#textSecondary {{ color: {t['text_secondary']}; font-size: 13px; }}
    QLabel#textTertiary {{ color: {t['text_tertiary']}; font-size: 12px; }}
    QLabel#versionPill {{
        background: {t['accent_muted']}; color: {t['accent']};
        border-radius: 10px; padding: 4px 12px; font-size: 11px; font-weight: 600;
    }}

    /* Stats / inner table */
    QTableWidget {{
        background-color: {t['bg_surface']}; alternate-background-color: {t['row_alt']};
        color: {t['text_primary']}; gridline-color: {t['border_subtle']};
        border: none; outline: none; font-size: 13px;
    }}
    QTableWidget::item {{ padding: 0px 10px; border-bottom: 1px solid {t['border_subtle']}; }}
    QTableWidget::item:selected {{ background-color: {t['selection_bg']}; color: {t['selection_text']}; }}

    /* Text browser */
    QTextBrowser {{
        background: {t['bg_surface']}; color: {t['text_primary']};
        border: none; font-size: 13px;
    }}

    /* Loading overlay */
    QWidget#loadingOverlay {{ background: rgba(15,18,20,180); }}
    QLabel#loadingText {{ color: {t['text_secondary']}; font-size: 14px; }}
    """
