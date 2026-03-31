# 📊 phumin.py — อธิบายโค้ดทีละบรรทัด

> **เจ้าของ:** ภูมินทร์  
> **ไฟล์:** `phumin.py`  
> **หน้าที่:** TrashZone + CalorieMeter + EditDialog + ProfileViewScreen + WeeklyChart + WeeklyScreen

---

## ฟังก์ชันที่รับผิดชอบ (7 FN)

| # | ฟังก์ชัน | อยู่ที่ไหน |
|---|----------|-----------|
| 1 | Edit name / age / height / weight / target weight | `EditDialog` + `ProfileViewScreen._edit()` |
| 2 | Select gender | `ProfileViewScreen` → `QComboBox` |
| 3 | Delete by drag to trash zone | `TrashZone` |
| 4 | Bar color by status (Low / Balanced / High / Cheat) | `WeeklyChart.paintEvent()` |
| 5 | Target dashed line | `WeeklyChart.paintEvent()` |
| 6 | Calorie meter (circular ring) | `CalorieMeter` |
| 7 | Click day → go to Diary | `WeeklyScreen` (chart bar clickable) |

---

## 🗑️ class TrashZone — [FN] Delete by drag to trash zone

### `__init__` (บรรทัด 36–45)

```python
class TrashZone(QFrame):
    delete_signal = Signal()   # Signal ที่ส่งออกเมื่อ drop เข้า zone
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(52)
        self.setAcceptDrops(True)   # รับ drag-and-drop
        self._idle()               # ตั้งสไตล์ idle
        
        l = QLabel("🗑  Drag here to delete")
        l.setAlignment(Qt.AlignCenter)
        l.setStyleSheet(f"color:{RED}; background:transparent; border:none;")
        QHBoxLayout(self).addWidget(l)
```

### สไตล์ 2 แบบ

```python
def _idle(self):
    # สไตล์ปกติ — เส้นประสีชมพูอ่อน
    self.setStyleSheet(f"""
        QFrame {{
            border: 2px dashed #FECACA;
            border-radius: 12px;
            background: {R_LIGHT};
        }}
    """)

def _hot(self):
    # สไตล์เมื่อลากเข้ามา — เส้นประสีแดงเข้ม
    self.setStyleSheet(f"""
        QFrame {{
            border: 2.5px dashed {RED};
            border-radius: 12px;
            background: #FEE2E2;
        }}
    """)
```

### Drag & Drop Events

```python
def dragEnterEvent(self, e):
    self._hot()                  # เปลี่ยนเป็นสีแดงเมื่อลากเข้ามา
    e.acceptProposedAction()     # ยอมรับ drag

def dragLeaveEvent(self, e):
    self._idle()                 # กลับสีปกติเมื่อลากออกไป

def dropEvent(self, e):
    self._idle()                 # กลับสีปกติ
    self.delete_signal.emit()    # ส่ง Signal → MealScreen._delete_sel()
    e.acceptProposedAction()
```
- เมื่อ drop → ส่ง Signal ไปให้ `MealScreen` ลบรายการที่เลือกอยู่

---

## 🔵 class CalorieMeter — [FN] Calorie meter (circular ring)

### `__init__` (บรรทัด 74–80)

```python
class CalorieMeter(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 120)   # ขนาด 120×120 px
        self._consumed = 0            # แคลอรีที่กินแล้ว
        self._target = 2000           # เป้าหมาย (default 2000)
        self._is_cheat = False
        self.setStyleSheet("background:transparent;")
```

### `set_data` — อัปเดตข้อมูล

```python
def set_data(self, consumed, target, is_cheat=False):
    self._consumed = consumed
    self._target = target
    self._is_cheat = is_cheat
    self.update()   # สั่งวาดใหม่ → เรียก paintEvent
```

### `paintEvent` — วาดวงกลม (บรรทัด 88–135)

```python
def paintEvent(self, event):
    p = QPainter(self)
    p.setRenderHint(QPainter.Antialiasing)   # ขอบเรียบ
    W, H = self.width(), self.height()
    cx, cy = W // 2, H // 2   # จุดศูนย์กลาง
    r = min(W, H) // 2 - 10   # รัศมีวงกลม (เว้นขอบ 10px)
    ring = 9                   # ความหนาวงแหวน 9px
```

#### วงแหวนพื้นหลัง (สีเทา)

```python
    p.setPen(QPen(QColor(L_GRAY), ring))   # เส้นสีเทา ความหนา ring
    p.setBrush(Qt.NoBrush)                 # ไม่เติมสี
    p.drawEllipse(cx - r, cy - r, r * 2, r * 2)  # วาดวงกลม
```

