# 🌿 panhathai.py — อธิบายโค้ดทีละบรรทัด

> **เจ้าของ:** พัณห์หทัย  
> **ไฟล์:** `panhathai.py`  
> **หน้าที่:** Splash Screen (หน้าเปิดแอป) + Food Library Dialog (คลังอาหาร)

---

## ฟังก์ชันที่รับผิดชอบ (5 FN)

| # | ฟังก์ชัน | อยู่ที่ไหน |
|---|----------|-----------|
| 1 | Profile check → route to Home or ProfileSetup | `SplashScreen._start()` |
| 2 | Flowchart (แสดงขั้นตอนแอป) | `SplashScreen._build()` — pills row |
| 3 | Search saved foods | `LibraryDialog._filter()` |
| 4 | Select food → auto-fill form | `LibraryDialog._pick()` |
| 5 | Delete saved food | `LibraryDialog._delete()` |

---

## 📌 IMPORT (บรรทัด 1–17)

```python
import os
```
- ใช้ตรวจหา path ของไฟล์รูปโลโก้

```python
from shared import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog,
    Qt, QFont, QColor, QPainter, QBrush, QLinearGradient,
    QPainterPath, QPixmap,
    PRIMARY, P_MED, P_LIGHT, P_ACCENT,
    TXT, TXT_MUTED, CARD, BG, RED, R_LIGHT, BORDER,
    _lbl, _input, _btn_primary, _btn_outline, _btn_danger,
    app_data,
)
```
- Import ทุกอย่างจาก shared.py ไม่ต้อง import PySide6 เอง

---

## 🖼️ class SplashScreen

> หน้าจอแรกของแอป — แสดงโลโก้, ชื่อ, ปุ่ม Get Started

### `__init__` (บรรทัด 23–26)

```python
def __init__(self, mw):
    super().__init__()      # เรียก __init__ ของ QWidget
    self.mw = mw            # เก็บ reference ถึง MainWindow ไว้ใช้ navigate
    self._build()           # สร้าง UI
```

---

### `paintEvent` — วาดพื้นหลัง Gradient (บรรทัด 28–38)

```python
def paintEvent(self, event):
    p = QPainter(self)
    p.setRenderHint(QPainter.Antialiasing)   # เปิด anti-aliasing (ขอบเรียบขึ้น)
```

```python
    grad = QLinearGradient(0, 0, 0, self.height())   # gradient แนวตั้ง
    grad.setColorAt(0.0, QColor("#2E7D52"))    # บน — เขียวกลาง
    grad.setColorAt(0.5, QColor("#3D9960"))    # กลาง — เขียวสด
    grad.setColorAt(1.0, QColor("#1B5E3B"))    # ล่าง — เขียวเข้ม
    p.fillRect(self.rect(), QBrush(grad))      # ทาสี gradient ทั้ง widget
```

```python
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(255, 255, 255, 18))      # ขาวโปร่งแสง opacity 18/255
    p.drawEllipse(-60, -60, 220, 220)          # วงกลมตกแต่งมุมบนซ้าย
    p.setBrush(QColor(255, 255, 255, 12))
    p.drawEllipse(...)                         # วงกลมตกแต่งมุมล่างขวา
```
- วาดวงกลมขาวโปร่งแสงเพื่อตกแต่งพื้นหลัง

---

### `_build` — สร้าง UI ทั้งหมด (บรรทัด 40–)

#### Layout หลัก

```python
root = QVBoxLayout(self)         # จัดเรียงแนวตั้ง
root.setAlignment(Qt.AlignCenter)  # จัดกึ่งกลาง
root.setSpacing(0)
root.setContentsMargins(36, 0, 36, 50)  # ขอบซ้าย 36, ล่าง 50
```

#### Badge "CALORIE CALCULATOR"

```python
badge = QLabel("CALORIE CALCULATOR")
badge.setAlignment(Qt.AlignCenter)
badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
badge.setStyleSheet("""
    color: rgba(255,255,255,0.90);         # ตัวอักษรขาวใส 90%
    background: rgba(255,255,255,0.15);    # พื้นหลังขาวโปร่ง 15%
    border: 1px solid rgba(255,255,255,0.30);
    border-radius: 12px;
    padding: 4px 16px;
    letter-spacing: 1.5px;                 # เว้นระยะตัวอักษร
""")
```

