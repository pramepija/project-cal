# 📁 shared.py + main.py — อธิบายโค้ด (ใช้ร่วมกันทุกคน)

> **เจ้าของ:** ทุกคนในกลุ่ม  
> **หน้าที่:** เก็บสี, สไตล์, Data Model, ฟังก์ชันช่วย, และ AppData (รวมถึง Save/Load)

---

## 📦 shared.py

### ส่วนที่ 1 — Import (บรรทัด 1–19)

```python
import sys, uuid, re, json
```
- `sys` — ใช้สำหรับออกจากโปรแกรม  
- `uuid` — สร้าง ID ไม่ซ้ำกันให้แต่ละอาหาร  
- `re` — ใช้ตรวจสอบ regex (เช่น ชื่อ, อีเมล)  
- `json` — ใช้บันทึก/โหลดข้อมูลเป็นไฟล์ .json  

```python
from dataclasses import dataclass, field
```
- `dataclass` — สร้าง class ที่เก็บข้อมูลได้สะดวก โดยไม่ต้องเขียน `__init__` เอง  

```python
from datetime import date, timedelta
```
- `date` — วันที่  
- `timedelta` — บวก/ลบวัน (เช่น เมื่อวาน = วันนี้ - 1 วัน)  

```python
from pathlib import Path
```
- ใช้สร้าง path ไฟล์ที่บันทึกข้อมูล (calcal_data.json)

```python
from PySide6.QtWidgets import (...)
from PySide6.QtCore import Qt, Signal, ...
from PySide6.QtGui import QFont, ...
```
- Import widget ทั้งหมดจาก PySide6 (ไลบรารี UI ของ Python)  
- นำมา re-export ให้ไฟล์อื่นๆ import จาก shared ได้เลย ไม่ต้อง import ซ้ำ

---

### ส่วนที่ 2 — สีและธีม (บรรทัด 24–65)

```python
BG        = "#F4F7F4"   # สีพื้นหลังหลัก (เขียวอ่อนมาก)
BG2       = "#E8F0E8"   # สีพื้นหลังรอง
CARD      = "#FFFFFF"   # สีการ์ด (ขาว)
BORDER    = "#D4E6D4"   # สีขอบ
PRIMARY   = "#1B5E3B"   # สีหลัก (เขียวเข้ม)
P_MED     = "#2E7D52"   # สีหลักกลาง
P_LIGHT   = "#C8EDD4"   # สีหลักอ่อน
P_ACCENT  = "#43C47A"   # สีเน้น (เขียวสด)
P_GLOW    = "#A8E6C0"   # สีเรืองแสง
```
- กำหนดสีเป็น hex code เพื่อให้ใช้ซ้ำทั่วทั้งแอป ไม่ต้องจำ hex เอง

```python
RED    = "#E53935"   # สีแดง (เกินเป้า)
ORANGE = "#F57C00"   # สีส้ม (ต่ำกว่าเป้า / Cheat Day)
```

```python
MEAL_STYLE = {
    "Breakfast": (Y_LIGHT, YELLOW, "#7B5800"),
    "Lunch":     (P_LIGHT, P_ACCENT, PRIMARY),
    ...
}
```
- Dictionary เก็บสี icon, ขอบ, ตัวอักษร ของแต่ละมื้ออาหาร

```python
STATUS_COLOR = {"low": ORANGE, "balanced": P_MED, "high": RED}
STATUS_BG    = {"low": O_LIGHT, "balanced": P_LIGHT, "high": R_LIGHT}
```
- กำหนดสีสถานะแคลอรี: ต่ำ=ส้ม, สมดุล=เขียว, สูง=แดง

```python
MEALS = ["Breakfast", "Lunch", "Dinner", "Snacks"]
MEAL_ICONS = {"Breakfast": "🌅", "Lunch": "☀️", "Dinner": "🌙", "Snacks": "🍎"}
DAY_LABEL = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
```
- List/Dictionary สำเร็จรูปสำหรับมื้ออาหารและวันในสัปดาห์

