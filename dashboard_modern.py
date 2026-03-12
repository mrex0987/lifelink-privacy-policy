"""
Modern PyQt6 Dashboard — Logistics Operations
==============================================
A visually stunning dashboard with:
  - Color-coded stat cards (blue, green, purple, orange)
  - Emoji icons throughout the UI
  - QPropertyAnimation hover effects
  - QGraphicsDropShadowEffect shadows
  - Animated status badges
  - Search/filter functionality
  - Action buttons per row (View, Edit, Delete)
  - Metric trend indicators
  - Custom styled scrollbars
  - Summary footer
  - Section dividers
"""

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QPushButton,
    QLineEdit, QScrollArea, QSizePolicy, QSpacerItem,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QRect, QTimer, pyqtProperty, QPoint
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QLinearGradient,
    QPainter, QBrush, QIcon
)
import sys


# ─────────────────────────────────────────────
# CARD GRADIENTS  (start color → end color)
# ─────────────────────────────────────────────
CARD_THEMES = [
    {
        "gradient_start": "#1D4ED8",
        "gradient_end":   "#3B82F6",
        "accent":         "#BFDBFE",
        "shadow":         "#1D4ED8",
    },
    {
        "gradient_start": "#065F46",
        "gradient_end":   "#10B981",
        "accent":         "#A7F3D0",
        "shadow":         "#065F46",
    },
    {
        "gradient_start": "#4C1D95",
        "gradient_end":   "#8B5CF6",
        "accent":         "#DDD6FE",
        "shadow":         "#4C1D95",
    },
    {
        "gradient_start": "#92400E",
        "gradient_end":   "#F59E0B",
        "accent":         "#FDE68A",
        "shadow":         "#92400E",
    },
]

STATUS_META = {
    "Delivered":  {"icon": "✓",  "color": "#10B981", "bg": "#ECFDF5", "border": "#A7F3D0"},
    "In Transit": {"icon": "→",  "color": "#3B82F6", "bg": "#EFF6FF", "border": "#BFDBFE"},
    "Pending":    {"icon": "⏳", "color": "#F59E0B", "bg": "#FFFBEB", "border": "#FDE68A"},
    "Delayed":    {"icon": "⚠️", "color": "#EF4444", "bg": "#FEF2F2", "border": "#FECACA"},
}