#### LogoWidget — แสดงรูปโลโก้

```python
class LogoWidget(QWidget):
    def __init__(self, path, size=140, corner_radius=28):
        super().__init__()
        self.setFixedSize(size, size)    # ขนาด 140×140
        self._radius = corner_radius
        raw = QPixmap(path)              # โหลดรูปภาพ
        self._pm = raw.scaled(size, size,
                              Qt.KeepAspectRatio,
                              Qt.SmoothTransformation)  # ย่อขยายแบบ smooth
```

```python
    def paintEvent(self, e):
        clip = QPainterPath()
        clip.addRoundedRect(0, 0, self.width(), self.height(),
                            self._radius, self._radius)  # สร้าง mask มุมโค้ง
        p.setClipPath(clip)     # ตัดรูปตาม mask
        p.drawPixmap(x, y, self._pm)  # วาดรูป
```
- แสดงรูปโลโก้มุมโค้ง โดยวาดเองแทนการใช้ border-radius CSS

```python
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_logo_clean.png")
if not os.path.exists(logo_path):
    logo_path = ... "app_logo.png"   # fallback ถ้าไม่มีไฟล์แรก
pm_test = QPixmap(logo_path)
if not pm_test.isNull():
    logo_widget = LogoWidget(logo_path, 148)   # มีรูป → ใช้รูป
else:
    logo_widget = QLabel("🥗")                  # ไม่มีรูป → ใช้ emoji แทน
```

#### Title และ Subtitle

```python
title = QLabel("Reduce your calories")
title.setFont(QFont("Segoe UI", 26, QFont.Bold))
title.setStyleSheet("color: white; background: transparent;")

sub = QLabel("Track your nutrition. Reach your goals.")
sub.setFont(QFont("Segoe UI", 12))
sub.setStyleSheet("color: rgba(255,255,255,0.72); ...")  # ขาว 72% ทึบ
```

#### [FN] Flowchart — Pills Row (3 ปุ่มขั้นตอน)

```python
for emoji, label in [("📋", "Log meals"), ("🎯", "Set goals"), ("📊", "Weekly")]:
    pill = QWidget()
    pill.setStyleSheet("""
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 18px;
    """)
    pl = QHBoxLayout(pill)    # Layout ภายใน pill
    # เพิ่ม emoji + label เข้าไป
    pills_row.addWidget(pill)
```
- สร้าง 3 ปุ่มกลมแสดงขั้นตอนการใช้แอป เป็น Flowchart อย่างง่าย

#### ปุ่ม Get Started

```python
btn = QPushButton("  Get Started  →")
btn.setFixedHeight(50)
btn.setFixedWidth(230)
btn.setCursor(Qt.PointingHandCursor)  # เปลี่ยน cursor เป็น pointer
btn.setStyleSheet(f"""
    QPushButton {{
        background: white;
        color: {PRIMARY};           # ตัวอักษรสีเขียว
        border-radius: 25px;        # มุมโค้ง
    }}
    QPushButton:hover  {{ background: #E8F5EE; }}   # hover สีเขียวอ่อน
    QPushButton:pressed {{ background: #C8E6D0; }}  # กดสีเขียวกว่า
""")
btn.clicked.connect(self._start)    # เชื่อมกับฟังก์ชัน _start
```

---

### `_start` — [FN] Profile check (บรรทัด ~120)

```python
def _start(self):
    # [FN] Profile check → route to Home or ProfileSetup
    if app_data.profile.is_complete():
        self.mw.show_diary()        # มีโปรไฟล์แล้ว → ไปหน้า Home
    else:
        self.mw.show_profile_setup()  # ยังไม่มี → ไปกรอกโปรไฟล์
```
- `is_complete()` ตรวจว่ามีชื่อ + อายุ + ส่วนสูง + น้ำหนัก ครบหรือเปล่า

