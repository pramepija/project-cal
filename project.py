import sys, uuid, re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QCheckBox, QRadioButton, QButtonGroup, QComboBox, QCompleter,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox, QMessageBox,
    QSizePolicy, QProgressBar, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal, QStringListModel, QRect, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import (
    QFont, QDoubleValidator, QIntValidator, QColor,
    QPainter, QBrush, QPen, QLinearGradient, QPainterPath, QPixmap,
)

# ══════════════════════════════════════════════════════════════════════════════
#  THEME  — Vibrant Modern Health App
# ══════════════════════════════════════════════════════════════════════════════
BG        = "#F4F7F4"
BG2       = "#E8F0E8"
CARD      = "#FFFFFF"
BORDER    = "#D4E6D4"
PRIMARY   = "#1B5E3B"   # Deep emerald
P_MED     = "#2E7D52"   # Medium emerald
P_LIGHT   = "#C8EDD4"   # Soft mint
P_ACCENT  = "#43C47A"   # Vivid green accent
P_GLOW    = "#A8E6C0"   # Glow mint

RED       = "#E53935"
R_LIGHT   = "#FDECEA"
ORANGE    = "#F57C00"
O_LIGHT   = "#FFF3E0"
YELLOW    = "#FBC02D"
Y_LIGHT   = "#FFFDE7"
BLUE      = "#1976D2"
B_LIGHT   = "#E3F2FD"
PURPLE    = "#7B1FA2"
PU_LIGHT  = "#F3E5F5"

GRAY      = "#78909C"
L_GRAY    = "#E0E7E0"
TXT       = "#1A2E22"
TXT_SUB   = "#3D5A46"
TXT_MUTED = "#90A4A0"
SHADOW    = "rgba(27,94,59,0.12)"

# Per-meal accent colours  (icon-bg, border, text)
MEAL_STYLE = {
    "Breakfast": (Y_LIGHT,  YELLOW,  "#7B5800"),
    "Lunch":     (P_LIGHT,  P_ACCENT, PRIMARY),
    "Dinner":    (B_LIGHT,  BLUE,    "#0D47A1"),
    "Snacks":    (PU_LIGHT, PURPLE,  "#4A0072"),
}

STATUS_COLOR = {"low": ORANGE, "balanced": P_MED, "high": RED}
STATUS_BG    = {"low": O_LIGHT, "balanced": P_LIGHT, "high": R_LIGHT}

APP_STYLE = f"""
* {{ font-family: 'Segoe UI', 'Noto Sans Thai', Arial, sans-serif; }}
QWidget {{ background: transparent; color: {TXT}; font-size: 13px; }}
QMainWindow {{ background: {BG}; }}
QDialog {{ background: {CARD}; border-radius: 14px; }}
QScrollArea {{ border: none; background: {BG}; }}
QScrollBar:vertical {{
    width: 5px; background: transparent; border: none; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {P_GLOW}; border-radius: 3px; min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}
QLineEdit {{
    background: {CARD}; border: 1.5px solid {BORDER};
    border-radius: 12px; padding: 0 14px;
    font-size: 13px; color: {TXT};
    min-height: 42px;
}}
QLineEdit:focus {{
    border: 2px solid {P_ACCENT};
    background: #FAFFFC;
}}
QLineEdit:hover {{ border-color: {P_MED}; }}
QPushButton {{
    border: 1.5px solid {BORDER}; border-radius: 12px;
    font-size: 13px; padding: 0 16px; background: {CARD};
}}
QPushButton:hover {{ background: {BG2}; }}
QTableWidget {{
    background: {CARD}; border: 1.5px solid {BORDER};
    border-radius: 12px; gridline-color: {L_GRAY};
    font-size: 12px; outline: none;
    selection-background-color: {P_LIGHT};
    selection-color: {TXT};
}}
QTableWidget::item {{ padding: 8px 10px; border: none; }}
QTableWidget::item:selected {{ background: {P_LIGHT}; color: {TXT}; }}
QTableWidget::item:hover {{ background: {BG2}; }}
QHeaderView::section {{
    background: {BG2}; color: {TXT_SUB};
    padding: 10px 8px; border: none;
    border-bottom: 1.5px solid {BORDER};
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
}}
QComboBox {{
    background: {CARD}; border: 1.5px solid {BORDER};
    border-radius: 12px; padding: 0 12px; font-size: 13px; min-height: 38px;
}}
QComboBox:focus {{ border-color: {P_ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{ width: 10px; height: 10px; }}
QCheckBox {{ spacing: 8px; font-size: 13px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 5px;
    border: 2px solid {BORDER}; background: {CARD};
}}
QCheckBox::indicator:checked {{ background: {PRIMARY}; border-color: {PRIMARY}; image: none; }}
QCheckBox::indicator:hover {{ border-color: {P_MED}; }}
QRadioButton {{ spacing: 8px; font-size: 13px; }}
QRadioButton::indicator {{
    width: 18px; height: 18px; border-radius: 9px;
    border: 2px solid {BORDER}; background: {CARD};
}}
QRadioButton::indicator:checked {{ background: {PRIMARY}; border-color: {PRIMARY}; }}
QListWidget {{
    background: {CARD}; border: 1.5px solid {BORDER};
    border-radius: 12px; outline: none;
}}
QListWidget::item {{ padding: 10px 14px; border-bottom: 1px solid {L_GRAY}; }}
QListWidget::item:last {{ border-bottom: none; }}
QListWidget::item:selected {{ background: {P_LIGHT}; color: {TXT}; }}
QListWidget::item:hover {{ background: {BG2}; }}
QProgressBar {{
    background: {L_GRAY}; border: none; border-radius: 5px;
    height: 10px; text-align: center; font-size: 0px;
}}
QProgressBar::chunk {{
    border-radius: 5px;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {P_ACCENT}, stop:0.6 {P_MED}, stop:1 {PRIMARY});
}}
QDialogButtonBox QPushButton {{
    min-width: 80px; height: 38px;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PRIMARY},stop:1 {P_MED});
    color: white; border: none; border-radius: 10px; font-weight: bold;
}}
QDialogButtonBox QPushButton:hover {{ background: {P_MED}; }}
"""

# ── Helpers ──────────────────────────────────────────────────────────────────
def _lbl(text, bold=False, size=13, color=TXT):
    l = QLabel(text)
    f = QFont("Segoe UI", size)
    if bold: f.setBold(True)
    l.setFont(f)
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l

def _input(ph="", h=42):
    e = QLineEdit()
    e.setPlaceholderText(ph)
    e.setFixedHeight(h)
    return e

def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"color:{BORDER}; background:{BORDER}; max-height:1px;")
    return f

def _btn_primary(text, h=42):
    b = QPushButton(text)
    b.setFixedHeight(h)
    b.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {PRIMARY}, stop:1 {P_MED});
            color: white; border: none; border-radius: 10px;
            font-size: 14px; font-weight: bold;
            letter-spacing: 0.3px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {P_MED}, stop:1 {P_ACCENT});
        }}
        QPushButton:pressed {{
            background: {PRIMARY};
        }}
    """)
    return b

def _btn_outline(text, h=38):
    b = QPushButton(text)
    b.setFixedHeight(h)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {CARD}; color: {PRIMARY};
            border: 2px solid {PRIMARY}; border-radius: 10px;
            font-size: 13px; font-weight: bold;
        }}
        QPushButton:hover {{
            background: {P_LIGHT}; border-color: {P_MED};
        }}
    """)
    return b

