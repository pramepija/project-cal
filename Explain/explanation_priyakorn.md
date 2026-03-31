# 🍽️ priyakorn.py — อธิบายโค้ดทีละบรรทัด

> **เจ้าของ:** ปริยากร  
> **ไฟล์:** `priyakorn.py`  
> **หน้าที่:** MealScreen — หน้าบันทึกอาหารแต่ละมื้อ

---

## ฟังก์ชันที่รับผิดชอบ (7 FN)

| # | ฟังก์ชัน | อยู่ที่ไหน |
|---|----------|-----------|
| 1 | Food name autocomplete | `_name_changed()`, `_comp_pick()`, `_refresh_comp()` |
| 2 | Kcal/100g input | `self.cal_e` + `QDoubleValidator` |
| 3 | Amount input + kcal preview | `self.amt_e` + `_update_kcal_preview()` |
| 4 | Save to library checkbox | `self.save_cb` ใน `_add_food()` |
| 5 | Add food to log | `_add_food()` |
| 6 | Filter food in table | `_filter_table()` |
| 7 | Delete selected (button) | `_delete_sel()` |

---

## 📌 IMPORT (บรรทัด 1–30)

```python
from phumin import TrashZone          # widget ลาก-ทิ้งลบอาหาร (ของ Phumin)
from panhathai import LibraryDialog   # dialog คลังอาหาร (ของ Panhathai)
```
- import ข้ามไฟล์เพื่อใช้ widget ของเพื่อนร่วมทีม

---

## 🖼️ class MealScreen

### `__init__` (บรรทัด 34–40)

```python
def __init__(self, mw):
    super().__init__()
    self.mw = mw
    self.meal_type = "Breakfast"   # มื้อเริ่มต้น
    self.log_date = date.today()   # วันเริ่มต้น
    self.setStyleSheet(f"background:{BG};")
    self._build()
```

---

### `_build` — สร้าง UI ทั้งหมด (บรรทัด 42–)

#### Top Bar

```python
top = GradientWidget(PRIMARY, P_MED, vertical=False)
top.setFixedHeight(56)
tl = QHBoxLayout(top)
tl.setContentsMargins(12, 0, 12, 0)

back = QPushButton("‹")    # ปุ่มย้อนกลับ
back.setFixedSize(38, 38)
back.setStyleSheet(f"""
    QPushButton {{ background:rgba(255,255,255,0.20); border:none;
        border-radius:10px; font-size:20px; color:white; }}
    QPushButton:hover {{ background:rgba(255,255,255,0.35); color:white; }}
""")
back.clicked.connect(self._go_back)
```

```python
self.title_lbl = _lbl("Breakfast", bold=True, size=17, color="white")
self.title_lbl.setAlignment(Qt.AlignCenter)   # ชื่อมื้ออาหาร ตรงกลาง
```

```python
lib_btn = QPushButton("📚  Library")    # ปุ่มเปิดคลังอาหาร
lib_btn.setFixedHeight(34)
lib_btn.setFixedWidth(110)
lib_btn.setStyleSheet(f"""
    QPushButton {{ background:rgba(255,255,255,0.20); color:white;
        border:1.5px solid rgba(255,255,255,0.45); ... }}
""")
lib_btn.clicked.connect(self._open_lib)   # เปิด LibraryDialog
```

---

#### Add Food Card

```python
add_card = _card()           # กล่องขาวมีขอบ
acl = QVBoxLayout(add_card)
acl.setContentsMargins(16, 14, 16, 14)
acl.setSpacing(8)
acl.addWidget(_lbl("Add Food", bold=True, size=14))
```

##### [FN] Food name autocomplete

```python
self.name_e = _input("Food name (e.g. Steamed rice)")

self._comp = QCompleter([])   # Completer เริ่มต้น list ว่าง
self._comp.setCaseSensitivity(Qt.CaseInsensitive)   # ไม่ตัวพิมพ์ใหญ่-เล็ก
self._comp.setFilterMode(Qt.MatchContains)          # ค้นแบบ contains (ไม่ต้องขึ้นต้น)
self._comp.activated.connect(self._comp_pick)       # เลือกจาก dropdown → _comp_pick

self.name_e.setCompleter(self._comp)                # ผูก completer กับ input
self.name_e.textChanged.connect(self._name_changed) # พิมพ์ → _name_changed
acl.addWidget(self.name_e)
```
- `QCompleter` = dropdown แนะนำชื่อขณะพิมพ์

##### [FN] Kcal/100g input

```python
self.cal_e = _input("Kcal / 100g")
self.cal_e.setValidator(QDoubleValidator(0, 99999, 1))   # ตัวเลขทศนิยม 1 ตำแหน่ง
```

##### [FN] Amount input + kcal preview

```python
self.amt_e = _input("Amount (grams)")
self.amt_e.setValidator(QDoubleValidator(0, 99999, 1))
```

```python
self.kcal_preview = _lbl("", size=11, color=TXT_MUTED)  # label แสดงตัวอย่างแคลอรี

# ทั้งสองช่องเชื่อมกับ _update_kcal_preview
self.cal_e.textChanged.connect(self._update_kcal_preview)
self.amt_e.textChanged.connect(self._update_kcal_preview)
```

