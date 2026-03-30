# ============================================================
#  panhathai.py  —  Splash Screen + Food Library Dialog
#  Owner: Panhathai
#  Functions:
#    [FN] Profile check → route to Home or ProfileSetup
#    [FN] Flowchart
#    [FN] Search saved foods
#    [FN] Select food → auto-fill form
#    [FN] Delete saved food
# ============================================================
import os
from shared import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog,
    Qt, QFont, QColor, QPainter, QBrush, QLinearGradient, QPainterPath, QPixmap,
    PRIMARY, P_MED, P_LIGHT, P_ACCENT,
    TXT, TXT_MUTED, CARD, BG, RED, R_LIGHT, BORDER,
    _lbl, _input, _btn_primary, _btn_outline, _btn_danger,
    app_data,
)


# ══════════════════════════════════════════════════════════════════════════════
#  SPLASH SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class SplashScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self._build()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0,  QColor("#2E7D52"))
        grad.setColorAt(0.5,  QColor("#3D9960"))
        grad.setColorAt(1.0,  QColor("#1B5E3B"))
        p.fillRect(self.rect(), QBrush(grad))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 18))
        p.drawEllipse(-60, -60, 220, 220)
        p.setBrush(QColor(255, 255, 255, 12))
        p.drawEllipse(self.width() - 110, self.height() - 140, 200, 200)
        p.end()

    def _build(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(0)
        root.setContentsMargins(36, 0, 36, 50)

        badge = QLabel("CALORIE CALCULATOR")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
        badge.setStyleSheet("""
            color: rgba(255,255,255,0.90);
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.30);
            border-radius: 12px;
            padding: 4px 16px;
            letter-spacing: 1.5px;
        """)
        row_badge = QHBoxLayout()
        row_badge.setAlignment(Qt.AlignCenter)
        row_badge.addWidget(badge)
        root.addLayout(row_badge)
        root.addSpacing(32)

        class LogoWidget(QWidget):
            def __init__(self, path, size=140, corner_radius=28):
                super().__init__()
                self.setFixedSize(size, size)
                self._radius = corner_radius
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setStyleSheet("background:transparent;")
                raw = QPixmap(path)
                self._pm = raw.scaled(size, size,
                                      Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation) if not raw.isNull() else raw

            def paintEvent(self, e):
                if self._pm.isNull():
                    return
                p = QPainter(self)
                p.setRenderHint(QPainter.Antialiasing)
                p.setRenderHint(QPainter.SmoothPixmapTransform)
                clip = QPainterPath()
                clip.addRoundedRect(0, 0, self.width(), self.height(),
                                    self._radius, self._radius)
                p.setClipPath(clip)
                x = (self.width()  - self._pm.width())  // 2
                y = (self.height() - self._pm.height()) // 2
                p.drawPixmap(x, y, self._pm)
                p.end()

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_logo_clean.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_logo.png")
        pm_test = QPixmap(logo_path)
        if not pm_test.isNull():
            logo_widget = LogoWidget(logo_path, 148)
        else:
            logo_widget = QLabel("🥗")
            logo_widget.setAlignment(Qt.AlignCenter)
            logo_widget.setFont(QFont("Segoe UI", 46))
            logo_widget.setFixedSize(110, 110)
            logo_widget.setStyleSheet(
                "background:rgba(255,255,255,0.18); border-radius:55px; border:2px solid rgba(255,255,255,0.35);"
            )

        row_icon = QHBoxLayout()
        row_icon.setAlignment(Qt.AlignCenter)
        row_icon.addWidget(logo_widget)
        root.addLayout(row_icon)
        root.addSpacing(20)

        title = QLabel("Reduce your calories")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        root.addWidget(title)
        root.addSpacing(8)

        sub = QLabel("Track your nutrition. Reach your goals.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setFont(QFont("Segoe UI", 12))
        sub.setStyleSheet("color: rgba(255,255,255,0.72); background: transparent;")
        root.addWidget(sub)
        root.addSpacing(44)

        pills_row = QHBoxLayout()
        pills_row.setAlignment(Qt.AlignCenter)
        pills_row.setSpacing(10)
        for emoji, label in [("📋", "Log meals"), ("🎯", "Set goals"), ("📊", "Weekly")]:
            pill = QWidget()
            pill.setStyleSheet("""
                background: rgba(255,255,255,0.16);
                border: 1px solid rgba(255,255,255,0.28);
                border-radius: 18px;
            """)
            pl = QHBoxLayout(pill)
            pl.setContentsMargins(10, 6, 14, 6)
            pl.setSpacing(5)
            el = QLabel(emoji)
            el.setFont(QFont("Segoe UI", 13))
            el.setStyleSheet("background:transparent; border:none;")
            tl = QLabel(label)
            tl.setFont(QFont("Segoe UI", 11))
            tl.setStyleSheet("color: rgba(255,255,255,0.88); background:transparent; border:none;")
            pl.addWidget(el)
            pl.addWidget(tl)
            pills_row.addWidget(pill)
        root.addLayout(pills_row)
        root.addSpacing(40)

        btn = QPushButton("  Get Started  →")
        btn.setFixedHeight(50)
        btn.setFixedWidth(230)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: {PRIMARY};
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover  {{ background: #E8F5EE; }}
            QPushButton:pressed {{ background: #C8E6D0; }}
        """)
        btn.clicked.connect(self._start)   # [FN] Profile check → route to Home or ProfileSetup
        row_btn = QHBoxLayout()
        row_btn.setAlignment(Qt.AlignCenter)
        row_btn.addWidget(btn)
        root.addLayout(row_btn)

        root.addSpacing(18)
        foot = QLabel("Your personal health companion")
        foot.setAlignment(Qt.AlignCenter)
        foot.setFont(QFont("Segoe UI", 10))
        foot.setStyleSheet("color: rgba(255,255,255,0.45); background: transparent;")
        root.addWidget(foot)

    def _start(self):
        # [FN] Profile check → route to Home or ProfileSetup
        if app_data.profile.is_complete():
            self.mw.show_diary()
        else:
            self.mw.show_profile_setup()


# ══════════════════════════════════════════════════════════════════════════════
#  FOOD LIBRARY DIALOG
# ══════════════════════════════════════════════════════════════════════════════
from shared import Signal

class LibraryDialog(QDialog):
    food_selected = Signal(str, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Food Library")
        self.setMinimumSize(400, 460)
        self.setStyleSheet(f"background:{CARD}; border-radius:12px;")
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        h = QHBoxLayout()
        h.addWidget(_lbl("📚  Saved Foods", bold=True, size=15))
        h.addStretch()
        h.addWidget(_lbl("Double-click to use", color=TXT_MUTED, size=10))
        root.addLayout(h)

        # [FN] Search saved foods
        self.srch = _input("🔍  Search foods...", 38)
        self.srch.textChanged.connect(self._filter)
        root.addWidget(self.srch)

        self.lw = QListWidget()
        self.lw.setFont(QFont("Segoe UI", 12))
        self.lw.itemDoubleClicked.connect(self._pick)   # [FN] Select food → auto-fill form
        root.addWidget(self.lw)

        bot = QHBoxLayout()
        db = _btn_danger("🗑  Delete selected")
        db.clicked.connect(self._delete)               # [FN] Delete saved food
        cb = _btn_outline("Close", h=36)
        cb.clicked.connect(self.reject)
        bot.addWidget(db)
        bot.addStretch()
        bot.addWidget(cb)
        root.addLayout(bot)
        self._populate()

    def _populate(self, q=""):
        self.lw.clear()
        foods = app_data.food_library.search(q) if q else app_data.food_library.all()
        for f in foods:
            it = QListWidgetItem(f"  {f.name}  ·  {f.cal_per_100g} kcal/100g")
            it.setData(Qt.UserRole, (f.name, f.cal_per_100g))
            self.lw.addItem(it)
        if not foods:
            ph = QListWidgetItem("  (No saved foods yet)")
            ph.setFlags(Qt.NoItemFlags)
            ph.setForeground(QColor(TXT_MUTED))
            self.lw.addItem(ph)

    def _filter(self, t): self._populate(t)         # [FN] Search saved foods

    def _pick(self, it):
        # [FN] Select food → auto-fill form
        d = it.data(Qt.UserRole)
        if d: self.food_selected.emit(d[0], d[1]); self.accept()

    def _delete(self):
        # [FN] Delete saved food
        it = self.lw.currentItem()
        if it:
            d = it.data(Qt.UserRole)
            if d: app_data.food_library.remove(d[0]); self._populate(self.srch.text())