---

### ส่วนที่ 3 — APP_STYLE (CSS ทั้งหมด บรรทัด 67–156)

```python
APP_STYLE = f"""
* {{ font-family: 'Segoe UI', ... }}
QWidget {{ background: transparent; ... }}
QLineEdit {{ background: {CARD}; border: 1.5px solid {BORDER}; ... }}
...
"""
```
- เป็น CSS ขนาดใหญ่ที่ใช้ตกแต่ง Widget ทุกชนิดในแอปพลิเคชัน  
- `f"""..."""` = f-string ที่แทรกตัวแปรสีเข้าไปได้

---

### ส่วนที่ 4 — ฟังก์ชันช่วย UI (บรรทัด 159–261)

```python
def _lbl(text, bold=False, size=13, color=TXT):
    l = QLabel(text)      # สร้าง Label
    f = QFont("Segoe UI", size)
    if bold: f.setBold(True)
    l.setFont(f)
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l
```
- สร้าง Label สำเร็จรูปพร้อมสไตล์ ไม่ต้องเขียนซ้ำทุกที่

```python
def _input(ph="", h=42):
    e = QLineEdit()
    e.setPlaceholderText(ph)   # ข้อความ placeholder เมื่อยังไม่พิมพ์
    e.setFixedHeight(h)
    return e
```
- สร้างช่องรับข้อมูลสำเร็จรูป

```python
def _btn_primary(text, h=42):
    ...
    b.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(...stop:0 {PRIMARY}, stop:1 {P_MED});
            color: white; border: none; ...
        }}
    """)
    return b
```
- ปุ่มหลักสีเขียว gradient

```python
def _card(radius=12):
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame#{name} {{ background: {CARD}; border: 1.5px solid {BORDER}; ... }}
    """)
    return f
```
- สร้าง Card (กล่องขาวมีขอบ) สำหรับใส่เนื้อหา

---

### ส่วนที่ 5 — Data Models (บรรทัด 266–356)

#### `UserProfile` — ข้อมูลผู้ใช้

```python
@dataclass
class UserProfile:
    name: str = ""
    gmail: str = ""
    age: int = 0
    height: float = 0.0
    weight: float = 0.0
    gender: str = "Male"
    target_weight: float = 0.0
```
- เก็บข้อมูลโปรไฟล์ผู้ใช้ทั้งหมด

```python
def calculate_bmr(self) -> float:
    b = 10 * self.weight + 6.25 * self.height - 5 * self.age
    return round(b + 5 if self.gender == "Male" else b - 161, 1)
```
- คำนวณ BMR (Basal Metabolic Rate) ด้วยสูตร Mifflin-St Jeor  
- ผู้ชาย: BMR = 10W + 6.25H - 5A + 5  
- ผู้หญิง: BMR = 10W + 6.25H - 5A - 161

```python
def calculate_target_kcal(self) -> float:
    return round(self.calculate_bmr() * 1.2, 1)
```
- เป้าหมายแคลอรีต่อวัน = BMR × 1.2 (activity factor เบาๆ)

```python
def is_complete(self) -> bool:
    return bool(self.name and self.age > 0 and self.height > 0 and self.weight > 0)
```
- ตรวจว่ากรอกข้อมูลครบหรือยัง (ใช้ใน Splash Screen)

```python
def bmi(self):
    return round(self.weight / ((self.height / 100) ** 2), 1)
```
- คำนวณ BMI = น้ำหนัก(kg) / ส่วนสูง(m)²

---

#### `FoodItem` — รายการอาหาร 1 รายการ

```python
@dataclass
class FoodItem:
    id: str; name: str; cal_per_100g: float
    amount_g: float; meal_type: str; date: date
```

```python
def __init__(self, name, cal_per_100g, amount_g, meal_type, entry_date=None):
    self.id = str(uuid.uuid4())[:8]   # สร้าง ID สุ่ม 8 ตัว
    self.name = name
    self.cal_per_100g = cal_per_100g
    self.amount_g = amount_g
    self.meal_type = meal_type
    self.date = entry_date or date.today()
```