# ─────────────────────────────────────────────
# MODERN CARD
# ─────────────────────────────────────────────
class ModernCard(QFrame):
    """
    Stat card with unique gradient background, emoji icon,
    trend indicator, and hover animation.
    """

    def __init__(self, title: str, value: str, icon: str,
                 trend: str, theme: dict):
        super().__init__()

        self._theme = theme
        self._base_shadow_blur = 18
        self._hover_shadow_blur = 32

        self.setMinimumHeight(150)
        self.setMinimumWidth(180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Drop-shadow effect
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(self._base_shadow_blur)
        self._shadow.setOffset(0, 6)
        self._shadow.setColor(QColor(theme["shadow"] + "60"))
        self.setGraphicsEffect(self._shadow)

        # Apply gradient stylesheet
        self._apply_style(hover=False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(6)

        # ── top row: icon + title ──
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 22))
        icon_label.setStyleSheet("color: rgba(255,255,255,0.9);")
        icon_label.setFixedWidth(36)

        title_label = QLabel(title)
        title_label.setFont(self._font(13, QFont.Weight.Medium))
        title_label.setStyleSheet("color: rgba(255,255,255,0.85);")
        title_label.setWordWrap(True)

        top_row.addWidget(icon_label)
        top_row.addWidget(title_label, 1)

        # ── value ──
        value_label = QLabel(value)
        value_label.setFont(self._font(34, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #FFFFFF;")

        # ── trend ──
        trend_label = QLabel(trend)
        trend_label.setFont(self._font(11, QFont.Weight.Normal))
        trend_label.setStyleSheet(f"color: {theme['accent']};")

        # ── separator line ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: rgba(255,255,255,0.2);")

        layout.addLayout(top_row)
        layout.addWidget(sep)
        layout.addWidget(value_label)
        layout.addWidget(trend_label)
        layout.addStretch()

    # ── helpers ────────────────────────────────
    @staticmethod
    def _font(size: int, weight: QFont.Weight) -> QFont:
        f = QFont("Segoe UI", size)
        f.setWeight(weight)
        return f

    def _apply_style(self, hover: bool):
        gs = self._theme["gradient_start"]
        ge = self._theme["gradient_end"]
        radius = "18px" if hover else "16px"
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {gs},
                    stop:1 {ge}
                );
                border-radius: {radius};
                border: none;
            }}
        """)

    # ── hover events ───────────────────────────
    def enterEvent(self, event):
        self._apply_style(hover=True)
        anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self._base_shadow_blur)
        anim.setEndValue(self._hover_shadow_blur)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_style(hover=False)
        anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self._hover_shadow_blur)
        anim.setEndValue(self._base_shadow_blur)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        super().leaveEvent(event)


# ─────────────────────────────────────────────
# STATUS BADGE
# ─────────────────────────────────────────────
class StatusBadge(QLabel):
    """
    Status badge with icon and color coding.
    Uses QGraphicsOpacityEffect for a smooth fade-in entrance animation.
    """

    def __init__(self, status: str):
        meta = STATUS_META.get(status, {"icon": "?", "color": "#6B7280",
                                        "bg": "#F3F4F6", "border": "#D1D5DB"})
        text = f"  {meta['icon']}  {status}  "
        super().__init__(text)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI Emoji", 11, QFont.Weight.DemiBold))
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {meta['bg']};
                color: {meta['color']};
                border: 1.5px solid {meta['border']};
                border-radius: 20px;
                padding: 5px 10px;
                font-size: 12px;
            }}
        """)
        self.setFixedHeight(34)

        # Fade-in entrance animation via QGraphicsOpacityEffect
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(350)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        # Start after the widget is shown so the animation is visible
        QTimer.singleShot(0, self._fade_anim.start)