#### คำนวณสีของวงแหวน progress

```python
    pct = min(self._consumed / self._target, 1.0) if self._target > 0 else 0
    
    if self._is_cheat:
        arc_color = QColor(ORANGE)       # Cheat Day → ส้ม
    elif pct > 1.0:
        arc_color = QColor(RED)          # เกิน 100% → แดง
    elif pct >= 0.8:
        arc_color = QColor(P_MED)        # 80-100% → เขียวกลาง
    else:
        arc_color = QColor(P_ACCENT)     # < 80% → เขียวสด
```

#### วาดวงแหวน progress

```python
    if self._is_cheat or pct > 0:
        pen = QPen(arc_color, ring)
        pen.setCapStyle(Qt.RoundCap)    # ปลายเส้นโค้งมน
        p.setPen(pen)
        draw_pct = 1.0 if self._is_cheat else pct   # cheat day = เต็ม 100%
        span = int(-draw_pct * 360 * 16)             # Qt ใช้ 1/16 degree
        # ลบ = วนตามเข็มนาฬิกา, เริ่มจาก 90° (บน)
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 90 * 16, span)
```
- Qt ใช้ unit 1/16 degree → 360° = 360 × 16 = 5760 units
- เริ่มจาก 90 × 16 = 1440 units (ด้านบนสุด)

#### ตัวเลขตรงกลาง

```python
    if self._is_cheat:
        # แสดง ∞ สีส้ม
        p.setFont(QFont("Segoe UI", 18, QFont.Bold))
        p.setPen(QColor(ORANGE))
        p.drawText(QRect(0, cy - 16, W, 26), Qt.AlignCenter, "∞")
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(TXT_MUTED))
        p.drawText(QRect(0, cy + 10, W, 16), Qt.AlignCenter, "Cheat Day!")
    else:
        remaining = max(0, int(self._target - self._consumed))   # แคลอรีที่เหลือ
        p.setFont(QFont("Segoe UI", 17, QFont.Bold))
        p.drawText(QRect(0, cy - 14, W, 24), Qt.AlignCenter, str(remaining))
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(TXT_MUTED))
        p.drawText(QRect(0, cy + 10, W, 16), Qt.AlignCenter, "remaining")
```

---

## ✏️ class EditDialog — [FN] Edit name / age / height / weight / target weight

### `__init__` (บรรทัด 142–165)

```python
class EditDialog(QDialog):
    def __init__(self, label, value, parent=None, attr=None):
        super().__init__(parent)
        self._attr = attr           # เก็บว่ากำลัง edit อะไร ("name", "age", ...)
        self.setWindowTitle(f"Edit {label}")
        self.setFixedWidth(320)
        
        root = QVBoxLayout(self)
        root.addWidget(_lbl(f"Edit {label}", bold=True, size=14))
        
        self.edit = _input(str(value) if value else "")
        self.edit.setText(str(value) if value else "")  # กรอกค่าเดิมไว้ก่อน
        root.addWidget(self.edit)
        
        self.err_lbl = QLabel("")
        self.err_lbl.setVisible(False)
        root.addWidget(self.err_lbl)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._try_accept)   # กด OK → ตรวจ validate
        btns.rejected.connect(self.reject)         # กด Cancel → ปิด
        root.addWidget(btns)
```

### `_try_accept` — validate ก่อน accept

```python
def _try_accept(self):
    val = self.edit.text().strip()
    err = self._validate(val)    # ตรวจสอบ
    if err:
        self.err_lbl.setText(f"⚠  {err}")
        self.err_lbl.setVisible(True)    # แสดง error ใน dialog
    else:
        self.err_lbl.setVisible(False)
        self.accept()                     # ปิด dialog + return OK
```

### `_validate` — ตรวจสอบตามประเภท

```python
def _validate(self, val) -> str:
    attr = self._attr
    if not val:
        return ""   # ว่าง → ยอมรับ (optional)
    
    if attr == "name":
        if re.search(r'[!@#$%^&*()...]', val):
            return "Name must not contain special symbols ..."
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
    
    return ""   # ผ่าน → return string ว่าง
```

### `value` — ดึงค่าที่แก้ไข

```python
def value(self):
    return self.edit.text().strip()
```

---

## 👤 class ProfileViewScreen

> หน้าแสดงและแก้ไขโปรไฟล์

### ส่วนสำคัญ

#### [FN] Select gender — QComboBox