---

## 📚 class LibraryDialog

> Dialog แสดงรายการอาหารที่บันทึกไว้

### `__init__` (บรรทัด ~130–175)

```python
class LibraryDialog(QDialog):
    food_selected = Signal(str, float)   # Signal ส่ง (ชื่ออาหาร, แคลอรี/100g)
```
- `Signal` = ช่องทางส่งข้อมูลจาก dialog ไปยังหน้าจออื่น

```python
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Food Library")
        self.setMinimumSize(400, 460)
```

```python
        # ช่องค้นหา — [FN] Search saved foods
        self.srch = _input("🔍  Search foods...", 38)
        self.srch.textChanged.connect(self._filter)   # ทุกครั้งที่พิมพ์ → _filter
```

```python
        # List รายการอาหาร
        self.lw = QListWidget()
        self.lw.itemDoubleClicked.connect(self._pick)   # double click → _pick
```

```python
        # ปุ่ม Delete
        db = _btn_danger("🗑  Delete selected")
        db.clicked.connect(self._delete)
```

---

### `_populate` — เติมข้อมูลลง List (บรรทัด ~177–192)

```python
def _populate(self, q=""):
    self.lw.clear()   # ล้าง list ก่อน
    foods = app_data.food_library.search(q) if q else app_data.food_library.all()
    # ถ้ามี keyword ให้ค้นหา, ถ้าไม่มีให้แสดงทั้งหมด
    
    for f in foods:
        it = QListWidgetItem(f"  {f.name}  ·  {f.cal_per_100g} kcal/100g")
        it.setData(Qt.UserRole, (f.name, f.cal_per_100g))  # เก็บข้อมูลซ่อนไว้กับ item
        self.lw.addItem(it)
    
    if not foods:
        ph = QListWidgetItem("  (No saved foods yet)")
        ph.setFlags(Qt.NoItemFlags)   # ทำให้ item นี้ click ไม่ได้
```
- `Qt.UserRole` = slot พิเศษใน QListWidgetItem สำหรับเก็บข้อมูลที่ผู้ใช้กำหนดเอง

---

### `_filter` — [FN] Search saved foods (บรรทัด ~194)

```python
def _filter(self, t):
    self._populate(t)   # เรียก _populate ด้วย keyword ที่พิมพ์
```
- ทุกครั้งที่พิมพ์ในช่องค้นหา → เติมข้อมูลใหม่ตาม keyword

---

### `_pick` — [FN] Select food → auto-fill form (บรรทัด ~196–200)

```python
def _pick(self, it):
    # [FN] Select food → auto-fill form
    d = it.data(Qt.UserRole)          # ดึง (ชื่อ, แคลอรี) ที่เก็บไว้
    if d:
        self.food_selected.emit(d[0], d[1])   # ส่ง Signal ออกไป
        self.accept()                           # ปิด dialog
```
- เมื่อ double-click อาหาร → ส่ง Signal ไปให้ MealScreen กรอกฟอร์มอัตโนมัติ

---

### `_delete` — [FN] Delete saved food (บรรทัด ~202–207)

```python
def _delete(self):
    # [FN] Delete saved food
    it = self.lw.currentItem()    # ดึง item ที่เลือกอยู่
    if it:
        d = it.data(Qt.UserRole)
        if d:
            app_data.food_library.remove(d[0])    # ลบออกจากคลัง
            self._populate(self.srch.text())       # refresh list
```

---

## 🗺️ แผนผังการทำงาน

```
SplashScreen
│
├── แสดง UI (gradient bg, logo, pills, button)
│
└── กด "Get Started"
        ├── มีโปรไฟล์ → show_diary()   [DiaryScreen]
        └── ไม่มีโปรไฟล์ → show_profile_setup()   [ProfileScreen]

LibraryDialog (เปิดจาก MealScreen)
│
├── แสดงรายการอาหารทั้งหมด
├── พิมพ์ค้นหา → filter
├── double-click อาหาร → ส่ง Signal กลับ MealScreen (auto-fill)
└── เลือก + กด Delete → ลบออกจากคลัง
```
