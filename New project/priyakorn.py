# ============================================================
#  priyakorn.py  —  Meal Log Screen
#  Owner: Priyakorn
#  Functions:
#    [FN] Food name autocomplete
#    [FN] Kcal/100g input
#    [FN] Amount input + kcal preview
#    [FN] Save to library checkbox
#    [FN] Add food to log
#    [FN] Filter food in table
#    [FN] Delete selected (button)
# ============================================================
from datetime import date
from shared import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QCheckBox, QCompleter, QStringListModel,
    QDoubleValidator,
    Qt, QFont, QColor,
    PRIMARY, P_MED, P_LIGHT, P_ACCENT,
    BG, BG2, CARD, BORDER, RED, TXT, TXT_MUTED, TXT_SUB,
    MEAL_ICONS,
    _lbl, _input, _btn_primary, _card,
    FoodItem, app_data,
    GradientWidget,
)
from phumin import TrashZone          # TrashZone widget belongs to Phumin
from panhathai import LibraryDialog   # LibraryDialog belongs to Panhathai


# ══════════════════════════════════════════════════════════════════════════════
#  MEAL SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class MealScreen(QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.meal_type = "Breakfast"
        self.log_date = date.today()
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
        back.clicked.connect(self._go_back)
        self.title_lbl = _lbl("Breakfast", bold=True, size=17, color="white")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        lib_btn = QPushButton("📚  Library")
        lib_btn.setFixedHeight(34)
        lib_btn.setFixedWidth(110)
        lib_btn.setStyleSheet(f"""
            QPushButton {{ background:rgba(255,255,255,0.20); color:white;
                border:1.5px solid rgba(255,255,255,0.45); border-radius:10px;
                font-size:12px; font-weight:bold; }}
            QPushButton:hover {{ background:rgba(255,255,255,0.35); }}
        """)
        lib_btn.clicked.connect(self._open_lib)
        tl.addWidget(back)
        tl.addWidget(self.title_lbl, 1)
        tl.addWidget(lib_btn)
        root.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll)
        inner = QWidget()
        inner.setStyleSheet(f"background:{BG};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(16, 16, 16, 16)
        il.setSpacing(12)
        scroll.setWidget(inner)

        add_card = _card()
        acl = QVBoxLayout(add_card)
        acl.setContentsMargins(16, 14, 16, 14)
        acl.setSpacing(8)

        acl.addWidget(_lbl("Add Food", bold=True, size=14))

        # [FN] Food name autocomplete
        self.name_e = _input("Food name (e.g. Steamed rice)")
        self._comp = QCompleter([])
        self._comp.setCaseSensitivity(Qt.CaseInsensitive)
        self._comp.setFilterMode(Qt.MatchContains)
        self._comp.activated.connect(self._comp_pick)
        self.name_e.setCompleter(self._comp)
        self.name_e.textChanged.connect(self._name_changed)
        acl.addWidget(self.name_e)

        # [FN] Kcal/100g input + [FN] Amount input + kcal preview
        cal_amt_row = QHBoxLayout()
        cal_amt_row.setSpacing(10)
        self.cal_e = _input("Kcal / 100g")
        self.cal_e.setValidator(QDoubleValidator(0, 99999, 1))
        self.amt_e = _input("Amount (grams)")
        self.amt_e.setValidator(QDoubleValidator(0, 99999, 1))
        cal_amt_row.addWidget(self.cal_e)
        cal_amt_row.addWidget(self.amt_e)
        acl.addLayout(cal_amt_row)

        self.kcal_preview = _lbl("", size=11, color=TXT_MUTED)
        self.cal_e.textChanged.connect(self._update_kcal_preview)
        self.amt_e.textChanged.connect(self._update_kcal_preview)
        acl.addWidget(self.kcal_preview)

        bottom_row = QHBoxLayout()
        # [FN] Save to library checkbox
        self.save_cb = QCheckBox("Save to library")
        self.save_cb.setChecked(True)
        self.save_cb.setStyleSheet(f"color:{TXT_SUB}; background:transparent; font-size:11px;")
        # [FN] Add food to log
        add_btn = _btn_primary("+ Add Food", h=38)
        add_btn.setFixedWidth(120)
        add_btn.clicked.connect(self._add_food)
        bottom_row.addWidget(self.save_cb)
        bottom_row.addStretch()
        bottom_row.addWidget(add_btn)
        acl.addLayout(bottom_row)

        self.add_err = QLabel("")
        self.add_err.setStyleSheet(f"color:{RED}; font-size:11px; background:transparent;")
        self.add_err.setVisible(False)
        acl.addWidget(self.add_err)

        il.addWidget(add_card)

        # [FN] Filter food in table
        lh = QHBoxLayout()
        lh.addWidget(_lbl("Food List", bold=True, size=14))
        lh.addStretch()
        self.srch = _input("🔍  Search", 32)
        self.srch.setMaximumWidth(150)
        self.srch.setStyleSheet(f"""
            QLineEdit {{
                background:{CARD}; border:1.5px solid {BORDER};
                border-radius:16px; padding:0 12px; font-size:12px;
            }}
            QLineEdit:focus {{ border-color:{P_ACCENT}; }}
        """)
        self.srch.textChanged.connect(self._filter_table)
        lh.addWidget(self.srch)
        il.addLayout(lh)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Food", "kcal/100g", "Amount", "Total"])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(False)
        self.table.setMinimumHeight(150)
        self.table.setMaximumHeight(240)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        il.addWidget(self.table)

        # TrashZone — drag-to-delete (implemented by Phumin)
        self.trash = TrashZone()
        self.trash.delete_signal.connect(self._delete_sel)
        il.addWidget(self.trash)

        tot_row = QHBoxLayout()
        tot_row.addStretch()
        self.total_lbl = _lbl("Total : 0 kcal", bold=True, size=13, color=PRIMARY)
        tot_row.addWidget(self.total_lbl)
        il.addLayout(tot_row)

    # [FN] Amount input + kcal preview
    def _update_kcal_preview(self):
        try:
            c = float(self.cal_e.text())
            a = float(self.amt_e.text())
            total = round((a / 100) * c, 1)
            self.kcal_preview.setText(f"→ {total} kcal")
            self.kcal_preview.setStyleSheet(f"color:{PRIMARY}; background:transparent; font-weight:bold; font-size:12px;")
        except ValueError:
            self.kcal_preview.setText("")

    def _refresh_comp(self):
        # [FN] Food name autocomplete — refresh list
        self._comp.setModel(QStringListModel([f.name for f in app_data.food_library.all()]))

    def _name_changed(self, t):
        # [FN] Food name autocomplete — auto-fill kcal
        s = app_data.food_library.find(t)
        if s: self.cal_e.setText(str(s.cal_per_100g))

    def _comp_pick(self, name):
        s = app_data.food_library.find(name)
        if s: self.cal_e.setText(str(s.cal_per_100g))

    def _open_lib(self):
        dlg = LibraryDialog(self)
        dlg.food_selected.connect(lambda n, c: (
            self.name_e.setText(n),
            self.cal_e.setText(str(c)),
            self.amt_e.setFocus()
        ))
        dlg.exec()
        self._refresh_comp()

    def set_meal(self, mt, ld):
        self.meal_type = mt
        self.log_date = ld
        self.title_lbl.setText(f"{MEAL_ICONS.get(mt, '🍽')}  {mt}")
        self._refresh_comp()
        self._refresh_table()

    # [FN] Add food to log
    def _add_food(self):
        n = self.name_e.text().strip()
        c = self.cal_e.text().strip()
        a = self.amt_e.text().strip()
        if not all([n, c, a]):
            self.add_err.setText("⚠  Please fill in Food Name, Kcal/100g, and Amount.")
            self.add_err.setVisible(True)
            return
        self.add_err.setVisible(False)
        cal, amt = float(c), float(a)
        # [FN] Save to library checkbox
        if self.save_cb.isChecked():
            app_data.food_library.add(n, cal)
            self._refresh_comp()
        app_data.add_food(FoodItem(n, cal, amt, self.meal_type, self.log_date))
        self.name_e.clear()
        self.cal_e.clear()
        self.amt_e.clear()
        self.kcal_preview.setText("")
        self._refresh_table()

    def _refresh_table(self):
        log = app_data.get_log(self.log_date)
        items = log.get_meal(self.meal_type) if log else []
        self._fill(items)
        total = log.meal_calories(self.meal_type) if log else 0
        self.total_lbl.setText(f"Total : {int(total)} kcal")

    def _fill(self, items):
        self.table.setRowCount(len(items))
        for r, it in enumerate(items):
            vals = [it.name, str(int(it.cal_per_100g)), f"{int(it.amount_g)}g", f"{it.total_cal}"]
            aligns = [Qt.AlignLeft | Qt.AlignVCenter,
                      Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter]
            bg = QColor(BG2) if r % 2 == 0 else QColor(CARD)
            for col, (val, align) in enumerate(zip(vals, aligns)):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(align)
                cell.setBackground(bg)
                self.table.setItem(r, col, cell)
            self.table.item(r, 0).setData(Qt.UserRole, it.id)
        self.table.setRowHeight(0, 36) if items else None

    # [FN] Filter food in table
    def _filter_table(self, t):
        log = app_data.get_log(self.log_date)
        items = log.get_meal(self.meal_type) if log else []
        if t:
            items = [i for i in items if t.lower() in i.name.lower()]
        self._fill(items)

    # [FN] Delete selected (button)
    def _delete_sel(self):
        row = self.table.currentRow()
        if row < 0:
            return
        cell = self.table.item(row, 0)
        if cell:
            fid = cell.data(Qt.UserRole)
            if fid:
                app_data.remove_food(self.log_date, fid)
                self._refresh_table()

    def _go_back(self):
        self.mw.show_diary(self.log_date)