##### [FN] Save to library checkbox

```python
self.save_cb = QCheckBox("Save to library")
self.save_cb.setChecked(True)   # ติ๊กไว้เป็น default
self.save_cb.setStyleSheet(f"color:{TXT_SUB}; background:transparent; font-size:11px;")
```

##### [FN] Add food to log — ปุ่ม + Add Food

```python
add_btn = _btn_primary("+ Add Food", h=38)
add_btn.setFixedWidth(120)
add_btn.clicked.connect(self._add_food)   # กด → _add_food()
```

```python
# Error message (ซ่อนไว้ก่อน)
self.add_err = QLabel("")
self.add_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
self.add_err.setVisible(False)
```

---

#### Food List

##### [FN] Filter food in table — ช่องค้นหา

```python
self.srch = _input("🔍  Search", 32)
self.srch.setMaximumWidth(150)
self.srch.textChanged.connect(self._filter_table)   # พิมพ์ → filter ตาราง
```

##### ตารางรายการอาหาร

```python
self.table = QTableWidget()
self.table.setColumnCount(4)
self.table.setHorizontalHeaderLabels(["Food", "kcal/100g", "Amount", "Total"])

hh = self.table.horizontalHeader()
hh.setSectionResizeMode(0, QHeaderView.Stretch)           # คอลัมน์ Food ขยายเต็ม
hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # คอลัมน์อื่นพอดีเนื้อหา
hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)

self.table.setSelectionBehavior(QAbstractItemView.SelectRows)   # เลือกทั้งแถว
self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)    # ห้ามแก้ไขในตาราง
self.table.setDragEnabled(True)      # เปิด drag (สำหรับลาก → TrashZone)
self.table.setAcceptDrops(False)     # ไม่รับ drop เข้าตาราง
self.table.verticalHeader().setVisible(False)   # ซ่อนตัวเลขแถว
self.table.setShowGrid(False)        # ซ่อนเส้นตาราง
```

##### TrashZone (ของ Phumin)

```python
self.trash = TrashZone()
self.trash.delete_signal.connect(self._delete_sel)   # drop ใน trash → _delete_sel
```

##### Total label

```python
self.total_lbl = _lbl("Total : 0 kcal", bold=True, size=13, color=PRIMARY)
```

---

## ⚙️ ฟังก์ชันต่างๆ

### `_update_kcal_preview` — [FN] Amount + kcal preview (บรรทัด ~120–130)

```python
def _update_kcal_preview(self):
    try:
        c = float(self.cal_e.text())    # แคลอรี/100g
        a = float(self.amt_e.text())    # ปริมาณ (g)
        total = round((a / 100) * c, 1)  # สูตร: แคลอรีรวม = (g/100) × kcal/100g
        self.kcal_preview.setText(f"→ {total} kcal")
        self.kcal_preview.setStyleSheet(
            f"color:{PRIMARY}; background:transparent; font-weight:bold; font-size:12px;"
        )
    except ValueError:
        self.kcal_preview.setText("")   # ถ้ายังไม่ครบ → ไม่แสดง
```

---

### `_refresh_comp` — รีเฟรช autocomplete list

```python
def _refresh_comp(self):
    self._comp.setModel(
        QStringListModel([f.name for f in app_data.food_library.all()])
    )
    # อัปเดต list ของ completer จากคลังอาหารล่าสุด
```
- `QStringListModel` = model สำหรับเก็บ list ของ string

---

### `_name_changed` — [FN] Food name autocomplete auto-fill (บรรทัด ~134–137)

```python
def _name_changed(self, t):
    s = app_data.food_library.find(t)    # ค้นหาชื่อที่ตรงพอดี
    if s:
        self.cal_e.setText(str(s.cal_per_100g))   # เติมแคลอรีอัตโนมัติ
```
- เมื่อพิมพ์ชื่ออาหารที่มีในคลัง → กรอก kcal/100g ให้อัตโนมัติ

---

### `_comp_pick` — เลือกจาก dropdown

```python
def _comp_pick(self, name):
    s = app_data.food_library.find(name)
    if s:
        self.cal_e.setText(str(s.cal_per_100g))   # เติมแคลอรีเมื่อเลือกจาก autocomplete
```

---

### `_open_lib` — เปิด Food Library

```python
def _open_lib(self):
    dlg = LibraryDialog(self)
    dlg.food_selected.connect(lambda n, c: (
        self.name_e.setText(n),    # เติมชื่อ
        self.cal_e.setText(str(c)), # เติมแคลอรี
        self.amt_e.setFocus()       # เอา cursor ไปที่ช่อง Amount
    ))
    dlg.exec()              # เปิด dialog แบบ modal (รอจนกว่าจะปิด)
    self._refresh_comp()    # อัปเดต autocomplete หลังปิด dialog
```

---

### `set_meal` — ตั้งค่ามื้ออาหาร (เรียกจาก DiaryScreen)

