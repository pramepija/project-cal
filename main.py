# ============================================================
#  main.py  —  MainWindow + Entry Point
#  Assembles all screens from each team member's file.
#
#  Import map:
#    shared.py      → Theme, Helpers, Models, app_data, Shared Widgets
#    panhathai.py   → SplashScreen, LibraryDialog
#    tintrai.py     → ProfileScreen (ProfileSetup)
#    pramepijak.py  → DiaryScreen (Home)
#    priyakorn.py   → MealScreen (MealLog)
#    phumin.py      → TrashZone, CalorieMeter, EditDialog,
#                     ProfileViewScreen, WeeklyChart, WeeklyScreen
# ============================================================
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QFont

from shared import APP_STYLE, app_data

from panhathai  import SplashScreen
from tintrai    import ProfileScreen
from pramepijak import DiaryScreen
from priyakorn  import MealScreen
from phumin     import WeeklyScreen, ProfileViewScreen


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calorie Calculator")
        self.setMinimumSize(400, 680)
        self.resize(420, 780)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.splash        = SplashScreen(self)
        self.profile_setup = ProfileScreen(self)
        self.diary         = DiaryScreen(self)
        self.meal          = MealScreen(self)
        self.weekly        = WeeklyScreen(self)
        self.profile_view  = ProfileViewScreen(self)

        for w in (self.splash, self.profile_setup, self.diary,
                  self.meal, self.weekly, self.profile_view):
            self.stack.addWidget(w)

        self.show_splash()

    def closeEvent(self, event):
        app_data.save()
        event.accept()

    def show_splash(self):        self.stack.setCurrentWidget(self.splash)
    def show_profile_setup(self): self.stack.setCurrentWidget(self.profile_setup)
    def show_diary(self, d=None): app_data.save(); self.diary.refresh(d); self.stack.setCurrentWidget(self.diary)
    def show_meal(self, mt, ld):  self.meal.set_meal(mt, ld); self.stack.setCurrentWidget(self.meal)
    def show_weekly(self):        self.weekly.refresh(); self.stack.setCurrentWidget(self.weekly)
    def show_profile_view(self):  self.profile_view.refresh(); self.stack.setCurrentWidget(self.profile_view)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Calorie Calculator")
    app.setFont(QFont("Segoe UI", 13))
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
