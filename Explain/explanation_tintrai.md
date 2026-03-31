# 👤 tintrai.py — อธิบายโค้ดทีละบรรทัด

> **เจ้าของ:** ทิ้นไตร  
> **ไฟล์:** `tintrai.py`  
> **หน้าที่:** Profile Setup Screen — หน้าสร้างโปรไฟล์ผู้ใช้ครั้งแรก

---

## ฟังก์ชันที่รับผิดชอบ (6 FN)

| # | ฟังก์ชัน | อยู่ที่ไหน |
|---|----------|-----------|
| 1 | Validate name | `_validate_name_inline()`, `_submit()` |
| 2 | Validate email | `_validate_email_inline()`, `_submit()` |
| 3 | Validate age / height / weight | `_validate_numbers_inline()`, `_submit()` |
| 4 | Select gender | Radio buttons Male/Female |
| 5 | BMR preview | `_update_preview()` |
| 6 | Submit → save profile | `_submit()` |

---

## 📌 IMPORT (บรรทัด 1–16)

```python
import re
```
- ใช้ตรวจสอบ pattern ของชื่อและอีเมล เช่น `re.match(r'^[\w\.\+\-]+@...')` 

```python
from shared import (
    QWidget, QVBoxLayout, QHBoxLayout, ...
    QRadioButton, QButtonGroup,           # ปุ่มเลือก gender
    QDoubleValidator, QIntValidator,      # ตรวจสอบตัวเลข
    ...
    UserProfile, app_data,
)
```

---

## 🖼️ class ProfileScreen

> หน้าจอกรอกข้อมูลส่วนตัว

### `__init__` (บรรทัด 20–30)

```python
def __init__(self, mw):
    super().__init__()
    self.mw = mw              # เก็บ MainWindow ไว้ navigate
    self.setStyleSheet(f"background:{BG};")
    outer = QVBoxLayout(self) # layout หลักแนวตั้ง
    outer.setContentsMargins(0, 0, 0, 0)  # ไม่มีขอบ
    outer.setSpacing(0)
```

### Banner บนสุด

```python
banner = GradientWidget(PRIMARY, P_MED, "#2E9E60", radius=0, vertical=False)
banner.setFixedHeight(130)   # ความสูง banner 130px
```

```python
av_banner = QLabel("👤")     # icon คน
av_banner.setStyleSheet(f"""
    background: rgba(255,255,255,0.18);   # ขาวโปร่งแสง
    border-radius: 30px;                   # มุมโค้ง
    min-width:60px; max-width:60px;
    min-height:60px; max-height:60px;
""")
```

```python
t = QLabel("Create Your Profile")
t.setFont(QFont("Segoe UI", 14, QFont.Bold))
t.setStyleSheet("color:white; background:transparent;")
```

### ScrollArea — เนื้อหาที่ scroll ได้

```python
scroll = QScrollArea()
scroll.setWidgetResizable(True)   # ให้ inner widget ขยายตาม scroll area
inner = QWidget()
lay = QVBoxLayout(inner)
lay.setContentsMargins(20, 20, 20, 32)
lay.setSpacing(14)
scroll.setWidget(inner)
```
- ห่อเนื้อหาด้วย QScrollArea เพราะฟอร์มยาวเกิน 1 หน้าจอ

---

### [FN] Validate name — ช่องกรอกชื่อ

```python
lay.addWidget(_lbl("Full Name", bold=True, size=12, color=TXT_SUB))
self.name_e = _input("Enter your name")
self.name_e.textChanged.connect(self._validate_name_inline)   # validate ทุกครั้งที่พิมพ์
lay.addWidget(self.name_e)

self.name_err = QLabel("")   # label แสดง error
self.name_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
self.name_err.setVisible(False)   # ซ่อนไว้ก่อน
lay.addWidget(self.name_err)
```

---

### [FN] Validate email — ช่องกรอกอีเมล

```python
lay.addWidget(_lbl("Email (optional)", bold=True, size=12, color=TXT_SUB))
self.gmail_e = _input("example@gmail.com")
self.gmail_e.textChanged.connect(self._validate_email_inline)
```

---

### [FN] Validate age / height / weight — 3 ช่องในแถวเดียว