```python
@property
def total_cal(self) -> float:
    return round((self.amount_g / 100) * self.cal_per_100g, 1)
```
- แคลอรีรวม = (ปริมาณ / 100) × แคลอรีต่อ 100g

---

#### `DailyLog` — บันทึกอาหารรายวัน

```python
@dataclass
class DailyLog:
    log_date: date
    food_items: List[FoodItem] = field(default_factory=list)
    is_cheat_day: bool = False
```

```python
def add_food(self, item): self.food_items.append(item)
def remove_food(self, fid): self.food_items = [f for f in self.food_items if f.id != fid]
def get_meal(self, mt): return [f for f in self.food_items if f.meal_type == mt]
def total_calories(self): return round(sum(f.total_cal for f in self.food_items), 1)
def meal_calories(self, mt): return round(sum(f.total_cal for f in self.get_meal(mt)), 1)
```
- ฟังก์ชันจัดการอาหารในแต่ละวัน

---

#### `FoodLibrary` — คลังอาหารที่บันทึกไว้

```python
class FoodLibrary:
    def add(self, name, cal):
        ex = self.find(name)
        if ex: ex.cal_per_100g = cal   # ถ้ามีอยู่แล้ว อัปเดตแคลอรี
        else: self._foods.append(SavedFood(name, cal))   # ถ้าใหม่ เพิ่มเข้า list
    
    def remove(self, name): ...        # ลบตามชื่อ
    def find(self, name): ...          # ค้นหาตรงๆ
    def search(self, q): ...           # ค้นหาแบบ contains
    def all(self): ...                 # ดึงทั้งหมด
```

---

#### `AppData` — ตัวกลางจัดการข้อมูลทั้งหมด

```python
class AppData:
    def __init__(self):
        self.profile = UserProfile()
        self.daily_logs: Dict[date, DailyLog] = {}
        self.food_library = FoodLibrary()
```
- เก็บ profile, บันทึกรายวัน, และคลังอาหาร ไว้ที่เดียว

```python
def get_or_create_log(self, d):
    if d not in self.daily_logs:
        self.daily_logs[d] = DailyLog(d)
    return self.daily_logs[d]
```
- ถ้ายังไม่มี log วันนั้น ให้สร้างใหม่อัตโนมัติ

```python
def toggle_cheat_day(self, d):
    log = self.get_or_create_log(d)
    log.is_cheat_day = not log.is_cheat_day
```
- สลับ on/off Cheat Day

```python
def weekly_total(self, week):
    return round(sum(
        self.get_log(d).total_calories()
        for d in week
        if self.get_log(d) and not self.get_log(d).is_cheat_day
    ), 1)
```
- รวมแคลอรีทั้งสัปดาห์ **โดยข้ามวัน Cheat Day**

```python
def get_status(self, d):
    if consumed < target * 0.8: return "low"
    if consumed <= target * 1.1: return "balanced"
    return "high"
```
- low: กินน้อยกว่า 80% ของเป้า  
- balanced: กิน 80–110% ของเป้า  
- high: กินมากกว่า 110% ของเป้า

---

### ส่วนที่ 6 — Save / Load (บรรทัด 400–484)

```python
_SAVE_FILE = Path(__file__).parent / "calcal_data.json"
```
- บันทึกไฟล์ไว้ในโฟลเดอร์เดียวกับโปรแกรม

```python
def save(self):
    data = {
        "profile": {...},
        "food_library": [...],
        "daily_logs": [...]
    }
    with open(self._SAVE_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
```
- แปลงข้อมูลทั้งหมดเป็น JSON แล้วเขียนลงไฟล์

```python
def load(self):
    with open(self._SAVE_FILE, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    # แปลง JSON กลับเป็น objects
    self.profile = UserProfile(...)
    self.food_library = FoodLibrary()
    ...
```
- อ่านไฟล์ JSON และแปลงกลับเป็น object ในโปรแกรม

