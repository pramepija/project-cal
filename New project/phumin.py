# ============================================================
#  phumin.py  —  TrashZone + CalorieMeter + EditProfile + Weekly
#  Owner: Phumin
#  Functions:
#    [FN] Edit name / age / height / weight / target weight
#    [FN] Select gender
#    [FN] Delete by drag to trash zone
#    [FN] Bar color by status (Low / Balanced / High / Cheat)
#    [FN] Target dashed line
#    [FN] Calorie meter (circular ring)
#    [FN] Click day → go to Diary
# ============================================================
import re
from datetime import date, timedelta
from shared import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    Qt, QFont, QColor, QPainter, QBrush, QPen, QLinearGradient, QPainterPath, QRect,
    QTimer, Signal,
    PRIMARY, P_MED, P_LIGHT, P_ACCENT,
    BG, BG2, CARD, BORDER, ORANGE, O_LIGHT, RED, R_LIGHT, L_GRAY, GRAY,
    TXT, TXT_SUB, TXT_MUTED,
    DAY_LABEL,
    _lbl, _input, _sep, _btn_primary, _card,
    GradientWidget, GradientFrame,
    UserProfile, app_data,
)


# ══════════════════════════════════════════════════════════════════════════════
#  TRASH ZONE  — [FN] Delete by drag to trash zone
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
    def dropEvent(self, e):      self._idle(); self.delete_signal.emit(); e.acceptProposedAction()


# ══════════════════════════════════════════════════════════════════════════════
#  CALORIE METER  — [FN] Calorie meter (circular ring)
# ══════════════════════════════════════════════════════════════════════════════
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

        # Background ring
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


# ══════════════════════════════════════════════════════════════════════════════
#  EDIT DIALOG  — [FN] Edit name / age / height / weight / target weight
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


# ══════════════════════════════════════════════════════════════════════════════
#  PROFILE VIEW SCREEN  — [FN] Edit profile + save
# ══════════════════════════════════════════════════════════════════════════════
class ProfileViewScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.setStyleSheet(f"background:{BG};")

        # Unsaved changes tracking
        self._pending: dict = {}
        self._unsaved = False

        self._build()

    def _mark_changed(self):
        self._unsaved = True
        self._warn_banner.setVisible(True)
        self._save_ok_lbl.setVisible(False)

    def _clear_unsaved(self):
        self._unsaved = False
        self._pending.clear()
        self._warn_banner.setVisible(False)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
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

        # Unsaved warning banner
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

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll)
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(16, 16, 16, 24)
        il.setSpacing(0)
        scroll.setWidget(inner)

        # Hero card
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

        il.addWidget(_lbl("About Me", bold=True, size=15))
        il.addSpacing(10)

        # [FN] Select gender
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

        # [FN] Edit name / age / height / weight / target weight
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

        self._save_ok_lbl = QLabel("✅  Profile saved!")
        self._save_ok_lbl.setAlignment(Qt.AlignCenter)
        self._save_ok_lbl.setStyleSheet(f"""
            color:{P_MED}; background:{P_LIGHT};
            border-radius:8px; padding:8px;
            font-weight:bold; font-size:12px;
        """)
        self._save_ok_lbl.setVisible(False)
        il.addWidget(self._save_ok_lbl)

        save_btn = _btn_primary("💾  Save Profile", h=44)
        save_btn.clicked.connect(self._save_profile)
        il.addWidget(save_btn)

        il.addStretch()

    def _try_go_back(self):
        if self._unsaved:
            self._warn_banner.setVisible(True)
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
        # [FN] Select gender
        self._pending["gender"] = t
        self._mark_changed()
        self._refresh_bmr_preview()

    def _refresh_bmr_preview(self):
        p = app_data.profile
        age    = self._pending.get("age",    p.age)
        height = self._pending.get("height", p.height)
        weight = self._pending.get("weight", p.weight)
        gender = self._pending.get("gender", p.gender)
        tmp = UserProfile(age=age, height=height, weight=weight, gender=gender)
        self.bmr_lbl.setText(f"Daily Target (BMR × 1.2):  {tmp.calculate_target_kcal()} kcal")

    def _edit(self, attr, display):
        # [FN] Edit name / age / height / weight / target weight
        p = app_data.profile
        current = self._pending.get(attr, getattr(p, attr, ""))
        dlg = EditDialog(display, current, self, attr=attr)
        if dlg.exec():
            val = dlg.value()
            try:
                if attr == "age":
                    val = int(val)
                elif attr in ("height", "weight", "target_weight"):
                    val = float(val)
            except ValueError:
                return
            self._pending[attr] = val
            self._mark_changed()
            self._refresh_labels()
            self._refresh_bmr_preview()

    def _save_profile(self):
        p = app_data.profile
        for attr, val in self._pending.items():
            setattr(p, attr, val)
        self._clear_unsaved()
        self.refresh()
        self._save_ok_lbl.setText("✅  Profile saved!")
        self._save_ok_lbl.setVisible(True)
        QTimer.singleShot(2200, lambda: self._save_ok_lbl.setVisible(False))

    def _refresh_labels(self):
        p = app_data.profile
        name = self._pending.get("name", p.name) or "—"
        self.hero_name.setText(name)

        weight = self._pending.get("weight", p.weight)
        tw     = self._pending.get("target_weight", p.target_weight)
        height = self._pending.get("height", p.height)

        self.wt_box_val.setText(f"{weight} kg" if weight else "—")
        self.tw_box_val.setText(f"{tw} kg" if tw else "—")
        if height and weight:
            bmi_v = round(weight / ((height / 100) ** 2), 1)
            self.bmi_box_val.setText(str(bmi_v))
        else:
            self.bmi_box_val.setText("—")

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
#  WEEKLY CHART  — [FN] Bar color by status + [FN] Target dashed line
# ══════════════════════════════════════════════════════════════════════════════
class WeeklyChart(QWidget):
    def __init__(self):
        super().__init__()
        self.data = []
        self.target = 2000.0
        self.setMinimumHeight(200)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:transparent;")

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

        # [FN] Target dashed line
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

            # [FN] Bar color by status (Low / Balanced / High / Cheat)
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


# ══════════════════════════════════════════════════════════════════════════════
#  WEEKLY SCREEN  — [FN] Click day → go to Diary
# ══════════════════════════════════════════════════════════════════════════════
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

        from shared import _sep
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

        from shared import _sep as sep2
        il.addWidget(sep2())

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