```python
self.gc = QComboBox()
self.gc.addItems(["Male", "Female"])
self.gc.setFixedWidth(130)
self.gc.currentTextChanged.connect(self._gender_changed)   # เปลี่ยน → บันทึก pending
```
- ใช้ `QComboBox` แทน RadioButton เพราะเป็นหน้า edit (compact กว่า)

#### [FN] Edit name/age/height/weight — ปุ่ม Edit แต่ละแถว

```python
rows = [("Name", "name", ""), ("Age", "age", "yrs"),
        ("Height", "height", "cm"), ("Weight", "weight", "kg"),
        ("Target Weight", "target_weight", "kg")]

for disp, attr, unit in rows:
    row = QHBoxLayout()
    row.addWidget(_lbl(disp, bold=True, size=13))  # ชื่อ field
    row.addStretch()
    
    vl = _lbl("—", size=13, color=TXT_SUB)        # แสดงค่าปัจจุบัน
    self.flabels[attr] = (vl, unit)                # เก็บ reference
    row.addWidget(vl)
    row.addSpacing(10)
    
    eb = QPushButton("Edit")
    eb.setFixedHeight(30); eb.setFixedWidth(60)
    eb.setStyleSheet(f"""
        QPushButton {{ background:{P_LIGHT}; border:none; color:{PRIMARY};
            font-size:12px; font-weight:bold; border-radius:8px; }}
    """)
    eb.clicked.connect(lambda _, a=attr, d=disp: self._edit(a, d))  # กด → เปิด EditDialog
```

#### `_pending` — ระบบ Unsaved Changes

```python
self._pending: dict = {}    # เก็บค่าที่แก้แล้วแต่ยังไม่ save
self._unsaved = False       # flag ว่ามีการแก้ไขที่ยังไม่ save

def _mark_changed(self):
    self._unsaved = True
    self._warn_banner.setVisible(True)    # แสดง banner เตือน
    self._save_ok_lbl.setVisible(False)

def _clear_unsaved(self):
    self._unsaved = False
    self._pending.clear()
    self._warn_banner.setVisible(False)
```

#### `_gender_changed` — [FN] Select gender

```python
def _gender_changed(self, t):
    self._pending["gender"] = t    # เก็บไว้ใน pending
    self._mark_changed()           # แสดง unsaved warning
    self._refresh_bmr_preview()    # อัปเดต BMR ตาม gender ใหม่
```

#### `_edit` — เปิด EditDialog

```python
def _edit(self, attr, display):
    p = app_data.profile
    current = self._pending.get(attr, getattr(p, attr, ""))
    # ถ้ามีค่า pending ใช้ pending, ถ้าไม่มีใช้จาก profile
    
    dlg = EditDialog(display, current, self, attr=attr)
    if dlg.exec():   # ผู้ใช้กด OK
        val = dlg.value()
        try:
            if attr == "age":
                val = int(val)
            elif attr in ("height", "weight", "target_weight"):
                val = float(val)
        except ValueError:
            return
        
        self._pending[attr] = val    # เก็บใน pending (ยังไม่ save)
        self._mark_changed()
        self._refresh_labels()       # อัปเดต UI ทันที
        self._refresh_bmr_preview()
```

#### `_save_profile` — บันทึกโปรไฟล์จริงๆ

```python
def _save_profile(self):
    p = app_data.profile
    for attr, val in self._pending.items():
        setattr(p, attr, val)   # ใส่ค่า pending ทั้งหมดเข้า profile
    
    self._clear_unsaved()    # ล้าง pending
    self.refresh()           # อัปเดต UI
    
    self._save_ok_lbl.setText("✅  Profile saved!")
    self._save_ok_lbl.setVisible(True)
    QTimer.singleShot(2200, lambda: self._save_ok_lbl.setVisible(False))
    # ซ่อน success message อัตโนมัติหลัง 2.2 วินาที
```

#### `_refresh_bmr_preview`

```python
def _refresh_bmr_preview(self):
    p = app_data.profile
    # ใช้ค่า pending ถ้ามี, ไม่มีใช้จาก profile
    age    = self._pending.get("age",    p.age)
    height = self._pending.get("height", p.height)
    weight = self._pending.get("weight", p.weight)
    gender = self._pending.get("gender", p.gender)
    
    tmp = UserProfile(age=age, height=height, weight=weight, gender=gender)
    self.bmr_lbl.setText(f"Daily Target (BMR × 1.2):  {tmp.calculate_target_kcal()} kcal")
```

---

## 📊 class WeeklyChart — [FN] Bar color + Target dashed line