def _btn_danger(text, h=36):
    b = QPushButton(text)
    b.setFixedHeight(h)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {CARD}; color: {RED};
            border: 1.5px solid #FECACA; border-radius: 10px;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background: {R_LIGHT}; border-color: {RED};
        }}
    """)
    return b

_card_counter = [0]
def _card(radius=12):
    _card_counter[0] += 1
    name = f"card_{_card_counter[0]}"
    f = QFrame()
    f.setObjectName(name)
    f.setStyleSheet(f"""
        QFrame#{name} {{
            background: {CARD};
            border: 1.5px solid {BORDER};
            border-radius: {radius}px;
        }}
        QFrame#{name} QLabel {{
            border: none;
            background: transparent;
        }}
        QFrame#{name} QWidget {{
            border: none;
        }}
    """)
    return f

def add_shadow(widget, blur=16, offset_y=4, color_str=SHADOW):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset_y)
    c = QColor()
    c.setNamedColor(color_str.replace("rgba(", "").replace(")", "").split(",")[0])
    rgba = color_str.replace("rgba(", "").replace(")", "").split(",")
    if len(rgba) == 4:
        shadow.setColor(QColor(int(rgba[0]), int(rgba[1]), int(rgba[2]), int(float(rgba[3])*255)))
    widget.setGraphicsEffect(shadow)

# ══════════════════════════════════════════════════════════════════════════════
#  MODELS  (OOP)
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class UserProfile:
    name: str = ""; gmail: str = ""; age: int = 0
    height: float = 0.0; weight: float = 0.0
    gender: str = "Male"; target_weight: float = 0.0

    def calculate_bmr(self) -> float:
        if not (self.weight > 0 and self.height > 0 and self.age > 0):
            return 2000.0
        b = 10 * self.weight + 6.25 * self.height - 5 * self.age
        return round(b + 5 if self.gender == "Male" else b - 161, 1)

    def calculate_target_kcal(self) -> float:
        return round(self.calculate_bmr() * 1.2, 1)

    def is_complete(self) -> bool:
        return bool(self.name and self.age > 0 and self.height > 0 and self.weight > 0)

    def bmi(self) -> Optional[float]:
        if self.height > 0 and self.weight > 0:
            return round(self.weight / ((self.height / 100) ** 2), 1)
        return None


@dataclass
class FoodItem:
    id: str; name: str; cal_per_100g: float
    amount_g: float; meal_type: str; date: date

    def __init__(self, name, cal_per_100g, amount_g, meal_type, entry_date=None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.cal_per_100g = cal_per_100g
        self.amount_g = amount_g
        self.meal_type = meal_type
        self.date = entry_date or date.today()

    @property
    def total_cal(self) -> float:
        return round((self.amount_g / 100) * self.cal_per_100g, 1)


@dataclass
class DailyLog:
    log_date: date
    food_items: List[FoodItem] = field(default_factory=list)
    is_cheat_day: bool = False

    def add_food(self, item: FoodItem):
        self.food_items.append(item)

    def remove_food(self, fid: str):
        self.food_items = [f for f in self.food_items if f.id != fid]

    def get_meal(self, mt: str) -> List[FoodItem]:
        return [f for f in self.food_items if f.meal_type == mt]

    def total_calories(self) -> float:
        return round(sum(f.total_cal for f in self.food_items), 1)

    def meal_calories(self, mt: str) -> float:
        return round(sum(f.total_cal for f in self.get_meal(mt)), 1)


@dataclass
class SavedFood:
    name: str
    cal_per_100g: float


class FoodLibrary:
    def __init__(self):
        self._foods: List[SavedFood] = []

    def add(self, name: str, cal: float):
        ex = self.find(name)
        if ex: ex.cal_per_100g = cal
        else: self._foods.append(SavedFood(name, cal))

    def remove(self, name: str):
        self._foods = [f for f in self._foods if f.name.lower() != name.lower()]

    def find(self, name: str) -> Optional[SavedFood]:
        return next((f for f in self._foods if f.name.lower() == name.lower()), None)

    def search(self, q: str) -> List[SavedFood]:
        return [f for f in self._foods if q.lower() in f.name.lower()]

    def all(self) -> List[SavedFood]:
        return list(self._foods)


class AppData:
    def __init__(self):
        self.profile = UserProfile()
        self.daily_logs: Dict[date, DailyLog] = {}
        self.food_library = FoodLibrary()

    def get_or_create_log(self, d: date) -> DailyLog:
        if d not in self.daily_logs:
            self.daily_logs[d] = DailyLog(d)
        return self.daily_logs[d]

    def get_log(self, d: date) -> Optional[DailyLog]:
        return self.daily_logs.get(d)

    def add_food(self, item: FoodItem):
        self.get_or_create_log(item.date).add_food(item)

    def remove_food(self, d: date, fid: str):
        log = self.get_log(d)
        if log: log.remove_food(fid)

    def toggle_cheat_day(self, d: date):
        log = self.get_or_create_log(d)
        log.is_cheat_day = not log.is_cheat_day

    def weekly_total(self, week: List[date]) -> float:
        return round(sum(
            self.get_log(d).total_calories()
            for d in week
            if self.get_log(d) and not self.get_log(d).is_cheat_day
        ), 1)

    def get_status(self, d: date) -> str:
        log = self.get_log(d)
        target = self.profile.calculate_target_kcal()
        consumed = log.total_calories() if log else 0
        if consumed < target * 0.8: return "low"
        if consumed <= target * 1.1: return "balanced"
        return "high"


app_data = AppData()

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

        import os

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
        btn.clicked.connect(self._start)
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
        if app_data.profile.is_complete():
            self.mw.show_diary()
        else:
            self.mw.show_profile_setup()

# ══════════════════════════════════════════════════════════════════════════════
#  PROFILE SETUP SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class ProfileScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.setStyleSheet(f"background:{BG};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        banner = GradientWidget(PRIMARY, P_MED, "#2E9E60", radius=0, vertical=False)
        banner.setFixedHeight(130)
        bl = QVBoxLayout(banner)
        bl.setAlignment(Qt.AlignCenter)
        bl.setContentsMargins(24, 16, 24, 16)
        av_banner = QLabel("👤")
        av_banner.setAlignment(Qt.AlignCenter)
        av_banner.setFont(QFont("Segoe UI", 32))
        av_banner.setStyleSheet(f"""
            background: rgba(255,255,255,0.18);
            border-radius: 30px;
            border: 2px solid rgba(255,255,255,0.35);
            min-width:60px; max-width:60px;
            min-height:60px; max-height:60px;
        """)
        av_row = QHBoxLayout()
        av_row.setAlignment(Qt.AlignCenter)
        av_row.addWidget(av_banner)
        bl.addLayout(av_row)
        t = QLabel("Create Your Profile")
        t.setAlignment(Qt.AlignCenter)
        t.setFont(QFont("Segoe UI", 14, QFont.Bold))
        t.setStyleSheet("color:white; background:transparent;")
        bl.addWidget(t)
        outer.addWidget(banner)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(20, 20, 20, 32)
        lay.setSpacing(14)
        scroll.setWidget(inner)

        lay.addWidget(_lbl("Full Name", bold=True, size=12, color=TXT_SUB))
        self.name_e = _input("Enter your name")
        self.name_e.textChanged.connect(self._validate_name_inline)
        lay.addWidget(self.name_e)
        self.name_err = QLabel("")
        self.name_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.name_err.setVisible(False)
        lay.addWidget(self.name_err)

        lay.addWidget(_lbl("Email (optional)", bold=True, size=12, color=TXT_SUB))
        self.gmail_e = _input("example@gmail.com")
        self.gmail_e.textChanged.connect(self._validate_email_inline)
        lay.addWidget(self.gmail_e)
        self.email_err = QLabel("")
        self.email_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.email_err.setVisible(False)
        lay.addWidget(self.email_err)

        row = QHBoxLayout()
        row.setSpacing(10)
        err_row = QHBoxLayout()
        err_row.setSpacing(10)

        for label, attr, ph, val in [
            ("Age", "age_e", "yrs", QIntValidator(1, 120)),
            ("Height (cm)", "height_e", "cm", QDoubleValidator(50, 272, 1)),
            ("Weight (kg)", "weight_e", "kg", QDoubleValidator(2, 650, 1)),
        ]:
            col = QVBoxLayout()
            col.setSpacing(6)
            col.addWidget(_lbl(label, bold=True, size=12, color=TXT_SUB))
            ed = _input(ph)
            ed.setValidator(val)
            setattr(self, attr, ed)
            col.addWidget(ed)
            row.addLayout(col)

            err_lbl = QLabel("")
            err_lbl.setStyleSheet(f"color:{RED}; font-size:10px; background:transparent;")
            err_lbl.setVisible(False)
            err_lbl.setWordWrap(True)
            setattr(self, attr.replace("_e", "_err"), err_lbl)
            ecol = QVBoxLayout()
            ecol.addWidget(err_lbl)
            err_row.addLayout(ecol)

        lay.addLayout(row)
        lay.addLayout(err_row)

        self.age_e.textChanged.connect(self._validate_numbers_inline)
        self.height_e.textChanged.connect(self._validate_numbers_inline)
        self.weight_e.textChanged.connect(self._validate_numbers_inline)

        lay.addWidget(_lbl("Gender", bold=True, size=12, color=TXT_SUB))
        gr = QHBoxLayout()
        gr.setSpacing(12)
        self.male_rb = QRadioButton("  Male")
        self.female_rb = QRadioButton("  Female")
        self.male_rb.setChecked(True)
        self.bg = QButtonGroup()
        self.bg.addButton(self.male_rb)
        self.bg.addButton(self.female_rb)
        for rb in (self.male_rb, self.female_rb):
            rb.setStyleSheet(f"""
                QRadioButton {{ color:{TXT}; background:{CARD};
                    border:1.5px solid {BORDER}; border-radius:10px;
                    padding:10px 18px; font-size:13px; }}
                QRadioButton:checked {{ border-color:{PRIMARY}; background:{P_LIGHT}; color:{PRIMARY}; font-weight:bold; }}
                QRadioButton::indicator {{ width:0; height:0; border:none; }}
            """)
            gr.addWidget(rb)
        lay.addLayout(gr)

        lay.addWidget(_lbl("Target Weight (kg)", bold=True, size=12, color=TXT_SUB))
        self.tw_e = _input("Optional — your goal weight")
        self.tw_e.setValidator(QDoubleValidator(2, 650, 1))
        self.tw_e.textChanged.connect(self._validate_tw_inline)
        lay.addWidget(self.tw_e)
        self.tw_err = QLabel("")
        self.tw_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.tw_err.setVisible(False)
        lay.addWidget(self.tw_err)

        lay.addSpacing(8)

        self.bmr_preview = _lbl("Fill in your info to see daily calorie target", size=12, color=TXT_MUTED)
        self.bmr_preview.setAlignment(Qt.AlignCenter)
        self.bmr_preview.setStyleSheet(f"""
            color:{TXT_SUB}; background:{P_LIGHT};
            border-radius:10px; padding:10px;
        """)
        self.bmr_preview.setWordWrap(True)
        lay.addWidget(self.bmr_preview)

        for e in (self.age_e, self.height_e, self.weight_e):
            e.textChanged.connect(self._update_preview)
        self.male_rb.toggled.connect(self._update_preview)

        self.form_err = QLabel("")
        self.form_err.setStyleSheet(f"""
            color:{RED}; font-size:12px; background:{R_LIGHT};
            border-radius:8px; padding:8px 12px;
        """)
        self.form_err.setVisible(False)
        self.form_err.setWordWrap(True)
        lay.addWidget(self.form_err)

        sub = _btn_primary("Create Profile  ✓", h=48)
        sub.clicked.connect(self._submit)
        lay.addWidget(sub)
        lay.addStretch()

    def _validate_name_inline(self, text):
        n = text.strip()
        if not n:
            self.name_err.setVisible(False)
            return
        if re.search(r'[!@#$%^&*()\[\]{}<>/\\|+=~`"\'?;:,_]', n):
            self.name_err.setText("⚠  Name must not contain special symbols (e.g. ! @ # $ % ^ & *)")
            self.name_err.setVisible(True)
        elif not re.search(r'[A-Za-zก-๙]', n):
            self.name_err.setText("⚠  Name must contain at least one letter")
            self.name_err.setVisible(True)
        else:
            self.name_err.setVisible(False)

    def _validate_email_inline(self, text):
        email = text.strip()
        if email and not re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', email):
            self.email_err.setText("⚠  Please enter a valid email address (e.g. example@gmail.com)")
            self.email_err.setVisible(True)
        else:
            self.email_err.setVisible(False)

    def _validate_numbers_inline(self):
        a = self.age_e.text().strip()
        if a:
            try:
                v = int(a)
                if not (1 <= v <= 120):
                    self.age_err.setText("⚠  Age must be between 1 and 120")
                    self.age_err.setVisible(True)
                else:
                    self.age_err.setVisible(False)
            except ValueError:
                self.age_err.setText("⚠  Numbers only")
                self.age_err.setVisible(True)
        else:
            self.age_err.setVisible(False)

        h = self.height_e.text().strip()
        if h:
            try:
                v = float(h)
                if not (50.0 <= v <= 272.0):
                    self.height_err.setText("⚠  50–272 cm")
                    self.height_err.setVisible(True)
                else:
                    self.height_err.setVisible(False)
            except ValueError:
                self.height_err.setText("⚠  Numbers only")
                self.height_err.setVisible(True)
        else:
            self.height_err.setVisible(False)

        w = self.weight_e.text().strip()
        if w:
            try:
                v = float(w)
                if not (2.0 <= v <= 650.0):
                    self.weight_err.setText("⚠  2–650 kg")
                    self.weight_err.setVisible(True)
                else:
                    self.weight_err.setVisible(False)
            except ValueError:
                self.weight_err.setText("⚠  Numbers only")
                self.weight_err.setVisible(True)
        else:
            self.weight_err.setVisible(False)

    def _validate_tw_inline(self, text):
        t = text.strip()
        if t:
            try:
                v = float(t)
                if not (2.0 <= v <= 650.0):
                    self.tw_err.setText("⚠  Target weight must be between 2 and 650 kg")
                    self.tw_err.setVisible(True)
                else:
                    self.tw_err.setVisible(False)
            except ValueError:
                self.tw_err.setText("⚠  Numbers only")
                self.tw_err.setVisible(True)
        else:
            self.tw_err.setVisible(False)

    def _update_preview(self):
        try:
            a = int(self.age_e.text())
            h = float(self.height_e.text())
            w = float(self.weight_e.text())
            g = "Male" if self.male_rb.isChecked() else "Female"
            tmp = UserProfile(age=a, height=h, weight=w, gender=g)
            bmr = tmp.calculate_bmr()
            tgt = tmp.calculate_target_kcal()
            self.bmr_preview.setText(f"BMR: {bmr} kcal  ·  Daily Target (×1.2): {tgt} kcal")
        except (ValueError, ZeroDivisionError):
            self.bmr_preview.setText("Fill in your info to see daily calorie target")

    def _submit(self):
        self.form_err.setVisible(False)
        n     = self.name_e.text().strip()
        a     = self.age_e.text().strip()
        h     = self.height_e.text().strip()
        w     = self.weight_e.text().strip()
        email = self.gmail_e.text().strip()

        if not all([n, a, h, w]):
            self.form_err.setText("⚠  Please fill in all required fields (Name, Age, Height, Weight).")
            self.form_err.setVisible(True)
            return

        if re.search(r'[!@#$%^&*()\[\]{}<>/\\|+=~`"\'?;:,_]', n):
            self.name_err.setText("⚠  Name must not contain special symbols (e.g. ! @ # $ % ^ & *)")
            self.name_err.setVisible(True)
            self.name_e.setFocus(); return

        if not re.search(r'[A-Za-zก-๙]', n):
            self.name_err.setText("⚠  Name must contain at least one letter")
            self.name_err.setVisible(True)
            self.name_e.setFocus(); return

        if email and not re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', email):
            self.email_err.setText("⚠  Please enter a valid email address (e.g. example@gmail.com)")
            self.email_err.setVisible(True)
            self.gmail_e.setFocus(); return

        try:
            age_val = int(a)
            if not (1 <= age_val <= 120):
                self.age_err.setText("⚠  Age must be between 1 and 120")
                self.age_err.setVisible(True)
                self.age_e.setFocus(); return
        except ValueError:
            self.age_err.setText("⚠  Numbers only")
            self.age_err.setVisible(True)
            self.age_e.setFocus(); return

        try:
            height_val = float(h)
            if not (50.0 <= height_val <= 272.0):
                self.height_err.setText("⚠  Height must be between 50 and 272 cm")
                self.height_err.setVisible(True)
                self.height_e.setFocus(); return
        except ValueError:
            self.height_err.setText("⚠  Numbers only")
            self.height_err.setVisible(True)
            self.height_e.setFocus(); return

        try:
            weight_val = float(w)
            if not (2.0 <= weight_val <= 650.0):
                self.weight_err.setText("⚠  Weight must be between 2 and 650 kg")
                self.weight_err.setVisible(True)
                self.weight_e.setFocus(); return
        except ValueError:
            self.weight_err.setText("⚠  Numbers only")
            self.weight_err.setVisible(True)
            self.weight_e.setFocus(); return

        tw_val = 0.0
        if self.tw_e.text().strip():
            try:
                tw_val = float(self.tw_e.text())
                if not (2.0 <= tw_val <= 650.0):
                    self.tw_err.setText("⚠  Target weight must be between 2 and 650 kg")
                    self.tw_err.setVisible(True)
                    self.tw_e.setFocus(); return
            except ValueError:
                self.tw_err.setText("⚠  Numbers only")
                self.tw_err.setVisible(True)
                self.tw_e.setFocus(); return

        app_data.profile = UserProfile(
            name=n, gmail=email,
            age=age_val, height=height_val, weight=weight_val,
            gender="Male" if self.male_rb.isChecked() else "Female",
            target_weight=tw_val,
        )
        self.mw.show_diary()

# ══════════════════════════════════════════════════════════════════════════════
#  DIARY SCREEN (หน้าหลัก)
# ══════════════════════════════════════════════════════════════════════════════
MEALS = ["Breakfast", "Lunch", "Dinner", "Snacks"]
MEAL_ICONS = {"Breakfast": "🌅", "Lunch": "☀️", "Dinner": "🌙", "Snacks": "🍎"}


class GradientWidget(QWidget):
    def __init__(self, c1: str, c2: str, c3: str = None,
                 radius: int = 0, vertical: bool = True, parent=None):
        super().__init__(parent)
        self._c1 = QColor(c1)
        self._c2 = QColor(c2)
        self._c3 = QColor(c3) if c3 else None
        self._radius = radius
        self._vertical = vertical

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self._vertical:
            grad = QLinearGradient(0, 0, 0, self.height())
        else:
            grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, self._c1)
        if self._c3:
            grad.setColorAt(0.5, self._c2)
            grad.setColorAt(1.0, self._c3)
        else:
            grad.setColorAt(1.0, self._c2)
        if self._radius > 0:
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.width(), self.height(),
                                self._radius, self._radius)
            p.fillPath(path, QBrush(grad))
        else:
            p.fillRect(self.rect(), QBrush(grad))
        p.end()


class GradientFrame(QFrame):
    def __init__(self, c1: str, c2: str, c3: str = None,
                 radius: int = 18, vertical: bool = True,
                 border_color: str = None, parent=None):
        super().__init__(parent)
        self._c1 = QColor(c1)
        self._c2 = QColor(c2)
        self._c3 = QColor(c3) if c3 else None
        self._radius = radius
        self._vertical = vertical
        self._border_color = QColor(border_color) if border_color else None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self._vertical:
            grad = QLinearGradient(0, 0, 0, self.height())
        else:
            grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, self._c1)
        if self._c3:
            grad.setColorAt(0.5, self._c2)
            grad.setColorAt(1.0, self._c3)
        else:
            grad.setColorAt(1.0, self._c2)
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width() - 2, self.height() - 2,
                            self._radius, self._radius)
        p.fillPath(path, QBrush(grad))
        if self._border_color:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(self._border_color, 1.5))
            p.drawPath(path)
        p.end()


class PersonIconButton(QWidget):
    clicked_signal = Signal()

    def __init__(self, color=PRIMARY, bg=P_LIGHT, border=P_ACCENT):
        super().__init__()
        self.setFixedSize(40, 40)
        self.setCursor(Qt.PointingHandCursor)
        self._color  = QColor(color)
        self._bg     = QColor(bg)
        self._border = QColor(border)
        self._hover  = False
        self.setStyleSheet("background:transparent;")

    def enterEvent(self, e): self._hover = True;  self.update()
    def leaveEvent(self, e): self._hover = False; self.update()
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked_signal.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W = H = self.width()
        cx, cy = W // 2, H // 2
        r = W // 2 - 1

        bg = QColor(self._border) if self._hover else self._bg
        p.setPen(QPen(self._border, 2))
        p.setBrush(QBrush(bg))
        p.drawEllipse(1, 1, W - 2, H - 2)

        icon_color = QColor("white") if self._hover else self._color

        head_r = int(r * 0.28)
        head_cx = cx
        head_cy = cy - int(r * 0.18)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(icon_color))
        p.drawEllipse(head_cx - head_r, head_cy - head_r,
                      head_r * 2, head_r * 2)

        body_w = int(r * 0.62)
        body_top = head_cy + head_r + 2
        body_h = int(r * 0.38)
        path = QPainterPath()
        path.moveTo(cx - body_w, cy + int(r * 0.42))
        path.arcTo(cx - body_w, body_top,
                   body_w * 2, body_h * 2, 180, 180)
        path.closeSubpath()
        p.setBrush(QBrush(icon_color))
        p.drawPath(path)

        p.end()

class CalorieMeter(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 120)
        self._consumed = 0
        self._target = 2000
        self._is_cheat = False
        self.setStyleSheet("background:transparent;")

    def set_data(self, consumed, target, is_cheat=False):
        self._consumed = consumed
        self._target = target
        self._is_cheat = is_cheat
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        cx, cy = W // 2, H // 2
        r = min(W, H) // 2 - 10
        ring = 9

        p.setPen(QPen(QColor(L_GRAY), ring))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        pct = min(self._consumed / self._target, 1.0) if self._target > 0 else 0
        if self._is_cheat:
            arc_color = QColor(ORANGE)
        elif pct > 1.0:
            arc_color = QColor(RED)
        elif pct >= 0.8:
            arc_color = QColor(P_MED)
        else:
            arc_color = QColor(P_ACCENT)

        if self._is_cheat or pct > 0:
            pen = QPen(arc_color, ring)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            draw_pct = 1.0 if self._is_cheat else pct
            span = int(-draw_pct * 360 * 16)
            p.drawArc(cx - r, cy - r, r * 2, r * 2, 90 * 16, span)

        if self._is_cheat:
            p.setFont(QFont("Segoe UI", 18, QFont.Bold))
            p.setPen(QColor(ORANGE))
            p.drawText(QRect(0, cy - 16, W, 26), Qt.AlignCenter, "∞")
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(QColor(TXT_MUTED))
            p.drawText(QRect(0, cy + 10, W, 16), Qt.AlignCenter, "Cheat Day!")
        else:
            remaining = max(0, int(self._target - self._consumed))
            p.setFont(QFont("Segoe UI", 17, QFont.Bold))
            p.setPen(QColor(TXT))
            p.drawText(QRect(0, cy - 14, W, 24), Qt.AlignCenter, str(remaining))
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(QColor(TXT_MUTED))
            p.drawText(QRect(0, cy + 10, W, 16), Qt.AlignCenter, "remaining")

        p.end()


class DiaryScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.current_date = date.today()
        self.setStyleSheet(f"background:{BG};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = GradientWidget(PRIMARY, P_MED, vertical=False)
        top.setFixedHeight(60)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(16, 0, 16, 0)

        diary_lbl = QLabel("My Diary")
        diary_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        diary_lbl.setStyleSheet("color:white; background:transparent;")

        prof_btn = PersonIconButton(PRIMARY, P_LIGHT, P_ACCENT)
        prof_btn.clicked_signal.connect(self.mw.show_profile_view)
        self.prof_btn = prof_btn

        tl.addWidget(diary_lbl)
        tl.addStretch()
        tl.addWidget(self.prof_btn)
        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll)
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(16, 16, 16, 20)
        il.setSpacing(14)
        scroll.setWidget(inner)

        dn = QHBoxLayout()
        self.prev_btn = QPushButton("‹")
        self.prev_btn.setFixedSize(36, 36)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background:{P_LIGHT}; border:none;
                border-radius:18px; font-size:20px;
                color:{PRIMARY}; font-weight:bold;
                padding-bottom:2px;
            }}
            QPushButton:hover {{ background:{P_ACCENT}; color:white; }}
            QPushButton:pressed {{ background:{PRIMARY}; color:white; }}
        """)
        self.prev_btn.clicked.connect(self._prev)

        self.date_lbl = _lbl("", bold=True, size=15)
        self.date_lbl.setAlignment(Qt.AlignCenter)

        self.next_btn = QPushButton("›")
        self.next_btn.setFixedSize(36, 36)
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.next_btn.clicked.connect(self._next)

        dn.addWidget(self.prev_btn)
        dn.addWidget(self.date_lbl, 1)
        dn.addWidget(self.next_btn)
        il.addLayout(dn)

        self.sum_card = GradientFrame("#EDF9F2", "#FFFFFF", radius=18,
                                       vertical=True, border_color=BORDER)
        self.sum_card.setStyleSheet("")
        scl = QVBoxLayout(self.sum_card)
        scl.setContentsMargins(16, 14, 16, 14)
        scl.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(0)
        self.status_badge = QLabel("↓ Low")
        self.status_badge.setFixedHeight(26)
        self.status_badge.setStyleSheet(f"""
            color:{ORANGE}; background:{O_LIGHT};
            border-radius:13px; padding:0 10px;
            font-size:11px; font-weight:bold;
        """)
        self.cheat_cb = QCheckBox("Cheat Day 🎉")
        self.cheat_cb.setStyleSheet(f"""
            QCheckBox {{ color:{ORANGE}; font-weight:bold; font-size:11px; background:transparent; }}
            QCheckBox::indicator {{ width:15px; height:15px; border-radius:7px;
                border:2px solid {ORANGE}; background:{CARD}; }}
            QCheckBox::indicator:checked {{ background:{ORANGE}; border-color:{ORANGE}; }}
        """)
        self.cheat_cb.stateChanged.connect(self._toggle_cheat)
        top_row.addWidget(self.status_badge)
        top_row.addStretch()
        top_row.addWidget(self.cheat_cb)
        scl.addLayout(top_row)

        mid = QHBoxLayout()
        mid.setSpacing(14)
        mid.setAlignment(Qt.AlignVCenter)

        self.meter = CalorieMeter()
        mid.addWidget(self.meter)

        stats = QVBoxLayout()
        stats.setSpacing(6)
        stats.setAlignment(Qt.AlignVCenter)

        self.food_lbl = _lbl("Eaten  0 kcal", size=12, color=TXT)
        self.goal_lbl = _lbl("Target  0 kcal", size=12, color=TXT_MUTED)

        pb_row = QHBoxLayout()
        pb_row.setSpacing(8)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(7)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.prog_lbl = _lbl("0%", size=10, color=TXT_MUTED)
        self.prog_lbl.setFixedWidth(36)
        pb_row.addWidget(self.progress, 1)
        pb_row.addWidget(self.prog_lbl)

        stats.addWidget(self.food_lbl)
        stats.addWidget(self.goal_lbl)
        stats.addLayout(pb_row)
        mid.addLayout(stats, 1)
        scl.addLayout(mid)
        il.addWidget(self.sum_card)

        il.addWidget(_lbl("Log Meal", bold=True, size=15))

        self.meal_cal_lbl = {}
        for m in MEALS:
            icon_bg, border_col, txt_col = MEAL_STYLE.get(m, (P_LIGHT, P_ACCENT, PRIMARY))
            card = QPushButton()
            card.setFixedHeight(58)
            card.setObjectName(f"mealCard_{m}")
            card.setStyleSheet(f"""
                QPushButton[objectName="mealCard_{m}"] {{
                    background:{CARD}; border:1px solid {BORDER};
                    border-radius:14px; text-align:left;
                }}
                QPushButton[objectName="mealCard_{m}"]:hover {{
                    border-color:{P_ACCENT}; background:{BG};
                }}
                QPushButton[objectName="mealCard_{m}"]:pressed {{
                    background:{P_LIGHT};
                }}
            """)
            card.clicked.connect(lambda _, mt=m: self.mw.show_meal(mt, self.current_date))

            cl = QHBoxLayout(card)
            cl.setContentsMargins(12, 0, 12, 0)
            cl.setSpacing(0)

            icon_bubble = QWidget()
            icon_bubble.setFixedSize(42, 42)
            icon_bubble.setStyleSheet(f"background:{icon_bg}; border-radius:12px; border:none;")
            ibl = QVBoxLayout(icon_bubble)
            ibl.setContentsMargins(0, 0, 0, 0)
            ibl.setAlignment(Qt.AlignCenter)
            icon_lbl = QLabel(MEAL_ICONS.get(m, "🍽"))
            icon_lbl.setFont(QFont("Segoe UI", 17))
            icon_lbl.setAlignment(Qt.AlignCenter)
            icon_lbl.setStyleSheet("background:transparent; border:none;")
            ibl.addWidget(icon_lbl)

            name_lbl = QLabel(m)
            name_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
            name_lbl.setStyleSheet(f"color:{TXT}; background:transparent; border:none;")
            name_lbl.setFixedWidth(88)

            cal_lbl = QLabel("0 kcal")
            cal_lbl.setFont(QFont("Segoe UI", 11))
            cal_lbl.setStyleSheet(f"color:{TXT_MUTED}; background:transparent; border:none;")
            self.meal_cal_lbl[m] = cal_lbl

            arrow_circle = QLabel("›")
            arrow_circle.setFixedSize(32, 32)
            arrow_circle.setAlignment(Qt.AlignCenter)
            arrow_circle.setFont(QFont("Segoe UI", 16, QFont.Bold))
            arrow_circle.setStyleSheet(f"""
                color:{PRIMARY}; background:{P_LIGHT};
                border-radius:16px; border:none;
                padding-bottom:2px;
            """)

            cl.addWidget(icon_bubble)
            cl.addSpacing(12)
            cl.addWidget(name_lbl)
            cl.addWidget(cal_lbl)
            cl.addStretch()
            cl.addWidget(arrow_circle)
            il.addWidget(card)

        wk_btn = QPushButton()
        wk_btn.setFixedHeight(58)
        wk_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {P_LIGHT}, stop:1 #E0F5EC);
                border:1.5px solid {P_ACCENT}55;
                border-radius:14px; text-align:left;
            }}
            QPushButton:hover {{ border-color:{P_ACCENT}; background:{P_LIGHT}; }}
            QPushButton:pressed {{ background:{P_GLOW}; }}
        """)
        wk_inner = QHBoxLayout(wk_btn)
        wk_inner.setContentsMargins(14, 0, 12, 0)
        wk_inner.setSpacing(0)

        wk_icon = QLabel("📊")
        wk_icon.setFont(QFont("Segoe UI", 16))
        wk_icon.setStyleSheet("background:transparent; border:none;")
        wk_icon.setFixedWidth(28)
        wk_inner.addWidget(wk_icon)
        wk_inner.addSpacing(10)

        wk_title = QLabel("Weekly Summary")
        wk_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        wk_title.setStyleSheet(f"color:{TXT}; background:transparent; border:none;")
        wk_inner.addWidget(wk_title)
        wk_inner.addStretch()

        self.weekly_val = QLabel("—")
        self.weekly_val.setFont(QFont("Segoe UI", 11))
        self.weekly_val.setStyleSheet(f"color:{TXT_MUTED}; background:transparent; border:none;")
        wk_inner.addWidget(self.weekly_val)
        wk_inner.addSpacing(8)

        wk_arrow = QLabel("›")
        wk_arrow.setFixedSize(32, 32)
        wk_arrow.setAlignment(Qt.AlignCenter)
        wk_arrow.setFont(QFont("Segoe UI", 16, QFont.Bold))
        wk_arrow.setStyleSheet(f"""
            color:{PRIMARY}; background:{P_LIGHT};
            border-radius:16px; border:none;
            padding-bottom:2px;
        """)
        wk_inner.addWidget(wk_arrow)
        wk_btn.clicked.connect(self.mw.show_weekly)
        il.addWidget(wk_btn)
        il.addStretch()

    def refresh(self, log_date=None):
        if log_date:
            self.current_date = log_date

        today = date.today()
        if self.current_date == today:
            ds = f"Today · {self.current_date.strftime('%d %b %Y')}"
        elif self.current_date == today - timedelta(days=1):
            ds = f"Yesterday · {self.current_date.strftime('%d %b')}"
        else:
            ds = self.current_date.strftime("%A · %d %b %Y")
        self.date_lbl.setText(ds)

        log = app_data.get_log(self.current_date)
        target = app_data.profile.calculate_target_kcal()
        consumed = log.total_calories() if log else 0
        is_cheat = log.is_cheat_day if log else False

        self.cheat_cb.blockSignals(True)
        self.cheat_cb.setChecked(is_cheat)
        self.cheat_cb.blockSignals(False)

        self.meter.set_data(consumed, target, is_cheat)

        if is_cheat:
            self.status_badge.setText("🎉 Cheat Day!")
            self.status_badge.setStyleSheet(f"""
                color:{ORANGE}; background:{O_LIGHT};
                border-radius:13px; padding:0 10px;
                font-size:11px; font-weight:bold;
            """)
            self.progress.setStyleSheet(f"""
                QProgressBar {{ background:{L_GRAY}; border:none; border-radius:3px; }}
                QProgressBar::chunk {{ border-radius:3px; background:{ORANGE}; }}
            """)
            self.progress.setValue(100)
            self.prog_lbl.setText("∞")
            self.prog_lbl.setStyleSheet(f"color:{ORANGE}; background:transparent; font-size:11px; font-weight:bold;")
        else:
            st = app_data.get_status(self.current_date)
            col = STATUS_COLOR.get(st, GRAY)
            bg_col = STATUS_BG.get(st, BG2)
            st_label = {"low": "↓ Low", "balanced": "✓ Balanced", "high": "↑ High"}.get(st, st)
            self.status_badge.setText(st_label)
            self.status_badge.setStyleSheet(f"""
                color:{col}; background:{bg_col};
                border-radius:13px; padding:0 10px;
                font-size:11px; font-weight:bold;
            """)
            pct = int(min(consumed / target * 100, 100)) if target > 0 else 0
            self.progress.setValue(pct)
            self.prog_lbl.setText(f"{pct}%")
            self.prog_lbl.setStyleSheet(f"color:{TXT_MUTED}; background:transparent; font-size:10px;")

            if st == "high":
                chunk_color = RED
            elif st == "balanced":
                chunk_color = P_MED
            else:
                chunk_color = ORANGE
            self.progress.setStyleSheet(f"""
                QProgressBar {{ background:{L_GRAY}; border:none; border-radius:3px; }}
                QProgressBar::chunk {{ border-radius:3px; background:{chunk_color}; }}
            """)

        self.food_lbl.setText(f"Eaten   {int(consumed)} kcal")
        self.goal_lbl.setText(f"Target  {int(target)} kcal")

        for m in MEALS:
            c = log.meal_calories(m) if log else 0
            self.meal_cal_lbl[m].setText(f"{int(c)} kcal" if c else "0 kcal")

        mon = self.current_date - timedelta(days=self.current_date.weekday())
        week = [mon + timedelta(days=i) for i in range(7)]
        wt = app_data.weekly_total(week)
        self.weekly_val.setText(f"{int(wt)} kcal this week")

    def _prev(self):
        self.current_date -= timedelta(days=1)
        self.refresh()

    def _next(self):
        self.current_date += timedelta(days=1)
        self.refresh()

    def _toggle_cheat(self):
        app_data.toggle_cheat_day(self.current_date)
        self.refresh()

# ══════════════════════════════════════════════════════════════════════════════
#  MEAL SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class TrashZone(QFrame):
    delete_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(52)
        self.setAcceptDrops(True)
        self._idle()
        l = QLabel("🗑  Drag here to delete")
        l.setAlignment(Qt.AlignCenter)
        l.setFont(QFont("Segoe UI", 11))
        l.setStyleSheet(f"color:{RED}; background:transparent; border:none;")
        QHBoxLayout(self).addWidget(l)

    def _idle(self):
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed #FECACA;
                border-radius: 12px;
                background: {R_LIGHT};
            }}
        """)

    def _hot(self):
        self.setStyleSheet(f"""
            QFrame {{
                border: 2.5px dashed {RED};
                border-radius: 12px;
                background: #FEE2E2;
            }}
        """)

    def dragEnterEvent(self, e): self._hot(); e.acceptProposedAction()
    def dragLeaveEvent(self, e): self._idle()
    def dropEvent(self, e): self._idle(); self.delete_signal.emit(); e.acceptProposedAction()


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

        self.srch = _input("🔍  Search foods...", 38)
        self.srch.textChanged.connect(self._filter)
        root.addWidget(self.srch)

        self.lw = QListWidget()
        self.lw.setFont(QFont("Segoe UI", 12))
        self.lw.itemDoubleClicked.connect(self._pick)
        root.addWidget(self.lw)

        bot = QHBoxLayout()
        db = _btn_danger("🗑  Delete selected")
        db.clicked.connect(self._delete)
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

    def _filter(self, t): self._populate(t)

    def _pick(self, it):
        d = it.data(Qt.UserRole)
        if d: self.food_selected.emit(d[0], d[1]); self.accept()

    def _delete(self):
        it = self.lw.currentItem()
        if it:
            d = it.data(Qt.UserRole)
            if d: app_data.food_library.remove(d[0]); self._populate(self.srch.text())


class MealScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.meal_type = "Breakfast"
        self.log_date = date.today()
        self.setStyleSheet(f"background:{BG};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = GradientWidget(PRIMARY, P_MED, vertical=False)
        top.setFixedHeight(56)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(12, 0, 12, 0)
        back = QPushButton("‹")
        back.setFixedSize(38, 38)
        back.setStyleSheet(f"""
            QPushButton {{ background:rgba(255,255,255,0.20); border:none;
                border-radius:10px; font-size:20px; color:white; }}
            QPushButton:hover {{ background:rgba(255,255,255,0.35); color:white; }}
        """)
        back.clicked.connect(self._go_back)
        self.title_lbl = _lbl("Breakfast", bold=True, size=17, color="white")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        lib_btn = QPushButton("📚  Library")
        lib_btn.setFixedHeight(34)
        lib_btn.setFixedWidth(110)
        lib_btn.setStyleSheet(f"""
            QPushButton {{ background:rgba(255,255,255,0.20); color:white;
                border:1.5px solid rgba(255,255,255,0.45); border-radius:10px;
                font-size:12px; font-weight:bold; }}
            QPushButton:hover {{ background:rgba(255,255,255,0.35); }}
        """)
        lib_btn.clicked.connect(self._open_lib)
        tl.addWidget(back)
        tl.addWidget(self.title_lbl, 1)
        tl.addWidget(lib_btn)
        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll)
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(16, 16, 16, 16)
        il.setSpacing(12)
        scroll.setWidget(inner)

        add_card = _card()
        acl = QVBoxLayout(add_card)
        acl.setContentsMargins(16, 14, 16, 14)
        acl.setSpacing(8)

        acl.addWidget(_lbl("Add Food", bold=True, size=14))

        self.name_e = _input("Food name (e.g. Steamed rice)")
        self._comp = QCompleter([])
        self._comp.setCaseSensitivity(Qt.CaseInsensitive)
        self._comp.setFilterMode(Qt.MatchContains)
        self._comp.activated.connect(self._comp_pick)
        self.name_e.setCompleter(self._comp)
        self.name_e.textChanged.connect(self._name_changed)
        acl.addWidget(self.name_e)

        cal_amt_row = QHBoxLayout()
        cal_amt_row.setSpacing(10)
        self.cal_e = _input("Kcal / 100g")
        self.cal_e.setValidator(QDoubleValidator(0, 99999, 1))
        self.amt_e = _input("Amount (grams)")
        self.amt_e.setValidator(QDoubleValidator(0, 99999, 1))
        cal_amt_row.addWidget(self.cal_e)
        cal_amt_row.addWidget(self.amt_e)
        acl.addLayout(cal_amt_row)

        self.kcal_preview = _lbl("", size=11, color=TXT_MUTED)
        self.cal_e.textChanged.connect(self._update_kcal_preview)
        self.amt_e.textChanged.connect(self._update_kcal_preview)
        acl.addWidget(self.kcal_preview)

        bottom_row = QHBoxLayout()
        self.save_cb = QCheckBox("Save to library")
        self.save_cb.setChecked(True)
        self.save_cb.setStyleSheet(f"color:{TXT_SUB}; background:transparent; font-size:11px;")
        add_btn = _btn_primary("+ Add Food", h=38)
        add_btn.setFixedWidth(120)
        add_btn.clicked.connect(self._add_food)
        bottom_row.addWidget(self.save_cb)
        bottom_row.addStretch()
        bottom_row.addWidget(add_btn)
        acl.addLayout(bottom_row)

        self.add_err = QLabel("")
        self.add_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.add_err.setVisible(False)
        acl.addWidget(self.add_err)

        il.addWidget(add_card)

        lh = QHBoxLayout()
        lh.addWidget(_lbl("Food List", bold=True, size=14))
        lh.addStretch()
        self.srch = _input("🔍  Search", 32)
        self.srch.setMaximumWidth(150)
        self.srch.setStyleSheet(f"""
            QLineEdit {{
                background:{CARD}; border:1.5px solid {BORDER};
                border-radius:16px; padding:0 12px; font-size:12px;
            }}
            QLineEdit:focus {{ border-color:{P_ACCENT}; }}
        """)
        self.srch.textChanged.connect(self._filter_table)
        lh.addWidget(self.srch)
        il.addLayout(lh)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Food", "kcal/100g", "Amount", "Total"])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(False)
        self.table.setMinimumHeight(150)
        self.table.setMaximumHeight(240)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        il.addWidget(self.table)

        self.trash = TrashZone()
        self.trash.delete_signal.connect(self._delete_sel)
        il.addWidget(self.trash)

        tot_row = QHBoxLayout()
        tot_row.addStretch()
        self.total_lbl = _lbl("Total : 0 kcal", bold=True, size=13, color=PRIMARY)
        tot_row.addWidget(self.total_lbl)
        il.addLayout(tot_row)

    def _update_kcal_preview(self):
        try:
            c = float(self.cal_e.text())
            a = float(self.amt_e.text())
            total = round((a / 100) * c, 1)
            self.kcal_preview.setText(f"→ {total} kcal")
            self.kcal_preview.setStyleSheet(f"color:{PRIMARY}; background:transparent; font-weight:bold; font-size:12px;")
        except ValueError:
            self.kcal_preview.setText("")

    def _refresh_comp(self):
        self._comp.setModel(QStringListModel([f.name for f in app_data.food_library.all()]))

    def _name_changed(self, t):
        s = app_data.food_library.find(t)
        if s: self.cal_e.setText(str(s.cal_per_100g))

    def _comp_pick(self, name):
        s = app_data.food_library.find(name)
        if s: self.cal_e.setText(str(s.cal_per_100g))

    def _open_lib(self):
        dlg = LibraryDialog(self)
        dlg.food_selected.connect(lambda n, c: (
            self.name_e.setText(n),
            self.cal_e.setText(str(c)),
            self.amt_e.setFocus()
        ))
        dlg.exec()
        self._refresh_comp()

    def set_meal(self, mt, ld):
        self.meal_type = mt
        self.log_date = ld
        self.title_lbl.setText(f"{MEAL_ICONS.get(mt, '🍽')}  {mt}")
        self._refresh_comp()
        self._refresh_table()

    def _add_food(self):
        n = self.name_e.text().strip()
        c = self.cal_e.text().strip()
        a = self.amt_e.text().strip()
        if not all([n, c, a]):
            self.add_err.setText("⚠  Please fill in Food Name, Kcal/100g, and Amount.")
            self.add_err.setVisible(True)
            return
        self.add_err.setVisible(False)
        cal, amt = float(c), float(a)
        if self.save_cb.isChecked():
            app_data.food_library.add(n, cal)
            self._refresh_comp()
        app_data.add_food(FoodItem(n, cal, amt, self.meal_type, self.log_date))
        self.name_e.clear()
        self.cal_e.clear()
        self.amt_e.clear()
        self.kcal_preview.setText("")
        self._refresh_table()

    def _refresh_table(self):
        log = app_data.get_log(self.log_date)
        items = log.get_meal(self.meal_type) if log else []
        self._fill(items)
        total = log.meal_calories(self.meal_type) if log else 0
        self.total_lbl.setText(f"Total : {int(total)} kcal")

    def _fill(self, items):
        self.table.setRowCount(len(items))
        for r, it in enumerate(items):
            vals = [it.name, str(int(it.cal_per_100g)), f"{int(it.amount_g)}g", f"{it.total_cal}"]
            aligns = [Qt.AlignLeft | Qt.AlignVCenter,
                      Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter]
            bg = QColor(BG2) if r % 2 == 0 else QColor(CARD)
            for col, (val, align) in enumerate(zip(vals, aligns)):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(align)
                cell.setBackground(bg)
                self.table.setItem(r, col, cell)
            self.table.item(r, 0).setData(Qt.UserRole, it.id)
        self.table.setRowHeight(0, 36) if items else None

    def _filter_table(self, t):
        log = app_data.get_log(self.log_date)
        items = log.get_meal(self.meal_type) if log else []
        if t:
            items = [i for i in items if t.lower() in i.name.lower()]
        self._fill(items)

    def _delete_sel(self):
        row = self.table.currentRow()
        if row < 0:
            return
        cell = self.table.item(row, 0)
        if cell:
            fid = cell.data(Qt.UserRole)
            if fid:
                app_data.remove_food(self.log_date, fid)
                self._refresh_table()

    def _go_back(self):
        self.mw.show_diary(self.log_date)