```python
def set_meal(self, mt, ld):
    self.meal_type = mt       # เช่น "Breakfast"
    self.log_date = ld        # วันที่
    self.title_lbl.setText(f"{MEAL_ICONS.get(mt, '🍽')}  {mt}")  # update title
    self._refresh_comp()      # โหลด autocomplete
    self._refresh_table()     # โหลดตาราง
```

---

### `_add_food` — [FN] Add food to log (บรรทัด ~155–180)

```python
def _add_food(self):
    n = self.name_e.text().strip()    # ชื่ออาหาร
    c = self.cal_e.text().strip()     # kcal/100g
    a = self.amt_e.text().strip()     # ปริมาณ
    
    # ตรวจว่ากรอกครบ 3 ช่อง
    if not all([n, c, a]):
        self.add_err.setText("⚠  Please fill in Food Name, Kcal/100g, and Amount.")
        self.add_err.setVisible(True)
        return
    
    self.add_err.setVisible(False)
    cal, amt = float(c), float(a)
    
    # [FN] Save to library checkbox
    if self.save_cb.isChecked():
        app_data.food_library.add(n, cal)   # บันทึกลงคลัง
        self._refresh_comp()
    
    # บันทึกลง log ประจำวัน
    app_data.add_food(FoodItem(n, cal, amt, self.meal_type, self.log_date))
    
    # ล้างฟอร์ม
    self.name_e.clear()
    self.cal_e.clear()
    self.amt_e.clear()
    self.kcal_preview.setText("")
    
    self._refresh_table()   # รีเฟรชตาราง
```

---

### `_refresh_table` — รีเฟรชตาราง

```python
def _refresh_table(self):
    log = app_data.get_log(self.log_date)
    items = log.get_meal(self.meal_type) if log else []   # ดึงเฉพาะมื้อนี้
    self._fill(items)
    total = log.meal_calories(self.meal_type) if log else 0
    self.total_lbl.setText(f"Total : {int(total)} kcal")
```

---

### `_fill` — เติมข้อมูลลงตาราง

```python
def _fill(self, items):
    self.table.setRowCount(len(items))   # ตั้งจำนวนแถว
    for r, it in enumerate(items):
        vals = [it.name, str(int(it.cal_per_100g)), f"{int(it.amount_g)}g", f"{it.total_cal}"]
        aligns = [Qt.AlignLeft | Qt.AlignVCenter,
                  Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter]
        bg = QColor(BG2) if r % 2 == 0 else QColor(CARD)   # สลับสีแถว
        
        for col, (val, align) in enumerate(zip(vals, aligns)):
            cell = QTableWidgetItem(val)
            cell.setTextAlignment(align)
            cell.setBackground(bg)
            self.table.setItem(r, col, cell)
        
        # เก็บ food ID ซ่อนไว้กับ cell แรก สำหรับใช้ลบ
        self.table.item(r, 0).setData(Qt.UserRole, it.id)
```

---

### `_filter_table` — [FN] Filter food in table (บรรทัด ~195–202)

```python
def _filter_table(self, t):
    log = app_data.get_log(self.log_date)
    items = log.get_meal(self.meal_type) if log else []
    if t:
        items = [i for i in items if t.lower() in i.name.lower()]
        # กรองเฉพาะที่มี keyword (case-insensitive)
    self._fill(items)
```

---

### `_delete_sel` — [FN] Delete selected (บรรทัด ~204–213)

```python
def _delete_sel(self):
    row = self.table.currentRow()   # แถวที่เลือกอยู่
    if row < 0:
        return   # ไม่มีแถวที่เลือก → ออก
    
    cell = self.table.item(row, 0)   # cell แรกของแถว
    if cell:
        fid = cell.data(Qt.UserRole)   # ดึง food ID ที่ซ่อนไว้
        if fid:
            app_data.remove_food(self.log_date, fid)   # ลบจาก log
            self._refresh_table()                       # รีเฟรชตาราง
```
- ใช้ `Qt.UserRole` เก็บ ID ซ่อนไว้ใน cell เพื่อไม่ต้อง match ด้วยชื่อ

---

### `_go_back` — กลับหน้า Diary

```python
def _go_back(self):
    self.mw.show_diary(self.log_date)   # กลับพร้อมส่งวันที่ไปด้วย (ไม่ reset วัน)
```

---

## 🗺️ แผนผังการทำงาน

```
MealScreen (เปิดจาก DiaryScreen)
│
├── Header (‹ ชื่อมื้อ Library)
│
├── Add Food Card
│       ├── กรอกชื่อ → autocomplete → กรอก kcal/100g อัตโนมัติ
│       ├── กรอก kcal/100g + Amount → แสดง preview แคลอรีรวม
│       ├── ติ๊ก "Save to library" → บันทึกลงคลังด้วย
│       └── กด "+ Add Food" → ตรวจ → บันทึก → refresh ตาราง
│
├── Food List
│       ├── ช่องค้นหา → filter ตาราง
│       ├── ตาราง (drag เพื่อลบ → TrashZone)
│       └── Total kcal
│
└── กด ‹ → show_diary(log_date)
```
