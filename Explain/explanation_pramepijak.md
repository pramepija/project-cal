# 📅 pramepijak.py — อธิบายโค้ดทีละบรรทัด

> **เจ้าของ:** ปราเมปิจาก  
> **ไฟล์:** `pramepijak.py`  
> **หน้าที่:** DiaryScreen (Home) — หน้าหลักแสดงสรุปแคลอรีรายวัน

---

## ฟังก์ชันที่รับผิดชอบ (6 FN)

| # | ฟังก์ชัน | อยู่ที่ไหน |
|---|----------|-----------|
| 1 | Calorie status (Low / Balanced / High) | `refresh()` → status_badge |
| 2 | Cheat day toggle | `_toggle_cheat()` + `refresh()` |
| 3 | Progress bar | `refresh()` → self.progress |
| 4 | Weekly total preview | `refresh()` → weekly_val |
| 5 | BMR / target kcal calculation | `refresh()` → `app_data.profile.calculate_target_kcal()` |
| 6 | Save profile | ผ่าน PersonIconButton → show_profile_view |

---

## 📌 IMPORT (บรรทัด 1–32)

```python
from datetime import date, timedelta
```
- `date` = วันที่ปัจจุบัน  
- `timedelta` = บวก/ลบวัน (เช่น เมื่อวาน = today - timedelta(days=1))

```python
from phumin import CalorieMeter   # ใช้ widget ของ Phumin
```
- import CalorieMeter ข้ามไฟล์

---

## 🖼️ class DiaryScreen

### `__init__` (บรรทัด 36–42)

```python
def __init__(self, mw):
    super().__init__()
    self.mw = mw
    self.current_date = date.today()   # วันที่แสดงอยู่ตอนนี้ (เริ่มที่วันนี้)
    self.setStyleSheet(f"background:{BG};")
    self._build()
```

---

### `_build` — สร้าง UI ทั้งหมด (บรรทัด 44–)

#### Top Bar

```python
top = GradientWidget(PRIMARY, P_MED, vertical=False)
top.setFixedHeight(60)
tl = QHBoxLayout(top)
tl.setContentsMargins(16, 0, 16, 0)

diary_lbl = QLabel("My Diary")
diary_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
diary_lbl.setStyleSheet("color:white; background:transparent;")
```

```python
prof_btn = PersonIconButton(PRIMARY, P_LIGHT, P_ACCENT)
prof_btn.clicked_signal.connect(self.mw.show_profile_view)  # กดปุ่มคน → ไปหน้าโปรไฟล์
self.prof_btn = prof_btn
```

#### ScrollArea

```python
scroll = QScrollArea()
scroll.setWidgetResizable(True)
inner = QWidget()
il = QVBoxLayout(inner)
il.setContentsMargins(16, 16, 16, 20)
il.setSpacing(14)
scroll.setWidget(inner)
```
- ทุกเนื้อหาอยู่ใน scroll area เพราะอาจยาวเกินหน้าจอ

---

#### Date Navigation

```python
dn = QHBoxLayout()

self.prev_btn = QPushButton("‹")
self.prev_btn.setFixedSize(36, 36)
self.prev_btn.setStyleSheet(f"""
    QPushButton {{
        background:{P_LIGHT}; border:none;
        border-radius:18px; font-size:20px;  # วงกลม
        color:{PRIMARY}; font-weight:bold;
    }}
    QPushButton:hover {{ background:{P_ACCENT}; color:white; }}
    QPushButton:pressed {{ background:{PRIMARY}; color:white; }}
""")
self.prev_btn.clicked.connect(self._prev)   # คลิก → วันก่อนหน้า

self.date_lbl = _lbl("", bold=True, size=15)
self.date_lbl.setAlignment(Qt.AlignCenter)

self.next_btn = QPushButton("›")
self.next_btn.clicked.connect(self._next)   # คลิก → วันถัดไป
```

---

#### Summary Card (กล่องสรุป)

```python
self.sum_card = GradientFrame("#EDF9F2", "#FFFFFF", radius=18,
                               vertical=True, border_color=BORDER)
scl = QVBoxLayout(self.sum_card)
```

##### [FN] Calorie status badge

```python
self.status_badge = QLabel("↓ Low")
self.status_badge.setFixedHeight(26)
self.status_badge.setStyleSheet(f"""
    color:{ORANGE}; background:{O_LIGHT};
    border-radius:13px; padding:0 10px;  # pill shape
    font-size:11px; font-weight:bold;
""")
```
- เริ่มต้นแสดง "↓ Low" สีส้ม (จะถูก refresh() อัปเดต)

##### [FN] Cheat day toggle

```python
self.cheat_cb = QCheckBox("Cheat Day 🎉")
self.cheat_cb.setStyleSheet(f"""
    QCheckBox {{ color:{ORANGE}; font-weight:bold; ... }}
    QCheckBox::indicator:checked {{ background:{ORANGE}; border-color:{ORANGE}; }}
""")
self.cheat_cb.stateChanged.connect(self._toggle_cheat)   # เปลี่ยน state → toggle
```