### `paintEvent` — วาดกราฟทั้งหมด

```python
def paintEvent(self, event):
    p = QPainter(self)
    p.setRenderHint(QPainter.Antialiasing)
    W, H = self.width(), self.height()
    
    pad_l, pad_r = 8, 8     # ขอบซ้าย-ขวา
    pad_top = 20             # ขอบบน
    pad_bot = 24             # ขอบล่าง (สำหรับ label วัน)
    bar_top = pad_top
    bar_bot = H - pad_bot
    bar_area = bar_bot - bar_top   # พื้นที่วาด bar
    
    n = len(self.data)
    slot_w = (W - pad_l - pad_r) / n   # ความกว้างของแต่ละช่องวัน
    
    max_val = max((v for _, v, _ in self.data), default=0)
    mv = max(max_val * 1.15, self.target * 1.15, 500.0)
    # mv = ค่าสูงสุดที่ใช้ scale (เผื่อที่ไว้ 15%)
```

#### [FN] Target dashed line

```python
    # คำนวณ y position ของเส้น target
    ty = int(bar_bot - (self.target / mv) * bar_area)
    
    p.setPen(QPen(QColor(P_ACCENT), 1.2, Qt.DashLine))  # เส้นประ
    p.drawLine(int(pad_l), ty, int(W - pad_r), ty)       # วาดเส้นแนวนอน
    
    p.setFont(QFont("Segoe UI", 7))
    p.setPen(QColor(P_MED))
    p.drawText(QRect(int(W - pad_r - 32), ty - 13, 32, 12),
               Qt.AlignRight, "target")    # label "target"
```

#### [FN] Bar color by status

```python
    bar_w = max(16, int(slot_w * 0.52))   # ความกว้าง bar = 52% ของ slot
    
    for i, (lbl, val, is_cheat) in enumerate(self.data):
        cx = int(pad_l + slot_w * i + slot_w / 2)   # กึ่งกลาง x ของวัน
        bx = cx - bar_w // 2                         # x เริ่มต้น bar
        
        # คำนวณความสูง bar
        if is_cheat:
            bh = max(6, int(bar_area * 0.18))   # cheat day = สั้น 18%
        elif val > 0:
            bh = max(4, int((val / mv) * bar_area))   # สัดส่วนตามค่า
        else:
            bh = 3   # ไม่มีข้อมูล = เส้นบางๆ
        
        by = int(bar_bot) - bh   # y เริ่มต้น bar (จากล่างขึ้นบน)
        
        # [FN] Bar color by status (Low / Balanced / High / Cheat)
        if is_cheat:
            fill = QColor(ORANGE)                  # ส้ม = cheat day
        elif val > self.target * 1.1:
            fill = QColor(RED)                     # แดง = เกินเป้า
        elif val >= self.target * 0.8:
            fill = QColor(P_MED)                   # เขียว = สมดุล
        elif val > 0:
            fill = QColor(P_ACCENT)
            fill.setAlpha(160)                     # เขียวโปร่ง = ต่ำกว่าเป้า
        else:
            fill = QColor(L_GRAY)                  # เทา = ไม่มีข้อมูล
```

```python
        # วาด bar พร้อม gradient
        if bh > 3:
            grad = QLinearGradient(bx, by, bx, by + bh)
            c1 = QColor(fill); c2 = QColor(fill); c2.setAlpha(max(80, c2.alpha() - 60))
            grad.setColorAt(0, c1); grad.setColorAt(1, c2)   # ค่อยๆ จางลงล่าง
            p.setBrush(QBrush(grad))
        else:
            p.setBrush(QBrush(fill))
        
        path = QPainterPath()
        path.addRoundedRect(bx, by, bar_w, bh, min(3, bh // 2), min(3, bh // 2))
        p.drawPath(path)   # วาด bar มุมโค้ง
```

```python
        # label ตัวเลข บน bar
        txt = "∞" if is_cheat else (str(int(val)) if val > 0 else "")
        if txt:
            p.setFont(QFont("Segoe UI", 7, QFont.Bold))
            p.setPen(QColor(TXT_SUB))
            p.drawText(QRect(bx - 6, max(0, by - 14), bar_w + 12, 13),
                       Qt.AlignCenter, txt)
        
        # label วัน ล่าง bar
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor(TXT_SUB))
        p.drawText(QRect(cx - 18, int(bar_bot) + 5, 36, 16),
                   Qt.AlignCenter, lbl)   # "Mon", "Tue", ...
```

---

## 📅 class WeeklyScreen — [FN] Click day → go to Diary

