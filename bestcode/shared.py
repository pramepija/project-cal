import sys, uuid, re, json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional
from pathlib import Path

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

MEALS = ["Breakfast", "Lunch", "Dinner", "Snacks"]
MEAL_ICONS = {"Breakfast": "🌅", "Lunch": "☀️", "Dinner": "🌙", "Snacks": "🍎"}
DAY_LABEL = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

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

# ── UI Helper Functions ───────────────────────────────────────────────────────
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
#  DATA MODELS  (OOP)
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class UserProfile:
    name: str = ""; gmail: str = ""; age: int = 0
    height: float = 0.0; weight: float = 0.0
    gender: str = "Male"; target_weight: float = 0.0
    avatar_path: str = ""   # path to profile picture

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
    amount_g: float; meal_type: str; date: date # type: ignore

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

    # ── Persistence ─────────────────────────────────────────────────────────
    _SAVE_FILE = Path(__file__).parent / "calcal_data.json"

    def save(self):
        """Save all app data to a JSON file in the user's home directory."""
        try:
            data = {
                "profile": {
                    "name":          self.profile.name,
                    "gmail":         self.profile.gmail,
                    "age":           self.profile.age,
                    "height":        self.profile.height,
                    "weight":        self.profile.weight,
                    "gender":        self.profile.gender,
                    "target_weight": self.profile.target_weight,
                    "avatar_path":   self.profile.avatar_path,
                },
                "food_library": [
                    {"name": f.name, "cal_per_100g": f.cal_per_100g}
                    for f in self.food_library.all()
                ],
                "daily_logs": [
                    {
                        "log_date":     log.log_date.isoformat(),
                        "is_cheat_day": log.is_cheat_day,
                        "food_items": [
                            {
                                "id":           fi.id,
                                "name":         fi.name,
                                "cal_per_100g": fi.cal_per_100g,
                                "amount_g":     fi.amount_g,
                                "meal_type":    fi.meal_type,
                                "date":         fi.date.isoformat(),
                            }
                            for fi in log.food_items
                        ],
                    }
                    for log in self.daily_logs.values()
                ],
            }
            with open(self._SAVE_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CalCal] Save failed: {e}")

    def load(self):
        """Load app data from JSON file if it exists."""
        if not self._SAVE_FILE.exists():
            return
        try:
            with open(self._SAVE_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            p = data.get("profile", {})
            self.profile = UserProfile(
                name=p.get("name", ""),
                gmail=p.get("gmail", ""),
                age=p.get("age", 0),
                height=p.get("height", 0.0),
                weight=p.get("weight", 0.0),
                gender=p.get("gender", "Male"),
                target_weight=p.get("target_weight", 0.0),
                avatar_path=p.get("avatar_path", ""),
            )
            self.food_library = FoodLibrary()
            for item in data.get("food_library", []):
                self.food_library.add(item["name"], item["cal_per_100g"])
            self.daily_logs = {}
            for log_data in data.get("daily_logs", []):
                d = date.fromisoformat(log_data["log_date"])
                log = DailyLog(log_date=d, is_cheat_day=log_data.get("is_cheat_day", False))
                for fi_data in log_data.get("food_items", []):
                    fi = FoodItem(
                        name=fi_data["name"],
                        cal_per_100g=fi_data["cal_per_100g"],
                        amount_g=fi_data["amount_g"],
                        meal_type=fi_data["meal_type"],
                        entry_date=date.fromisoformat(fi_data["date"]),
                    )
                    fi.id = fi_data["id"]
                    log.food_items.append(fi)
                self.daily_logs[d] = log
        except Exception as e:
            print(f"[CalCal] Load failed (starting fresh): {e}")


# Global shared app data instance — load saved data immediately
app_data = AppData()
app_data.load()

# ══════════════════════════════════════════════════════════════════════════════
#  SHARED WIDGETS
# ══════════════════════════════════════════════════════════════════════════════
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

        # ── ถ้ามีรูปโปรไฟล์ ให้แสดงรูปในวงกลม ──────────────────────────────
        avatar_path = getattr(app_data.profile, "avatar_path", "")
        if avatar_path:
            from pathlib import Path as _Path
            if _Path(avatar_path).exists():
                # วาด clip วงกลม
                clip = QPainterPath()
                clip.addEllipse(1, 1, W - 2, H - 2)
                p.setClipPath(clip)

                px = QPixmap(avatar_path).scaled(
                    W, H,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )
                sx = (px.width()  - W) // 2
                sy = (px.height() - H) // 2
                p.drawPixmap(
                    QRect(0, 0, W, H),
                    px,
                    QRect(max(0, sx), max(0, sy), min(W, px.width()), min(H, px.height())),
                )

                # Hover overlay
                if self._hover:
                    p.fillRect(0, 0, W, H, QColor(0, 0, 0, 80))

                # Border ring
                p.setClipping(False)
                p.setPen(QPen(self._border, 2))
                p.setBrush(Qt.NoBrush)
                p.drawEllipse(1, 1, W - 2, H - 2)
                p.end()
                return   # ← วาดเสร็จแล้ว ไม่ต้องวาด icon คน

        # ── ไม่มีรูป → วาด default person icon เดิม ──────────────────────────
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