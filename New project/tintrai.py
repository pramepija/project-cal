# ============================================================
#  tintrai.py  —  Profile Setup Screen
#  Owner: Tintrai
#  Functions:
#    [FN] Validate name
#    [FN] Validate email
#    [FN] Validate age / height / weight
#    [FN] Select gender
#    [FN] BMR preview
#    [FN] Submit → save profile
# ============================================================
import re
from shared import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QRadioButton, QButtonGroup,
    QDoubleValidator, QIntValidator,
    Qt, QFont, QColor,
    PRIMARY, P_MED, P_LIGHT, P_ACCENT,
    BG, CARD, BORDER, RED, R_LIGHT, TXT, TXT_SUB, TXT_MUTED,
    _lbl, _input, _btn_primary,
    GradientWidget, UserProfile, app_data,
)


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

        # [FN] Validate name
        lay.addWidget(_lbl("Full Name", bold=True, size=12, color=TXT_SUB))
        self.name_e = _input("Enter your name")
        self.name_e.textChanged.connect(self._validate_name_inline)
        lay.addWidget(self.name_e)
        self.name_err = QLabel("")
        self.name_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.name_err.setVisible(False)
        lay.addWidget(self.name_err)

        # [FN] Validate email
        lay.addWidget(_lbl("Email (optional)", bold=True, size=12, color=TXT_SUB))
        self.gmail_e = _input("example@gmail.com")
        self.gmail_e.textChanged.connect(self._validate_email_inline)
        lay.addWidget(self.gmail_e)
        self.email_err = QLabel("")
        self.email_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.email_err.setVisible(False)
        lay.addWidget(self.email_err)

        # [FN] Validate age / height / weight
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

        # [FN] Select gender
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

        # [FN] BMR preview
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

        # [FN] Submit → save profile
        sub = _btn_primary("Create Profile  ✓", h=48)
        sub.clicked.connect(self._submit)
        lay.addWidget(sub)
        lay.addStretch()

    # [FN] Validate name
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

    # [FN] Validate email
    def _validate_email_inline(self, text):
        email = text.strip()
        if email and not re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', email):
            self.email_err.setText("⚠  Please enter a valid email address (e.g. example@gmail.com)")
            self.email_err.setVisible(True)
        else:
            self.email_err.setVisible(False)

    # [FN] Validate age / height / weight
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

    # [FN] BMR preview
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

    # [FN] Submit → save profile
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
