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
        root.setContentsMargins(32, 0, 32, 52)

        # ── Hero: CalCal ──
        root.addSpacing(30)
        calcal_lbl = QLabel("CalCal")
        calcal_lbl.setAlignment(Qt.AlignCenter)
        calcal_lbl.setStyleSheet("""
            color: white;
            background: transparent;
            font-size: 82px;
            font-weight: 900;
            font-family: 'Segoe UI';
            letter-spacing: -4px;
        """)
        root.addWidget(calcal_lbl)
        root.addSpacing(4)

        # ── Sub-title ──
        sub = QLabel("Your Smart Calorie Calculator")
        sub.setAlignment(Qt.AlignCenter)
        sub.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sub.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent;")
        root.addWidget(sub)
        root.addSpacing(6)

        tagline = QLabel("Track meals · Hit your goal · Stay healthy")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setFont(QFont("Segoe UI", 11))
        tagline.setStyleSheet("color: rgba(255,255,255,0.58); background: transparent;")
        root.addWidget(tagline)
        root.addSpacing(44)

        # ── Feature cards ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        cards_row.setAlignment(Qt.AlignCenter)
        for emoji, title_text, desc in [
            ("🍱", "Log Meals", "Track every bite"),
            ("🎯", "Set Goals", "Target calories"),
            ("📊", "Weekly", "View progress"),
        ]:
            card = QWidget()
            card.setFixedSize(104, 96)
            card.setStyleSheet("""
                background: rgba(255,255,255,0.13);
                border: 1px solid rgba(255,255,255,0.22);
                border-radius: 18px;
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(0, 12, 0, 10)
            cl.setSpacing(3)
            cl.setAlignment(Qt.AlignCenter)
            e_lbl = QLabel(emoji)
            e_lbl.setFont(QFont("Segoe UI", 22))
            e_lbl.setAlignment(Qt.AlignCenter)
            e_lbl.setStyleSheet("background:transparent; border:none;")
            t_lbl = QLabel(title_text)
            t_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            t_lbl.setAlignment(Qt.AlignCenter)
            t_lbl.setStyleSheet("color:white; background:transparent; border:none;")
            d_lbl = QLabel(desc)
            d_lbl.setFont(QFont("Segoe UI", 8))
            d_lbl.setAlignment(Qt.AlignCenter)
            d_lbl.setStyleSheet("color:rgba(255,255,255,0.55); background:transparent; border:none;")
            cl.addWidget(e_lbl)
            cl.addWidget(t_lbl)
            cl.addWidget(d_lbl)
            cards_row.addWidget(card)
        root.addLayout(cards_row)
        root.addSpacing(52)

        # ── Get Started button ──
        btn = QPushButton("Get Started  →")
        btn.setFixedHeight(54)
        btn.setFixedWidth(260)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: {PRIMARY};
                border: none;
                border-radius: 27px;
                font-weight: bold;
            }}
            QPushButton:hover  {{ background: #E8F5EE; }}
            QPushButton:pressed {{ background: #C8E6D0; }}
        """)
        btn.clicked.connect(self._start)
        row_btn = QHBoxLayout()
        row_btn.setAlignment(Qt.AlignCenter)
        row_btn.addWidget(btn)
        root.addLayout(row_btn)
        root.addSpacing(16)

        # ── Footer ──
        foot = QLabel("Your personal health companion")
        foot.setAlignment(Qt.AlignCenter)
        foot.setFont(QFont("Segoe UI", 10))
        foot.setStyleSheet("color: rgba(255,255,255,0.38); background: transparent;")
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