# ─────────────────────────────────────────────
# ACTION BUTTON
# ─────────────────────────────────────────────
class ActionButton(QPushButton):
    """Small inline action button for table rows."""

    STYLES = {
        "View":   ("#3B82F6", "#EFF6FF", "#BFDBFE"),
        "Edit":   ("#10B981", "#ECFDF5", "#A7F3D0"),
        "Delete": ("#EF4444", "#FEF2F2", "#FECACA"),
    }

    def __init__(self, label: str):
        super().__init__(label)
        color, bg, border = self.STYLES.get(label, ("#6B7280", "#F3F4F6", "#D1D5DB"))
        self.setFixedHeight(30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px 10px;
            }}
            QPushButton:hover {{
                background: {color};
                color: white;
            }}
            QPushButton:pressed {{
                background: {color};
                color: white;
                border: none;
            }}
        """)


# ─────────────────────────────────────────────
# DIVIDER
# ─────────────────────────────────────────────
class SectionDivider(QFrame):
    """Thin horizontal divider for visual organisation."""

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet("background: #E5E7EB; border: none;")


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
class DashboardHome(QWidget):
    """
    Modern logistics dashboard with:
      - Animated gradient stat cards
      - Search/filter bar
      - Icon-rich shipment table with action buttons
      - Summary footer
    """

    # Column indices for _DEMO_DATA tuples: (lr_no, sender, destination, status, amount)
    _COL_LR_NO       = 0
    _COL_SENDER      = 1
    _COL_DESTINATION = 2
    _COL_STATUS      = 3
    _COL_AMOUNT      = 4

    _DEMO_DATA = [
        ("LR001", "ABC Traders",    "Delhi",     "Delivered",  "₹1,200"),
        ("LR002", "XYZ Ltd",        "Kolkata",   "In Transit", "₹800"),
        ("LR003", "Tech Solutions", "Mumbai",    "Pending",    "₹2,500"),
        ("LR004", "Global Imports", "Bangalore", "In Transit", "₹1,850"),
        ("LR005", "Local Retail",   "Chennai",   "Delivered",  "₹650"),
        ("LR006", "SunTrade Co.",   "Hyderabad", "Delayed",    "₹3,100"),
        ("LR007", "Prime Cargo",    "Pune",      "Pending",    "₹990"),
        ("LR008", "Apex Exports",   "Ahmedabad", "Delivered",  "₹4,200"),
    ]

    def __init__(self):
        super().__init__()
        self._all_data = list(self._DEMO_DATA)
        self._build_ui()
        self._load_data(self._all_data)

    # ─────────────────────────────────────────
    # UI CONSTRUCTION
    # ─────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(self._global_stylesheet())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: #F1F5F9; border: none; }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94A3B8; }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar:horizontal {
                background: #F1F5F9;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #CBD5E1;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover { background: #94A3B8; }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal { width: 0; }
        """)

        content = QWidget()
        content.setStyleSheet("background: #F1F5F9;")
        scroll.setWidget(content)

        main = QVBoxLayout(content)
        main.setSpacing(28)
        main.setContentsMargins(36, 36, 36, 36)

        # ── Header ───────────────────────────
        main.addLayout(self._build_header())

        # ── Stat cards ───────────────────────
        main.addLayout(self._build_cards())

        # ── Table section ────────────────────
        main.addWidget(self._build_table_section(), 1)

        main.addStretch()
        root.addWidget(scroll)

    # ── Header ─────────────────────────────────
    def _build_header(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(4)

        title = QLabel("🚚  Dashboard Overview")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #0F172A;")

        subtitle = QLabel("Real-time overview of your logistics operations")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #64748B;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(SectionDivider())
        return layout

    # ── Stat cards ─────────────────────────────
    def _build_cards(self) -> QHBoxLayout:
        cards = [
            ("Total Shipments",    "1,234", "📦", "+8.3% from yesterday",  CARD_THEMES[0]),
            ("Revenue Today",      "₹42,500","💰", "+12.5% from yesterday", CARD_THEMES[1]),
            ("Pending Deliveries", "48",    "🕐", "−3.1% from yesterday",  CARD_THEMES[2]),
            ("Active Customers",   "287",   "👥", "+5.7% from yesterday",  CARD_THEMES[3]),
        ]

        layout = QHBoxLayout()
        layout.setSpacing(20)

        for title, value, icon, trend, theme in cards:
            layout.addWidget(ModernCard(title, value, icon, trend, theme))

        return layout

    # ── Table section ──────────────────────────
    def _build_table_section(self) -> QFrame:
        container = QFrame()
        container.setObjectName("tableContainer")
        container.setStyleSheet("""
            QFrame#tableContainer {
                background: white;
                border-radius: 18px;
                border: 1px solid #E2E8F0;
            }
        """)

        # Drop-shadow on the table card
        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor("#64748B30"))
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # ── Table header row ─────────────────
        header_row = QHBoxLayout()

        tbl_title = QLabel("📋  Recent Shipments")
        tbl_title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        tbl_title.setStyleSheet("color: #0F172A;")

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Search shipments…")
        self._search.setMinimumWidth(240)
        self._search.setMaximumWidth(320)
        self._search.setFixedHeight(38)
        self._search.setFont(QFont("Segoe UI", 11))
        self._search.setStyleSheet("""
            QLineEdit {
                background: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 10px;
                padding: 0 14px;
                color: #334155;
            }
            QLineEdit:focus {
                border: 1.5px solid #3B82F6;
                background: white;
            }
        """)
        self._search.textChanged.connect(self._filter_table)

        header_row.addWidget(tbl_title)
        header_row.addStretch()
        header_row.addWidget(self._search)

        layout.addLayout(header_row)
        layout.addWidget(SectionDivider())

        # ── Table ────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "  LR No", "  Sender", "  Destination", "  Status", "  Amount", "  Actions"
        ])

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 200)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setMinimumHeight(320)

        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                border-radius: 0;
                gridline-color: transparent;
                outline: none;
            }
            QTableWidget::item {
                padding: 0 8px;
                border-bottom: 1px solid #F1F5F9;
                color: #334155;
            }
            QTableWidget::item:selected {
                background: #EFF6FF;
                color: #1E40AF;
            }
            QTableWidget::item:hover {
                background: #F8FAFC;
            }
            QHeaderView::section {
                background: #F8FAFC;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                padding: 12px 8px;
                font-size: 12px;
                font-weight: 700;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)

        layout.addWidget(self.table)

        # ── Footer / summary bar ─────────────
        layout.addWidget(SectionDivider())
        layout.addLayout(self._build_footer())

        return container

    # ── Footer ─────────────────────────────────
    def _build_footer(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(24)

        self._footer_count = QLabel()
        self._footer_count.setFont(QFont("Segoe UI", 11))
        self._footer_count.setStyleSheet("color: #64748B;")

        self._footer_total = QLabel()
        self._footer_total.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self._footer_total.setStyleSheet("color: #0F172A;")

        layout.addWidget(self._footer_count)
        layout.addStretch()
        layout.addWidget(self._footer_total)
        return layout

    # ─────────────────────────────────────────
    # DATA LOADING / FILTERING
    # ─────────────────────────────────────────
    def _load_data(self, data: list):
        self.table.setRowCount(0)

        for row_idx, row_data in enumerate(data):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 52)

            lr_no, sender, destination, status, amount = row_data

            # Text cells
            text_cells = [
                (self._COL_LR_NO,       lr_no),
                (self._COL_SENDER,      sender),
                (self._COL_DESTINATION, destination),
                (self._COL_AMOUNT,      amount),
            ]
            for col, text in text_cells:
                item = QTableWidgetItem(f"  {text}")
                item.setFont(QFont("Segoe UI", 12))
                self.table.setItem(row_idx, col, item)

            # Status badge (col 3 = _COL_STATUS)
            badge_wrapper = QWidget()
            badge_layout = QHBoxLayout(badge_wrapper)
            badge_layout.setContentsMargins(8, 6, 8, 6)
            badge_layout.addWidget(StatusBadge(status))
            badge_layout.addStretch()
            self.table.setCellWidget(row_idx, self._COL_STATUS, badge_wrapper)

            # Action buttons (col 5)
            btn_wrapper = QWidget()
            btn_layout = QHBoxLayout(btn_wrapper)
            btn_layout.setContentsMargins(6, 6, 6, 6)
            btn_layout.setSpacing(6)

            for label in ("View", "Edit", "Delete"):
                btn = ActionButton(label)
                # Capture row/label for callback
                btn.clicked.connect(self._make_action_handler(row_idx, label, lr_no))
                btn_layout.addWidget(btn)

            self.table.setCellWidget(row_idx, 5, btn_wrapper)

        self._update_footer(data)

    def _filter_table(self, query: str):
        q = query.strip().lower()
        if not q:
            filtered = self._all_data
        else:
            filtered = [
                row for row in self._all_data
                if any(q in cell.lower() for cell in row)
            ]
        self._load_data(filtered)

    def _update_footer(self, data: list):
        count = len(data)
        self._footer_count.setText(
            f"Showing {count} shipment{'s' if count != 1 else ''}"
        )

        total = 0
        for row in data:
            try:
                total += int(row[self._COL_AMOUNT].replace("₹", "").replace(",", ""))
            except ValueError:
                pass
        self._footer_total.setText(
            f"Total Revenue: ₹{total:,}"
        )

    # ─────────────────────────────────────────
    # ACTION HANDLERS
    # ─────────────────────────────────────────
    def _make_action_handler(self, row: int, action: str, lr_no: str):
        """
        Returns a closure for the given action on the given shipment.
        Uses `lr_no` as the stable identifier — it remains correct even
        when the table is filtered and display row indices change.
        """
        def handler():
            print(f"[{action}] Shipment {lr_no} (display row {row})")
        return handler

    # ─────────────────────────────────────────
    # GLOBAL STYLESHEET
    # ─────────────────────────────────────────
    @staticmethod
    def _global_stylesheet() -> str:
        return """
            QWidget {
                font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #F1F5F9;
            }
        """


# ─────────────────────────────────────────────
# ENTRY POINT (standalone testing)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = QWidget()
    window.setWindowTitle("Modern Logistics Dashboard")
    window.resize(1280, 820)

    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(DashboardHome())

    window.show()
    sys.exit(app.exec())