```python
for label, attr, ph, val in [
    ("Age",         "age_e",    "yrs", QIntValidator(1, 120)),       # อายุ 1-120
    ("Height (cm)", "height_e", "cm",  QDoubleValidator(50, 272, 1)), # ส่วนสูง 50-272
    ("Weight (kg)", "weight_e", "kg",  QDoubleValidator(2, 650, 1)),  # น้ำหนัก 2-650
]:
    col = QVBoxLayout()   # column สำหรับแต่ละช่อง
    col.addWidget(_lbl(label, bold=True, size=12, color=TXT_SUB))
    ed = _input(ph)
    ed.setValidator(val)          # ตั้ง validator — ป้องกันพิมพ์ผิดประเภท
    setattr(self, attr, ed)       # เก็บ reference: self.age_e, self.height_e, self.weight_e
    col.addWidget(ed)
    row.addLayout(col)
    
    # Error label แต่ละช่อง
    err_lbl = QLabel("")
    err_lbl.setVisible(False)
    setattr(self, attr.replace("_e", "_err"), err_lbl)   # self.age_err, self.height_err, ...
```
- `setattr(self, attr, ed)` = สร้าง attribute ชื่อ attr ให้กับ self แบบ dynamic

```python
self.age_e.textChanged.connect(self._validate_numbers_inline)
self.height_e.textChanged.connect(self._validate_numbers_inline)
self.weight_e.textChanged.connect(self._validate_numbers_inline)
```
- ทุกช่องเชื่อมกับฟังก์ชันเดียว เพราะตรวจทั้งหมดพร้อมกัน

---

### [FN] Select gender — Radio Buttons

```python
self.male_rb = QRadioButton("  Male")
self.female_rb = QRadioButton("  Female")
self.male_rb.setChecked(True)   # Male เป็น default

self.bg = QButtonGroup()        # Group ทำให้เลือกได้แค่ 1 อย่าง
self.bg.addButton(self.male_rb)
self.bg.addButton(self.female_rb)

for rb in (self.male_rb, self.female_rb):
    rb.setStyleSheet(f"""
        QRadioButton {{
            color:{TXT}; background:{CARD};
            border:1.5px solid {BORDER}; border-radius:10px;
            padding:10px 18px; font-size:13px;
        }}
        QRadioButton:checked {{
            border-color:{PRIMARY}; background:{P_LIGHT};
            color:{PRIMARY}; font-weight:bold;
        }}
        QRadioButton::indicator {{ width:0; height:0; border:none; }}
        # ซ่อน indicator circle เพราะใช้ border ของปุ่มทั้งหมดแทน
    """)
```

---

### Target Weight (optional)

```python
lay.addWidget(_lbl("Target Weight (kg)", bold=True, size=12, color=TXT_SUB))
self.tw_e = _input("Optional — your goal weight")
self.tw_e.setValidator(QDoubleValidator(2, 650, 1))
self.tw_e.textChanged.connect(self._validate_tw_inline)
```

---

### [FN] BMR preview

```python
self.bmr_preview = _lbl("Fill in your info to see daily calorie target", ...)
self.bmr_preview.setStyleSheet(f"""
    color:{TXT_SUB}; background:{P_LIGHT};
    border-radius:10px; padding:10px;
""")

# เชื่อมทุกช่องที่เกี่ยวกับ BMR
for e in (self.age_e, self.height_e, self.weight_e):
    e.textChanged.connect(self._update_preview)
self.male_rb.toggled.connect(self._update_preview)  # เปลี่ยน gender ก็ update
```

---

## ✅ ฟังก์ชัน Validation

### `_validate_name_inline` — [FN] Validate name (บรรทัด ~110–125)

```python
def _validate_name_inline(self, text):
    n = text.strip()
    if not n:
        self.name_err.setVisible(False)   # ยังไม่พิมพ์ → ไม่แสดง error
        return
    
    if re.search(r'[!@#$%^&*()\[\]{}<>/\\|+=~`"\'?;:,_]', n):
        # ถ้าพบสัญลักษณ์พิเศษ
        self.name_err.setText("⚠  Name must not contain special symbols (e.g. ! @ # $ % ^ & *)")
        self.name_err.setVisible(True)
    
    elif not re.search(r'[A-Za-zก-๙]', n):
        # ถ้าไม่มีตัวอักษรเลย (มีแต่ตัวเลขหรืออื่นๆ)
        self.name_err.setText("⚠  Name must contain at least one letter")
        self.name_err.setVisible(True)
    
    else:
        self.name_err.setVisible(False)   # ผ่าน → ซ่อน error
```
- `r'[A-Za-zก-๙]'` = ยอมรับทั้งภาษาอังกฤษและภาษาไทย

---

### `_validate_email_inline` — [FN] Validate email (บรรทัด ~127–134)

```python
def _validate_email_inline(self, text):
    email = text.strip()
    if email and not re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', email):
        # email ไม่ว่าง AND ไม่ตรง pattern
        self.email_err.setText("⚠  Please enter a valid email address (e.g. example@gmail.com)")
        self.email_err.setVisible(True)
    else:
        self.email_err.setVisible(False)