##### CalorieMeter (จาก phumin.py)

```python
self.meter = CalorieMeter()   # วงกลมแสดงแคลอรีที่เหลือ
mid.addWidget(self.meter)
```

##### Stats Column (ด้านขวาของ meter)

```python
self.food_lbl = _lbl("Eaten  0 kcal", size=12, color=TXT)
self.goal_lbl = _lbl("Target  0 kcal", size=12, color=TXT_MUTED)
```

##### [FN] Progress bar

```python
pb_row = QHBoxLayout()
self.progress = QProgressBar()
self.progress.setFixedHeight(7)      # บาง 7px
self.progress.setRange(0, 100)       # 0-100%
self.progress.setValue(0)
self.progress.setTextVisible(False)  # ซ่อนตัวเลข %
self.prog_lbl = _lbl("0%", size=10, color=TXT_MUTED)
self.prog_lbl.setFixedWidth(36)
pb_row.addWidget(self.progress, 1)   # ขยายเต็ม
pb_row.addWidget(self.prog_lbl)
```

---

#### Meal Buttons (4 มื้อ)

```python
self.meal_cal_lbl = {}   # dict เก็บ label แคลอรีของแต่ละมื้อ

for m in MEALS:   # ["Breakfast", "Lunch", "Dinner", "Snacks"]
    icon_bg, border_col, txt_col = MEAL_STYLE.get(m, (P_LIGHT, P_ACCENT, PRIMARY))
    
    card = QPushButton()        # ใช้ QPushButton เป็นการ์ดที่กดได้
    card.setFixedHeight(58)
    card.setObjectName(f"mealCard_{m}")    # ชื่อ unique สำหรับ CSS
    card.setStyleSheet(f"""
        QPushButton[objectName="mealCard_{m}"] {{
            background:{CARD}; border:1px solid {BORDER};
            border-radius:14px; text-align:left;
        }}
        QPushButton[objectName="mealCard_{m}"]:hover {{
            border-color:{P_ACCENT}; background:{BG};
        }}
    """)
    card.clicked.connect(lambda _, mt=m: self.mw.show_meal(mt, self.current_date))
    # lambda _, mt=m: ← ใช้ default argument เพื่อ capture ค่า m ถูกต้อง
```

```python
    cl = QHBoxLayout(card)
    cl.setContentsMargins(12, 0, 12, 0)
    
    # Icon bubble
    icon_bubble = QWidget()
    icon_bubble.setFixedSize(42, 42)
    icon_bubble.setStyleSheet(f"background:{icon_bg}; border-radius:12px; border:none;")
    icon_lbl = QLabel(MEAL_ICONS.get(m, "🍽"))
    icon_lbl.setFont(QFont("Segoe UI", 17))
    
    # ชื่อมื้อ
    name_lbl = QLabel(m)
    name_lbl.setFixedWidth(88)
    
    # แคลอรีของมื้อนี้
    cal_lbl = QLabel("0 kcal")
    self.meal_cal_lbl[m] = cal_lbl   # เก็บ reference ไว้ update ภายหลัง
    
    # ลูกศร ›
    arrow_circle = QLabel("›")
    arrow_circle.setFixedSize(32, 32)
    arrow_circle.setAlignment(Qt.AlignCenter)
    arrow_circle.setStyleSheet(f"""
        color:{PRIMARY}; background:{P_LIGHT};
        border-radius:16px; border:none;
    """)
```

---

#### [FN] Weekly total preview — ปุ่มไปหน้า Weekly

```python
wk_btn = QPushButton()
wk_btn.setFixedHeight(58)
wk_btn.setStyleSheet(f"""
    QPushButton {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {P_LIGHT}, stop:1 #E0F5EC);   # gradient แนวนอน
        border:1.5px solid {P_ACCENT}55;
        border-radius:14px; text-align:left;
    }}
""")
```

```python
self.weekly_val = QLabel("—")   # จะถูก refresh() อัปเดตเป็น "X kcal this week"
```

```python
wk_btn.clicked.connect(self.mw.show_weekly)   # กด → ไปหน้า Weekly
```

---

## 🔄 `refresh` — อัปเดต UI ทั้งหมด (บรรทัด ~160–220)

> ฟังก์ชันนี้ถูกเรียกทุกครั้งที่เปลี่ยนวัน หรือกลับมาหน้านี้

### อัปเดต Date Label

```python
def refresh(self, log_date=None):
    if log_date:
        self.current_date = log_date   # ถ้าส่งวันมา ให้ใช้วันนั้น
    
    today = date.today()
    if self.current_date == today:
        ds = f"Today · {self.current_date.strftime('%d %b %Y')}"
    elif self.current_date == today - timedelta(days=1):
        ds = f"Yesterday · {self.current_date.strftime('%d %b')}"
    else:
        ds = self.current_date.strftime("%A · %d %b %Y")  # จันทร์ 31 Mar 2026
    self.date_lbl.setText(ds)
```

