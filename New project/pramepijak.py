# ============================================================
#  pramepijak.py  —  Home (Diary) Screen
#  Owner: Pramepijak
#  Functions:
#    [FN] Calorie status (Low / Balanced / High)
#    [FN] Cheat day toggle
#    [FN] Progress bar
#    [FN] Weekly total preview
#    [FN] BMR / target kcal calculation
#    [FN] Save profile
# ============================================================
from datetime import date, timedelta
from shared import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QCheckBox, QProgressBar, QFrame,
    Qt, QFont, QColor,
    PRIMARY, P_MED, P_LIGHT, P_ACCENT, P_GLOW,
    BG, BG2, CARD, BORDER, ORANGE, O_LIGHT, RED, R_LIGHT, L_GRAY,
    TXT, TXT_SUB, TXT_MUTED,
    STATUS_COLOR, STATUS_BG, MEALS, MEAL_ICONS, MEAL_STYLE,
    _lbl, _sep,
    GradientWidget, GradientFrame, PersonIconButton,
    app_data,
)
from phumin import CalorieMeter   # CalorieMeter widget belongs to Phumin


# ══════════════════════════════════════════════════════════════════════════════
#  DIARY SCREEN  (Home)
# ══════════════════════════════════════════════════════════════════════════════
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

        # Date navigation
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

        # Summary card
        self.sum_card = GradientFrame("#EDF9F2", "#FFFFFF", radius=18,
                                       vertical=True, border_color=BORDER)
        self.sum_card.setStyleSheet("")
        scl = QVBoxLayout(self.sum_card)
        scl.setContentsMargins(16, 14, 16, 14)
        scl.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(0)

        # [FN] Calorie status (Low / Balanced / High)
        self.status_badge = QLabel("↓ Low")
        self.status_badge.setFixedHeight(26)
        self.status_badge.setStyleSheet(f"""
            color:{ORANGE}; background:{O_LIGHT};
            border-radius:13px; padding:0 10px;
            font-size:11px; font-weight:bold;
        """)

        # [FN] Cheat day toggle
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

        # CalorieMeter (implemented by Phumin, used here)
        self.meter = CalorieMeter()
        mid.addWidget(self.meter)

        stats = QVBoxLayout()
        stats.setSpacing(6)
        stats.setAlignment(Qt.AlignVCenter)

        self.food_lbl = _lbl("Eaten  0 kcal", size=12, color=TXT)
        self.goal_lbl = _lbl("Target  0 kcal", size=12, color=TXT_MUTED)

        # [FN] Progress bar
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

        # Meal buttons
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

        # [FN] Weekly total preview
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
        # [FN] BMR / target kcal calculation
        target = app_data.profile.calculate_target_kcal()
        consumed = log.total_calories() if log else 0
        is_cheat = log.is_cheat_day if log else False

        self.cheat_cb.blockSignals(True)
        self.cheat_cb.setChecked(is_cheat)
        self.cheat_cb.blockSignals(False)

        self.meter.set_data(consumed, target, is_cheat)

        if is_cheat:
            # [FN] Cheat day toggle — UI update
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
            # [FN] Calorie status (Low / Balanced / High)
            st = app_data.get_status(self.current_date)
            col = STATUS_COLOR.get(st, "#78909C")
            bg_col = STATUS_BG.get(st, BG2)
            st_label = {"low": "↓ Low", "balanced": "✓ Balanced", "high": "↑ High"}.get(st, st)
            self.status_badge.setText(st_label)
            self.status_badge.setStyleSheet(f"""
                color:{col}; background:{bg_col};
                border-radius:13px; padding:0 10px;
                font-size:11px; font-weight:bold;
            """)
            # [FN] Progress bar
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

        # [FN] Weekly total preview
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
        # [FN] Cheat day toggle
        app_data.toggle_cheat_day(self.current_date)
        self.refresh()