```
- Pattern `^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$`:
  - `^[\w\.\+\-]+` = ต้นประโยค: ตัวอักษร, `.`, `+`, `-` หนึ่งครั้งขึ้นไป
  - `@` = มี @ 
  - `[\w\-]+` = domain (ตัวอักษรหรือ -)
  - `\.[a-zA-Z]{2,}$` = จบด้วย `.com`, `.org` เป็นต้น

---

### `_validate_numbers_inline` — [FN] Validate age/height/weight (บรรทัด ~136–175)

```python
def _validate_numbers_inline(self):
    # ตรวจ Age
    a = self.age_e.text().strip()
    if a:
        try:
            v = int(a)
            if not (1 <= v <= 120):   # ต้องอยู่ในช่วง 1-120
                self.age_err.setText("⚠  Age must be between 1 and 120")
                self.age_err.setVisible(True)
            else:
                self.age_err.setVisible(False)
        except ValueError:            # พิมพ์ตัวอักษรที่ไม่ใช่ตัวเลข
            self.age_err.setText("⚠  Numbers only")
            self.age_err.setVisible(True)
    else:
        self.age_err.setVisible(False)   # ยังไม่พิมพ์ → ไม่แสดง error
    
    # ตรวจ Height (คล้ายกัน แต่ใช้ float)
    h = self.height_e.text().strip()
    if h:
        try:
            v = float(h)
            if not (50.0 <= v <= 272.0):
                self.height_err.setText("⚠  50–272 cm")
                ...
        except ValueError: ...
    
    # ตรวจ Weight (คล้ายกัน)
    w = self.weight_e.text().strip()
    ...
```

---

### `_update_preview` — [FN] BMR preview (บรรทัด ~185–196)

```python
def _update_preview(self):
    try:
        a = int(self.age_e.text())       # อ่านอายุ
        h = float(self.height_e.text())  # อ่านส่วนสูง
        w = float(self.weight_e.text())  # อ่านน้ำหนัก
        g = "Male" if self.male_rb.isChecked() else "Female"  # อ่าน gender
        
        tmp = UserProfile(age=a, height=h, weight=w, gender=g)   # สร้าง profile ชั่วคราว
        bmr = tmp.calculate_bmr()         # คำนวณ BMR
        tgt = tmp.calculate_target_kcal() # คำนวณเป้าหมาย
        
        self.bmr_preview.setText(
            f"BMR: {bmr} kcal  ·  Daily Target (×1.2): {tgt} kcal"
        )
    except (ValueError, ZeroDivisionError):
        # ถ้ายังกรอกไม่ครบ หรือกรอกผิด → แสดงข้อความเริ่มต้น
        self.bmr_preview.setText("Fill in your info to see daily calorie target")
```
- สร้าง `UserProfile` ชั่วคราวเพื่อใช้ `calculate_bmr()` โดยไม่ต้อง save ก่อน

---

### `_submit` — [FN] Submit → save profile (บรรทัด ~198–280)

```python
def _submit(self):
    self.form_err.setVisible(False)
    
    # อ่านค่าจากฟอร์ม
    n     = self.name_e.text().strip()
    a     = self.age_e.text().strip()
    h     = self.height_e.text().strip()
    w     = self.weight_e.text().strip()
    email = self.gmail_e.text().strip()
    
    # ตรวจว่ากรอกครบ
    if not all([n, a, h, w]):
        self.form_err.setText("⚠  Please fill in all required fields.")
        self.form_err.setVisible(True)
        return    # หยุดทำงาน ไม่ไปต่อ
```

```python
    # Validate แต่ละช่อง (ซ้ำอีกครั้งเพื่อความปลอดภัย)
    if re.search(r'[!@#$%^&*()...]', n): ...  # ชื่อมี symbol → error
    if email and not re.match(r'...', email): ...  # email ผิด format → error
    
    try:
        age_val = int(a)
        if not (1 <= age_val <= 120): ...
    except ValueError: ...
    
    # (validate height, weight คล้ายกัน)
```

```python
    # ผ่านทุก validation → บันทึก Profile
    app_data.profile = UserProfile(
        name=n, gmail=email,
        age=age_val, height=height_val, weight=weight_val,
        gender="Male" if self.male_rb.isChecked() else "Female",
        target_weight=tw_val,
    )
    self.mw.show_diary()    # ไปหน้า Home
```

---

## 🗺️ แผนผังการทำงาน

```
ProfileScreen
│
├── กรอกชื่อ → validate_name_inline() (ทันที)
├── กรอกอีเมล → validate_email_inline() (ทันที)
├── กรอกอายุ/ส่วนสูง/น้ำหนัก → validate_numbers_inline() (ทันที)
│                                  + update_preview() (แสดง BMR)
├── เลือก gender → update_preview()
│
└── กด "Create Profile"
        ├── validate ทั้งหมดอีกครั้ง
        ├── มี error → แสดง error, หยุด
        └── ผ่านหมด → บันทึก UserProfile → show_diary()
```