### `_build` — สร้าง UI

```python
# Navigation ← Prev / Next →
self.pb = QPushButton("‹ Prev")
self.pb.clicked.connect(self._prev)   # สัปดาห์ก่อน
self.nb = QPushButton("Next ›")
self.nb.clicked.connect(self._next)   # สัปดาห์ถัดไป
```

```python
# WeeklyChart
self.chart = WeeklyChart()
ccl.addWidget(self.chart)
```

```python
# Cheat Day checkboxes (จ-อา)
self.cheat_cbs = {}
sketch_order = [(6, "Sun"), (0, "Mon"), (1, "Tue"), ...]
for dow, name in sketch_order:
    cb = QCheckBox(name)
    cb.setProperty("dow", dow)       # เก็บ day of week ไว้กับ checkbox
    cb.stateChanged.connect(self._cheat_toggled)
    self.cheat_cbs[dow] = cb
```

### `_get_week` — คำนวณวันในสัปดาห์

```python
def _get_week(self):
    today = date.today()
    # หาวันอาทิตย์ต้นสัปดาห์ + offset
    sun = today - timedelta(days=(today.weekday() + 1) % 7) + timedelta(weeks=self.week_offset)
    return [sun + timedelta(days=i) for i in range(7)]   # อา-เสาร์
```

### `refresh` — อัปเดต UI

```python
def refresh(self):
    week = self._get_week()
    self._week_dates = week
    self.wl.setText(f"{week[0].strftime('%d %b')} – {week[-1].strftime('%d %b %Y')}")
    
    td = app_data.profile.calculate_target_kcal()   # เป้าหมายต่อวัน
    tw = td * 7                                       # เป้าหมายต่อสัปดาห์
    
    # สร้างข้อมูลสำหรับ chart
    chart_data = []
    for i, d in enumerate(week):
        log = app_data.get_log(d)
        val = log.total_calories() if log else 0
        cheat = log.is_cheat_day if log else False
        chart_data.append((DAY_LABEL[i], val, cheat))
    
    self.chart.set_data(chart_data, td)   # ส่งข้อมูลให้ WeeklyChart วาด
```

```python
    # อัปเดต cheat day checkboxes
    for d in week:
        dow = d.weekday()
        if dow in self.cheat_cbs:
            cb = self.cheat_cbs[dow]
            cb.blockSignals(True)
            log = app_data.get_log(d)
            cb.setChecked(log.is_cheat_day if log else False)
            cb.blockSignals(False)
```

```python
    total = app_data.weekly_total(week)    # รวมแคลอรีสัปดาห์ (ข้าม cheat)
    self.total_val.setText(f"{int(total)} kcal")
    self.target_val.setText(f"{int(tw)} kcal")
    
    # สถานะสัปดาห์
    if total < tw * 0.8:
        s, c, icon = "Below target this week", GRAY, "↓"
        st_bg = O_LIGHT
    elif total <= tw * 1.1:
        s, c, icon = "On track this week!  🎯", P_MED, "✓"
        st_bg = P_LIGHT
    else:
        s, c, icon = "Exceeded weekly target", RED, "↑"
        st_bg = R_LIGHT
```

### `_cheat_toggled` — toggle cheat day จาก checkbox

```python
def _cheat_toggled(self):
    if not self._week_dates: return
    for d in self._week_dates:
        dow = d.weekday()
        if dow in self.cheat_cbs:
            cb = self.cheat_cbs[dow]
            log = app_data.get_or_create_log(d)
            if cb.isChecked() != log.is_cheat_day:
                app_data.toggle_cheat_day(d)   # toggle ถ้าไม่ตรงกัน
    self.refresh()
```

---

## 🗺️ แผนผังการทำงาน

```
phumin.py มี 4 class หลัก:

TrashZone (ใช้ใน MealScreen)
    └── drag → hot style → drop → emit delete_signal → MealScreen._delete_sel()

CalorieMeter (ใช้ใน DiaryScreen)
    └── set_data(consumed, target, is_cheat) → paintEvent วาดใหม่

ProfileViewScreen
    ├── แสดงข้อมูลโปรไฟล์
    ├── กด Edit → EditDialog → บันทึกไว้ใน _pending
    └── กด Save → ใส่ _pending เข้า profile จริง

WeeklyScreen
    ├── WeeklyChart (วาดกราฟ bar 7 วัน)
    │       ├── Bar color ตามสถานะ
    │       └── เส้นประ target
    ├── Cheat Day checkboxes
    └── Total / Target สัปดาห์
```