# ══════════════════════════════════════════════════════════════════════════════
#  WEEKLY SCREEN
# ══════════════════════════════════════════════════════════════════════════════
DAY_LABEL = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


class WeeklyChart(QWidget):
    def __init__(self):
        super().__init__()
        self.data = []
        self.target = 2000.0
        self.setMinimumHeight(200)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background:transparent;")

    def set_data(self, data, target):
        self.data = data
        self.target = target
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()

        pad_l, pad_r = 8, 8
        pad_top = 20
        pad_bot = 24
        bar_top = pad_top
        bar_bot = H - pad_bot
        bar_area = bar_bot - bar_top

        n = len(self.data)
        slot_w = (W - pad_l - pad_r) / n

        max_val = max((v for _, v, _ in self.data), default=0)
        mv = max(max_val * 1.15, self.target * 1.15, 500.0)

        ty = int(bar_bot - (self.target / mv) * bar_area)
        p.setPen(QPen(QColor(P_ACCENT), 1.2, Qt.DashLine))
        p.drawLine(int(pad_l), ty, int(W - pad_r), ty)
        p.setFont(QFont("Segoe UI", 7))
        p.setPen(QColor(P_MED))
        p.drawText(QRect(int(W - pad_r - 32), ty - 13, 32, 12), Qt.AlignRight, "target")

        bar_w = max(16, int(slot_w * 0.52))
        for i, (lbl, val, is_cheat) in enumerate(self.data):
            cx = int(pad_l + slot_w * i + slot_w / 2)
            bx = cx - bar_w // 2

            if is_cheat:
                bh = max(6, int(bar_area * 0.18))
            elif val > 0:
                bh = max(4, int((val / mv) * bar_area))
            else:
                bh = 3
            by = int(bar_bot) - bh

            if is_cheat:
                fill = QColor(ORANGE)
            elif val > self.target * 1.1:
                fill = QColor(RED)
            elif val >= self.target * 0.8:
                fill = QColor(P_MED)
            elif val > 0:
                fill = QColor(P_ACCENT)
                fill.setAlpha(160)
            else:
                fill = QColor(L_GRAY)

            p.setPen(Qt.NoPen)

            if bh > 3:
                grad = QLinearGradient(bx, by, bx, by + bh)
                c1 = QColor(fill); c2 = QColor(fill); c2.setAlpha(max(80, c2.alpha() - 60))
                grad.setColorAt(0, c1); grad.setColorAt(1, c2)
                p.setBrush(QBrush(grad))
            else:
                p.setBrush(QBrush(fill))
            path = QPainterPath()
            path.addRoundedRect(bx, by, bar_w, bh, min(3, bh // 2), min(3, bh // 2))
            p.drawPath(path)

            txt = "∞" if is_cheat else (str(int(val)) if val > 0 else "")
            if txt:
                p.setFont(QFont("Segoe UI", 7, QFont.Bold))
                p.setPen(QColor(TXT_SUB))
                label_y = max(0, by - 14)
                p.drawText(QRect(bx - 6, label_y, bar_w + 12, 13), Qt.AlignCenter, txt)

            p.setFont(QFont("Segoe UI", 9))
            p.setPen(QColor(TXT_SUB))
            p.drawText(QRect(cx - 18, int(bar_bot) + 5, 36, 16), Qt.AlignCenter, lbl)

        p.end()


class WeeklyScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.week_offset = 0
        self._week_dates = []
        self.setStyleSheet(f"background:{BG};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = GradientWidget(PRIMARY, P_MED, vertical=False)
        top.setFixedHeight(56)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(12, 0, 12, 0)
        back = QPushButton("‹")
        back.setFixedSize(38, 38)
        back.setStyleSheet(f"""
            QPushButton {{ background:rgba(255,255,255,0.20); border:none;
                border-radius:10px; font-size:20px; color:white; }}
            QPushButton:hover {{ background:rgba(255,255,255,0.35); color:white; }}
        """)
        back.clicked.connect(lambda: self.mw.show_diary())
        ttl = _lbl("Weekly Summary", bold=True, size=17, color="white")
        ttl.setAlignment(Qt.AlignCenter)
        tl.addWidget(back)
        tl.addWidget(ttl, 1)
        tl.addSpacing(46)
        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll)
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(14, 14, 14, 20)
        il.setSpacing(12)
        scroll.setWidget(inner)

        nav = QHBoxLayout()
        self.pb = QPushButton("‹ Prev")
        self.pb.setFixedHeight(32)
        self.pb.setStyleSheet(f"""
            QPushButton {{ background:{CARD}; border:1.5px solid {BORDER};
                border-radius:8px; font-size:12px; padding:0 12px; }}
            QPushButton:hover {{ background:{BG2}; border-color:{PRIMARY}; color:{PRIMARY}; }}
        """)
        self.pb.clicked.connect(self._prev)
        self.wl = _lbl("", size=12, color=TXT_SUB)
        self.wl.setAlignment(Qt.AlignCenter)
        self.nb = QPushButton("Next ›")
        self.nb.setFixedHeight(32)
        self.nb.setStyleSheet(self.pb.styleSheet())
        self.nb.clicked.connect(self._next)
        nav.addWidget(self.pb)
        nav.addWidget(self.wl, 1)
        nav.addWidget(self.nb)
        il.addLayout(nav)

        chart_card = _card()
        ccl = QVBoxLayout(chart_card)
        ccl.setContentsMargins(12, 14, 12, 12)
        ccl.setSpacing(10)

        self.chart = WeeklyChart()
        ccl.addWidget(self.chart)

        ccl.addWidget(_sep())

        cheat_hdr = QHBoxLayout()
        cheat_hdr.addWidget(_lbl("Cheat Day", bold=True, size=11, color=ORANGE))
        cheat_hdr.addWidget(_lbl("(days excluded from calorie count)", size=10, color=TXT_MUTED))
        cheat_hdr.addStretch()
        ccl.addLayout(cheat_hdr)

        self.cheat_cbs = {}
        sketch_order = [(6, "Sun"), (0, "Mon"), (1, "Tue"), (2, "Wed"),
                        (3, "Thu"), (4, "Fri"), (5, "Sat")]
        cb_row = QHBoxLayout()
        cb_row.setSpacing(0)
        for dow, name in sketch_order:
            cb = QCheckBox(name)
            cb.setFont(QFont("Segoe UI", 9))
            cb.setStyleSheet(f"""
                QCheckBox {{ color:{TXT_SUB}; background:transparent; spacing:3px; font-size:10px; }}
                QCheckBox::indicator {{ width:13px; height:13px; border-radius:3px;
                    border:1.5px solid {BORDER}; background:{CARD}; }}
                QCheckBox::indicator:checked {{ background:{ORANGE}; border-color:{ORANGE}; }}
            """)
            cb.setProperty("dow", dow)
            cb.stateChanged.connect(self._cheat_toggled)
            self.cheat_cbs[dow] = cb
            cb_row.addWidget(cb, 1)
        ccl.addLayout(cb_row)
        il.addWidget(chart_card)

        il.addWidget(_sep())

        self.total_card = _card()
        tcl = QHBoxLayout(self.total_card)
        tcl.setContentsMargins(16, 14, 16, 14)
        self.total_lbl = _lbl("Total this week", bold=True, size=14)
        self.total_val = _lbl("— kcal", bold=True, size=16, color=PRIMARY)
        self.total_val.setAlignment(Qt.AlignRight)
        tcl.addWidget(self.total_lbl)
        tcl.addStretch()
        tcl.addWidget(self.total_val)
        il.addWidget(self.total_card)

        self.tgt_card = _card()
        tgtl = QHBoxLayout(self.tgt_card)
        tgtl.setContentsMargins(16, 10, 16, 10)
        self.target_lbl = _lbl("Weekly Target", size=13, color=TXT_SUB)
        self.target_val = _lbl("—", size=13, color=TXT_MUTED)
        self.target_val.setAlignment(Qt.AlignRight)
        tgtl.addWidget(self.target_lbl)
        tgtl.addStretch()
        tgtl.addWidget(self.target_val)
        il.addWidget(self.tgt_card)

        self.st_card = _card()
        self.st_card.setFixedHeight(48)
        stl = QHBoxLayout(self.st_card)
        stl.setContentsMargins(14, 0, 14, 0)
        self.st_icon = QLabel("↓")
        self.st_icon.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.st_icon.setFixedWidth(20)
        self.st_icon.setStyleSheet(f"color:{GRAY}; background:transparent; border:none;")
        self.st_lbl = QLabel("Below target this week")
        self.st_lbl.setFont(QFont("Segoe UI", 12))
        self.st_lbl.setStyleSheet(f"color:{GRAY}; background:transparent; border:none;")
        stl.addWidget(self.st_icon)
        stl.addSpacing(8)
        stl.addWidget(self.st_lbl)
        stl.addStretch()
        il.addWidget(self.st_card)
        il.addStretch()

    def _get_week(self):
        today = date.today()
        sun = today - timedelta(days=(today.weekday() + 1) % 7) + timedelta(weeks=self.week_offset)
        return [sun + timedelta(days=i) for i in range(7)]

    def refresh(self):
        week = self._get_week()
        self._week_dates = week
        self.wl.setText(f"{week[0].strftime('%d %b')} – {week[-1].strftime('%d %b %Y')}")

        td = app_data.profile.calculate_target_kcal()
        tw = td * 7

        chart_data = []
        for i, d in enumerate(week):
            log = app_data.get_log(d)
            val = log.total_calories() if log else 0
            cheat = log.is_cheat_day if log else False
            chart_data.append((DAY_LABEL[i], val, cheat))
        self.chart.set_data(chart_data, td)

        for d in week:
            dow = d.weekday()
            if dow in self.cheat_cbs:
                cb = self.cheat_cbs[dow]
                cb.blockSignals(True)
                log = app_data.get_log(d)
                cb.setChecked(log.is_cheat_day if log else False)
                cb.blockSignals(False)

        total = app_data.weekly_total(week)
        self.total_val.setText(f"{int(total)} kcal")
        self.target_val.setText(f"{int(tw)} kcal")

        if total < tw * 0.8:
            s, c, icon = "Below target this week", GRAY, "↓"
            st_bg = O_LIGHT
        elif total <= tw * 1.1:
            s, c, icon = "On track this week!  🎯", P_MED, "✓"
            st_bg = P_LIGHT
        else:
            s, c, icon = "Exceeded weekly target", RED, "↑"
            st_bg = R_LIGHT

        self.st_lbl.setText(s)
        self.st_lbl.setStyleSheet(f"color:{c}; background:transparent; border:none; font-size:12px;")
        self.st_icon.setText(icon)
        self.st_icon.setStyleSheet(f"color:{c}; background:transparent; border:none; font-size:14px; font-weight:bold;")
        cn = self.st_card.objectName()
        self.st_card.setStyleSheet(f"""
            QFrame#{cn} {{
                background:{st_bg}; border:1.5px solid {BORDER};
                border-radius:12px;
            }}
            QFrame#{cn} QLabel {{ border:none; background:transparent; }}
        """)

    def _cheat_toggled(self):
        if not self._week_dates: return
        for d in self._week_dates:
            dow = d.weekday()
            if dow in self.cheat_cbs:
                cb = self.cheat_cbs[dow]
                log = app_data.get_or_create_log(d)
                if cb.isChecked() != log.is_cheat_day:
                    app_data.toggle_cheat_day(d)
        self.refresh()

    def _prev(self): self.week_offset -= 1; self.refresh()
    def _next(self): self.week_offset += 1; self.refresh()

# ══════════════════════════════════════════════════════════════════════════════
#  PROFILE VIEW SCREEN  (with unsaved-changes protection)
# ══════════════════════════════════════════════════════════════════════════════
class EditDialog(QDialog):
    def __init__(self, label, value, parent=None, attr=None):
        super().__init__(parent)
        self._attr = attr
        self.setWindowTitle(f"Edit {label}")
        self.setFixedWidth(320)
        self.setStyleSheet(f"background:{CARD};")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(10)
        root.addWidget(_lbl(f"Edit {label}", bold=True, size=14))
        self.edit = _input(str(value) if value else "")
        self.edit.setText(str(value) if value else "")
        root.addWidget(self.edit)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.err_lbl.setWordWrap(True)
        self.err_lbl.setVisible(False)
        root.addWidget(self.err_lbl)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._try_accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _try_accept(self):
        val = self.edit.text().strip()
        err = self._validate(val)
        if err:
            self.err_lbl.setText(f"⚠  {err}")
            self.err_lbl.setVisible(True)
        else:
            self.err_lbl.setVisible(False)
            self.accept()

    def _validate(self, val) -> str:
        attr = self._attr
        if not val:
            return ""
        if attr == "name":
            if re.search(r'[!@#$%^&*()\[\]{}<>/\\|+=~`"\'?;:,_]', val):
                return "Name must not contain special symbols (e.g. ! @ # $ % ^ & *)"
            if not re.search(r'[A-Za-zก-๙]', val):
                return "Name must contain at least one letter"
        elif attr == "age":
            try:
                v = int(val)
                if not (1 <= v <= 120):
                    return "Age must be between 1 and 120"
            except ValueError:
                return "Please enter a valid whole number"
        elif attr == "height":
            try:
                v = float(val)
                if not (50.0 <= v <= 272.0):
                    return "Height must be between 50 and 272 cm"
            except ValueError:
                return "Please enter a valid number"
        elif attr in ("weight", "target_weight"):
            try:
                v = float(val)
                if not (2.0 <= v <= 650.0):
                    return "Weight must be between 2 and 650 kg"
            except ValueError:
                return "Please enter a valid number"
        return ""

    def value(self):
        return self.edit.text().strip()


class ProfileViewScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.setStyleSheet(f"background:{BG};")

        # ── Unsaved changes tracking ──────────────────────────────────────────
        # _pending holds changes not yet saved to app_data.profile
        self._pending: dict = {}
        self._unsaved = False   # True when _pending differs from saved profile

        self._build()

    # ── Internal helpers ──────────────────────────────────────────────────────
    def _mark_changed(self):
        """Call after any edit dialog succeeds — marks unsaved state."""
        self._unsaved = True
        self._warn_banner.setVisible(True)
        self._save_ok_lbl.setVisible(False)

    def _clear_unsaved(self):
        """Call after successful save."""
        self._unsaved = False
        self._pending.clear()
        self._warn_banner.setVisible(False)

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────────
        top = GradientWidget(PRIMARY, P_MED, vertical=False)
        top.setFixedHeight(56)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(12, 0, 12, 0)
        self._back_btn = QPushButton("‹")
        self._back_btn.setFixedSize(38, 38)
        self._back_btn.setStyleSheet(f"""
            QPushButton {{ background:rgba(255,255,255,0.20); border:none;
                border-radius:10px; font-size:20px; color:white; }}
            QPushButton:hover {{ background:rgba(255,255,255,0.35); color:white; }}
        """)
        self._back_btn.clicked.connect(self._try_go_back)
        ttl = _lbl("My Profile", bold=True, size=17, color="white")
        ttl.setAlignment(Qt.AlignCenter)
        tl.addWidget(self._back_btn)
        tl.addWidget(ttl, 1)
        tl.addSpacing(46)
        root.addWidget(top)

        # ── Unsaved warning banner (hidden by default) ────────────────────────
        self._warn_banner = QFrame()
        self._warn_banner.setFixedHeight(46)
        self._warn_banner.setStyleSheet(f"""
            QFrame {{
                background: {O_LIGHT};
                border-bottom: 2px solid {ORANGE};
            }}
        """)
        wb_lay = QHBoxLayout(self._warn_banner)
        wb_lay.setContentsMargins(16, 0, 12, 0)
        wb_lay.setSpacing(8)

        warn_icon = QLabel("⚠")
        warn_icon.setFont(QFont("Segoe UI", 14))
        warn_icon.setStyleSheet(f"color:{ORANGE}; background:transparent; border:none;")
        warn_icon.setFixedWidth(22)

        warn_txt = QLabel("You have unsaved changes — press Save Profile before leaving.")
        warn_txt.setFont(QFont("Segoe UI", 11))
        warn_txt.setStyleSheet(f"color:{ORANGE}; background:transparent; border:none;")
        warn_txt.setWordWrap(False)

        wb_lay.addWidget(warn_icon)
        wb_lay.addWidget(warn_txt, 1)
        self._warn_banner.setVisible(False)
        root.addWidget(self._warn_banner)

        # ── Scrollable body ───────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll)
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(16, 16, 16, 24)
        il.setSpacing(0)
        scroll.setWidget(inner)

        # ── Hero card ─────────────────────────────────────────────────────────
        hero = GradientFrame(PRIMARY, P_MED, "#2E9E60", radius=18, vertical=False)
        hero.setStyleSheet("""
            QLabel { border: none; background: transparent; }
            QWidget { border: none; background: transparent; }
        """)
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(20, 22, 20, 22)
        hl.setSpacing(10)

        av_row = QHBoxLayout()
        av_row.setAlignment(Qt.AlignCenter)
        av = _lbl("👤", size=38)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"""
            background:rgba(255,255,255,0.20); border-radius:40px;
            border:2.5px solid rgba(255,255,255,0.45);
            min-width:80px; max-width:80px;
            min-height:80px; max-height:80px;
        """)
        av_row.addWidget(av)
        hl.addLayout(av_row)

        self.hero_name = _lbl("—", bold=True, size=18, color="white")
        self.hero_name.setAlignment(Qt.AlignCenter)
        hl.addWidget(self.hero_name)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(0)
        lbl_labels = {"wt_box": "Weight", "bmi_box": "BMI", "tw_box": "Target"}
        for attr_name in ["wt_box", "bmi_box", "tw_box"]:
            box = QWidget()
            box.setStyleSheet("background:transparent; border:none;")
            bl = QVBoxLayout(box)
            bl.setSpacing(2)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setAlignment(Qt.AlignCenter)
            v = QLabel("—")
            v.setFont(QFont("Segoe UI", 15, QFont.Bold))
            v.setAlignment(Qt.AlignCenter)
            v.setStyleSheet("color:white; background:transparent; border:none;")
            sub = QLabel(lbl_labels[attr_name])
            sub.setFont(QFont("Segoe UI", 10))
            sub.setAlignment(Qt.AlignCenter)
            sub.setStyleSheet("color:rgba(255,255,255,0.70); background:transparent; border:none;")
            bl.addWidget(v)
            bl.addWidget(sub)
            setattr(self, attr_name + "_val", v)
            stats_row.addWidget(box, 1)
            if attr_name != "tw_box":
                div = QFrame()
                div.setFrameShape(QFrame.VLine)
                div.setFixedWidth(1)
                div.setStyleSheet("background:rgba(255,255,255,0.30); border:none;")
                stats_row.addWidget(div)
        hl.addLayout(stats_row)
        il.addWidget(hero)
        il.addSpacing(16)

        # ── About Me ──────────────────────────────────────────────────────────
        il.addWidget(_lbl("About Me", bold=True, size=15))
        il.addSpacing(10)

        # Gender row
        gr = QHBoxLayout()
        gr.setContentsMargins(0, 8, 0, 8)
        gr.addWidget(_lbl("Gender", bold=True, size=13))
        gr.addStretch()
        self.gc = QComboBox()
        self.gc.addItems(["Male", "Female"])
        self.gc.setFixedWidth(130)
        self.gc.setFixedHeight(36)
        self.gc.currentTextChanged.connect(self._gender_changed)
        gr.addWidget(self.gc)
        il.addLayout(gr)
        il.addWidget(_sep())

        # Editable rows
        self.flabels = {}
        rows = [("Name", "name", ""), ("Age", "age", "yrs"),
                ("Height", "height", "cm"), ("Weight", "weight", "kg"),
                ("Target Weight", "target_weight", "kg")]
        for disp, attr, unit in rows:
            row = QHBoxLayout()
            row.setContentsMargins(0, 10, 0, 10)
            row.addWidget(_lbl(disp, bold=True, size=13))
            row.addStretch()
            vl = _lbl("—", size=13, color=TXT_SUB)
            self.flabels[attr] = (vl, unit)
            row.addWidget(vl)
            row.addSpacing(10)
            eb = QPushButton("Edit")
            eb.setFixedHeight(30)
            eb.setFixedWidth(60)
            eb.setStyleSheet(f"""
                QPushButton {{ background:{P_LIGHT}; border:none; color:{PRIMARY};
                    font-size:12px; font-weight:bold; border-radius:8px; }}
                QPushButton:hover {{ background:{BORDER}; }}
            """)
            eb.clicked.connect(lambda _, a=attr, d=disp: self._edit(a, d))
            row.addWidget(eb)
            il.addLayout(row)
            il.addWidget(_sep())

        il.addSpacing(10)
        self.bmr_lbl = _lbl("Daily Target (BMR × 1.2): — kcal", size=12, color=TXT_MUTED)
        self.bmr_lbl.setAlignment(Qt.AlignCenter)
        self.bmr_lbl.setStyleSheet(f"""
            color:{TXT_SUB}; background:{P_LIGHT};
            border-radius:10px; padding:10px;
        """)
        il.addWidget(self.bmr_lbl)
        il.addSpacing(12)

        # ── Save confirmation label ───────────────────────────────────────────
        self._save_ok_lbl = QLabel("✅  Profile saved!")
        self._save_ok_lbl.setAlignment(Qt.AlignCenter)
        self._save_ok_lbl.setStyleSheet(f"""
            color:{P_MED}; background:{P_LIGHT};
            border-radius:8px; padding:8px;
            font-weight:bold; font-size:12px;
        """)
        self._save_ok_lbl.setVisible(False)
        il.addWidget(self._save_ok_lbl)

        # ── Save Profile button ───────────────────────────────────────────────
        save_btn = _btn_primary("💾  Save Profile", h=44)
        save_btn.clicked.connect(self._save_profile)
        il.addWidget(save_btn)

        il.addStretch()

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _try_go_back(self):
        """Back button handler — block if there are unsaved changes."""
        if self._unsaved:
            # Flash the warning banner to draw attention
            self._warn_banner.setVisible(True)
            # Briefly highlight the banner with a stronger border
            self._warn_banner.setStyleSheet(f"""
                QFrame {{
                    background: #FFE0B2;
                    border-bottom: 2.5px solid {RED};
                }}
            """)
            QTimer.singleShot(600, self._reset_banner_style)
        else:
            self.mw.show_diary()

    def _reset_banner_style(self):
        self._warn_banner.setStyleSheet(f"""
            QFrame {{
                background: {O_LIGHT};
                border-bottom: 2px solid {ORANGE};
            }}
        """)

    def _gender_changed(self, t):
        """Store pending gender change — don't apply until Save."""
        self._pending["gender"] = t
        self._mark_changed()
        # Update BMR preview using pending values
        self._refresh_bmr_preview()

    def _refresh_bmr_preview(self):
        """Recompute BMR using the mix of pending + saved values for live preview."""
        p = app_data.profile
        age    = self._pending.get("age",    p.age)
        height = self._pending.get("height", p.height)
        weight = self._pending.get("weight", p.weight)
        gender = self._pending.get("gender", p.gender)
        tmp = UserProfile(age=age, height=height, weight=weight, gender=gender)
        self.bmr_lbl.setText(f"Daily Target (BMR × 1.2):  {tmp.calculate_target_kcal()} kcal")

    def _edit(self, attr, display):
        """Open edit dialog; on accept, store in _pending (not yet saved)."""
        p = app_data.profile
        # Use pending value if already modified, else use saved
        current = self._pending.get(attr, getattr(p, attr, ""))
        dlg = EditDialog(display, current, self, attr=attr)
        if dlg.exec():
            val = dlg.value()
            # Convert type
            try:
                if attr == "age":
                    val = int(val)
                elif attr in ("height", "weight", "target_weight"):
                    val = float(val)
            except ValueError:
                return
            self._pending[attr] = val
            self._mark_changed()
            # Update the display label immediately so user sees the change
            self._refresh_labels()
            self._refresh_bmr_preview()

    def _save_profile(self):
        """Apply all pending changes to app_data.profile, then clear unsaved flag."""
        p = app_data.profile
        for attr, val in self._pending.items():
            setattr(p, attr, val)
        self._clear_unsaved()
        self.refresh()
        # Show brief confirmation
        self._save_ok_lbl.setText("✅  Profile saved!")
        self._save_ok_lbl.setVisible(True)
        QTimer.singleShot(2200, lambda: self._save_ok_lbl.setVisible(False))

    def _refresh_labels(self):
        """Update the displayed field values using pending data where available."""
        p = app_data.profile
        # Hero name
        name = self._pending.get("name", p.name) or "—"
        self.hero_name.setText(name)

        # Stats boxes
        weight = self._pending.get("weight", p.weight)
        tw     = self._pending.get("target_weight", p.target_weight)
        height = self._pending.get("height", p.height)
        age_v  = self._pending.get("age", p.age)

        self.wt_box_val.setText(f"{weight} kg" if weight else "—")
        self.tw_box_val.setText(f"{tw} kg" if tw else "—")
        if height and weight:
            bmi_v = round(weight / ((height / 100) ** 2), 1)
            self.bmi_box_val.setText(str(bmi_v))
        else:
            self.bmi_box_val.setText("—")

        # Field rows
        pending_map = {
            "name":          (self._pending.get("name",          p.name), ""),
            "age":           (self._pending.get("age",           p.age), "yrs"),
            "height":        (self._pending.get("height",        p.height), "cm"),
            "weight":        (self._pending.get("weight",        p.weight), "kg"),
            "target_weight": (self._pending.get("target_weight", p.target_weight), "kg"),
        }
        for attr, (lbl_widget, unit) in self.flabels.items():
            val, u = pending_map[attr]
            if val and attr != "name":
                lbl_widget.setText(f"{val} {u}".strip())
            elif val:
                lbl_widget.setText(str(val))
            else:
                lbl_widget.setText("—")

    def refresh(self):
        """Full refresh from app_data.profile (called on screen entry & after save)."""
        # Reset pending on fresh entry
        self._pending.clear()
        self._unsaved = False
        self._warn_banner.setVisible(False)

        p = app_data.profile
        self.hero_name.setText(p.name or "—")
        self.wt_box_val.setText(f"{p.weight} kg" if p.weight else "—")
        self.tw_box_val.setText(f"{p.target_weight} kg" if p.target_weight else "—")
        bmi = p.bmi()
        self.bmi_box_val.setText(str(bmi) if bmi else "—")
        self.bmr_lbl.setText(f"Daily Target (BMR × 1.2):  {p.calculate_target_kcal()} kcal")

        self.gc.blockSignals(True)
        idx = self.gc.findText(p.gender)
        if idx >= 0: self.gc.setCurrentIndex(idx)
        self.gc.blockSignals(False)

        for attr, (lbl, unit) in self.flabels.items():
            val = getattr(p, attr, None)
            if val and attr != "name": lbl.setText(f"{val} {unit}".strip())
            elif val: lbl.setText(str(val))
            else: lbl.setText("—")

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calorie Calculator")
        self.setMinimumSize(400, 680)
        self.resize(420, 780)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.splash        = SplashScreen(self)
        self.profile_setup = ProfileScreen(self)
        self.diary         = DiaryScreen(self)
        self.meal          = MealScreen(self)
        self.weekly        = WeeklyScreen(self)
        self.profile_view  = ProfileViewScreen(self)

        for w in (self.splash, self.profile_setup, self.diary,
                  self.meal, self.weekly, self.profile_view):
            self.stack.addWidget(w)

        self.show_splash()

    def show_splash(self):        self.stack.setCurrentWidget(self.splash)
    def show_profile_setup(self): self.stack.setCurrentWidget(self.profile_setup)
    def show_diary(self, d=None): self.diary.refresh(d); self.stack.setCurrentWidget(self.diary)
    def show_meal(self, mt, ld):  self.meal.set_meal(mt, ld); self.stack.setCurrentWidget(self.meal)
    def show_weekly(self):        self.weekly.refresh(); self.stack.setCurrentWidget(self.weekly)
    def show_profile_view(self):  self.profile_view.refresh(); self.stack.setCurrentWidget(self.profile_view)

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Calorie Calculator")
    app.setFont(QFont("Segoe UI", 13))
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())