### [FN] BMR / target kcal calculation

```python
    log = app_data.get_log(self.current_date)   # ดึง log ของวันนี้
    target = app_data.profile.calculate_target_kcal()  # คำนวณเป้าหมาย (BMR × 1.2)
    consumed = log.total_calories() if log else 0       # แคลอรีที่กินแล้ว
    is_cheat = log.is_cheat_day if log else False
```

### อัปเดต Cheat Day checkbox

```python
    self.cheat_cb.blockSignals(True)     # หยุด signal ชั่วคราว ป้องกัน loop
    self.cheat_cb.setChecked(is_cheat)
    self.cheat_cb.blockSignals(False)    # เปิด signal อีกครั้ง
```
- `blockSignals` ป้องกัน infinite loop เมื่อ set ค่า checkbox จากโค้ด

### อัปเดต CalorieMeter

```python
    self.meter.set_data(consumed, target, is_cheat)
```

### กรณี Cheat Day — [FN] Cheat day toggle

```python
    if is_cheat:
        self.status_badge.setText("🎉 Cheat Day!")
        self.status_badge.setStyleSheet(f"color:{ORANGE}; background:{O_LIGHT}; ...")
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background:{L_GRAY}; ... }}
            QProgressBar::chunk {{ background:{ORANGE}; }}   # แถบส้ม
        """)
        self.progress.setValue(100)   # เต็ม 100%
        self.prog_lbl.setText("∞")    # แสดง ∞
```

### กรณีปกติ — [FN] Calorie status + Progress bar

```python
    else:
        st = app_data.get_status(self.current_date)   # "low" / "balanced" / "high"
        col = STATUS_COLOR.get(st, "#78909C")          # สีตัวอักษร
        bg_col = STATUS_BG.get(st, BG2)                # สีพื้นหลัง badge
        
        st_label = {"low": "↓ Low", "balanced": "✓ Balanced", "high": "↑ High"}.get(st, st)
        self.status_badge.setText(st_label)
        self.status_badge.setStyleSheet(f"color:{col}; background:{bg_col}; ...")
        
        # [FN] Progress bar
        pct = int(min(consumed / target * 100, 100)) if target > 0 else 0
        self.progress.setValue(pct)
        self.prog_lbl.setText(f"{pct}%")
        
        # สีแถบ progress ตามสถานะ
        if st == "high":
            chunk_color = RED
        elif st == "balanced":
            chunk_color = P_MED
        else:
            chunk_color = ORANGE
        
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background:{L_GRAY}; border-radius:3px; }}
            QProgressBar::chunk {{ background:{chunk_color}; }}
        """)
```

### อัปเดต Labels

```python
    self.food_lbl.setText(f"Eaten   {int(consumed)} kcal")
    self.goal_lbl.setText(f"Target  {int(target)} kcal")
    
    for m in MEALS:
        c = log.meal_calories(m) if log else 0
        self.meal_cal_lbl[m].setText(f"{int(c)} kcal" if c else "0 kcal")
```

### [FN] Weekly total preview

```python
    # คำนวณวันแรกของสัปดาห์ (วันจันทร์)
    mon = self.current_date - timedelta(days=self.current_date.weekday())
    week = [mon + timedelta(days=i) for i in range(7)]   # จ-อา
    
    wt = app_data.weekly_total(week)   # รวมแคลอรีทั้งสัปดาห์ (ข้าม cheat day)
    self.weekly_val.setText(f"{int(wt)} kcal this week")
```

---

## 📆 Navigation วัน

```python
def _prev(self):
    self.current_date -= timedelta(days=1)   # ถอยหลัง 1 วัน
    self.refresh()

def _next(self):
    self.current_date += timedelta(days=1)   # ไปข้างหน้า 1 วัน
    self.refresh()
```

---

## 🎉 `_toggle_cheat` — [FN] Cheat day toggle

```python
def _toggle_cheat(self):
    app_data.toggle_cheat_day(self.current_date)   # สลับ cheat day on/off
    self.refresh()   # อัปเดต UI ใหม่
```

---

## 🗺️ แผนผังการทำงาน

```
DiaryScreen
│
├── แสดง Header (My Diary + ปุ่มโปรไฟล์)
│
├── Date Navigation (‹ วันที่ ›)
│       ├── กด ‹ → current_date - 1 → refresh()
│       └── กด › → current_date + 1 → refresh()
│
├── Summary Card
│       ├── Status Badge (Low / Balanced / High / Cheat Day)
│       ├── CalorieMeter (วงกลม)
│       ├── Eaten / Target kcal
│       └── Progress Bar (0-100%)
│
├── Meal Buttons (4 ปุ่ม)
│       └── กด → show_meal(meal_type, current_date)
│
└── Weekly Summary Button
        └── กด → show_weekly()
```