```python
app_data = AppData()
app_data.load()   # โหลดข้อมูลทันทีเมื่อเริ่มโปรแกรม
```

---

### ส่วนที่ 7 — Shared Widgets (บรรทัด 489–611)

#### `GradientWidget` และ `GradientFrame`
```python
class GradientWidget(QWidget):
    def paintEvent(self, event):
        grad = QLinearGradient(0, 0, 0, self.height())  # gradient แนวตั้ง
        grad.setColorAt(0.0, self._c1)
        grad.setColorAt(1.0, self._c2)
        p.fillRect(self.rect(), QBrush(grad))
```
- Widget ที่วาด gradient สีเอง ใช้เป็น header bar

#### `PersonIconButton`
```python
class PersonIconButton(QWidget):
    clicked_signal = Signal()
    def paintEvent(self, event):
        # วาดวงกลม + หัว + ลำตัว ด้วย QPainter (ไม่ใช้รูปภาพ)
```
- ปุ่มไอคอนคนวาดด้วยโค้ด ใช้ใน header ของ Home Screen

---

## 📦 main.py

### `MainWindow` — หน้าต่างหลัก

```python
class MainWindow(QMainWindow):
    def __init__(self):
        self.setWindowTitle("Calorie Calculator")
        self.setMinimumSize(400, 680)
        self.resize(420, 780)
        self.stack = QStackedWidget()   # Widget ที่สลับหน้าจอได้
        self.setCentralWidget(self.stack)
```
- `QStackedWidget` = กองหน้าจอ แสดงได้ทีละ 1 หน้า

```python
        self.splash        = SplashScreen(self)
        self.profile_setup = ProfileScreen(self)
        self.diary         = DiaryScreen(self)
        self.meal          = MealScreen(self)
        self.weekly        = WeeklyScreen(self)
        self.profile_view  = ProfileViewScreen(self)
```
- สร้างหน้าจอทั้ง 6 หน้า (แต่ละหน้ารับ `mw=self` เพื่อเรียก navigate)

```python
        for w in (...all screens...):
            self.stack.addWidget(w)    # เพิ่มทุกหน้าเข้า stack

        self.show_splash()             # เริ่มที่ Splash Screen
```

```python
    def closeEvent(self, event):
        app_data.save()   # บันทึกข้อมูลทุกครั้งที่ปิดโปรแกรม
        event.accept()
```

```python
    def show_splash(self):        self.stack.setCurrentWidget(self.splash)
    def show_profile_setup(self): self.stack.setCurrentWidget(self.profile_setup)
    def show_diary(self, d=None): app_data.save(); self.diary.refresh(d); ...
    def show_meal(self, mt, ld):  self.meal.set_meal(mt, ld); ...
    def show_weekly(self):        self.weekly.refresh(); ...
    def show_profile_view(self):  self.profile_view.refresh(); ...
```
- ฟังก์ชัน navigate แต่ละหน้า เรียกจาก screen ไหนก็ได้ผ่าน `self.mw`

### Entry Point

```python
if __name__ == "__main__":
    app = QApplication(sys.argv)       # สร้าง application
    app.setApplicationName("Calorie Calculator")
    app.setFont(QFont("Segoe UI", 13)) # ตั้ง font เริ่มต้น
    app.setStyleSheet(APP_STYLE)       # ใส่ CSS ทั้งหมด
    window = MainWindow()
    window.show()
    sys.exit(app.exec())               # รัน event loop
```
- `if __name__ == "__main__"` = รันเฉพาะเมื่อรันไฟล์นี้โดยตรง (ไม่ใช่เมื่อ import)

---

## 🗺️ แผนผังการทำงาน

```
main.py เริ่มรัน
    └── สร้าง MainWindow
            └── สร้างหน้าจอทั้ง 6
            └── แสดง SplashScreen
                    ├── มีโปรไฟล์แล้ว → show_diary()
                    └── ยังไม่มี → show_profile_setup()
```
