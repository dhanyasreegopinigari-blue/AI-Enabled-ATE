"""
AI-Enabled-ATE  -  GUI preview launcher (MMI only, no backend yet)
===================================================================

What this file does
-------------------
1. Loads the Qt Designer files in  MMI/ui/*.ui   (the real design lives THERE).
2. Applies the stylesheet         MMI/ui/styles/dark.qss  or  light.qss.
3. Wires up ONLY the pure-GUI behaviour: page navigation, collapsing the
   sidebar, dark/light switch, tab switches, TOC jumps, FAQ expand/collapse.
   Every other button just prints a message - the backend will be connected later.

How to run
----------
    pip install PyQt5
    python main.py                       # whole application window
    python main.py MMI/ui/dashboard.ui      # preview ONE .ui file on its own

Rule of thumb: never design widgets in this file - design them in Qt Designer.
This file only finds widgets by their objectName and connects signals.
"""
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(BASE_DIR, "MMI", "ui")   # all .ui files, styles/ and icons/ live here
MMI_DIR = UI_DIR
STYLE_DIR = os.path.join(MMI_DIR, "styles")


def ui_path(filename):
    return os.path.join(MMI_DIR, filename)


def load_stylesheet(theme):
    """Return the QSS text for 'dark' or 'light'."""
    with open(os.path.join(STYLE_DIR, f"{theme}.qss"), encoding="utf-8") as f:
        return f.read()


def repolish(widget):
    """Qt must be told to re-read the stylesheet after a dynamic property (kind/role) changes."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def set_kind(widget, kind):
    widget.setProperty("kind", kind)
    repolish(widget)


def make_clickable(frame, callback):
    """QFrame cards (the 'quick action' cards) are not buttons, so we turn clicks into a callback."""
    class _Filter(QtCore.QObject):
        def eventFilter(self, obj, event):
            if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
                callback()
            return False
    f = _Filter(frame)
    frame.installEventFilter(f)
    frame._click_filter = f  # keep a reference so Python does not delete it


# --------------------------------------------------------------------------- #
class MainWindow:
    """Builds the full window from the .ui files and connects the GUI-only behaviour."""

    PAGE_TITLES = ["Dashboard", "AI Assistant", "User Manual"]

    def __init__(self, app):
        self.app = app
        self.theme = "dark"

        # --- 1. load every .ui file ---------------------------------------
        self.win = uic.loadUi(ui_path("main_window.ui"))
        self.dashboard = uic.loadUi(ui_path("dashboard.ui"))
        self.assistant = uic.loadUi(ui_path("AI-assistant.ui"))
        self.library = uic.loadUi(ui_path("library.ui"))
        self.guide = uic.loadUi(ui_path("usermanual.ui"))

        # --- 2. assemble pages into the stack ------------------------------
        stack = self.win.pageStack
        while stack.count():                      # remove the placeholder pages drawn in Designer
            stack.removeWidget(stack.widget(0))
        for page in (self.dashboard, self.assistant, self.library):
            stack.addWidget(page)
        self.library.userGuidePlaceholder.hide()  # usermanual.ui lives inside library.ui's 2nd tab
        self.library.userGuideHostLayout.addWidget(self.guide)

        self._wire_sidebar()
        self._wire_dashboard()
        self._wire_assistant()
        self._wire_library()
        self._wire_guide()
        self.go_to_page(0)

    # ------------------------------------------------------------------ navigation
    def _wire_sidebar(self):
        w = self.win
        self.nav_buttons = [w.btnNavDashboard, w.btnNavAssistant, w.btnNavManual]
        self.sidebar_collapsed = False
        for i, b in enumerate(self.nav_buttons):
            b.clicked.connect(lambda _=False, idx=i: self.go_to_page(idx))
        w.btnNavHelp.clicked.connect(lambda: self.todo("Help drawer"))
        w.btnCollapseSidebar.clicked.connect(self.toggle_sidebar)
        w.btnMenuToggle.clicked.connect(self.toggle_sidebar)
        w.btnTheme.clicked.connect(self.toggle_theme)
        w.btnSettings.clicked.connect(lambda: self.todo("Settings dialog"))
        # remember each nav button's text/icon so we can restore it after collapsing
        self._nav_info = {b: (b.text(), b.icon()) for b in self.nav_buttons + [w.btnNavHelp]}

    def go_to_page(self, idx):
        self.win.pageStack.setCurrentIndex(idx)
        self.win.headerTitleLabel.setText(self.PAGE_TITLES[idx])
        for i, b in enumerate(self.nav_buttons):
            self._set_nav_state(b, active=(i == idx))

    def _set_nav_state(self, button, active):
        if self.sidebar_collapsed:
            set_kind(button, "sidebarNavCollapsedActive" if active else "sidebarNavCollapsed")
        else:
            set_kind(button, "sidebarNavActive" if active else "sidebarNav")

    def toggle_sidebar(self):
        w = self.win
        self.sidebar_collapsed = not self.sidebar_collapsed
        collapsed = self.sidebar_collapsed
        w.globalSidebar.setFixedWidth(68 if collapsed else 230)
        w.appTitleLabel.setVisible(not collapsed)
        w.ollamaStatusLabel.setVisible(not collapsed)
        w.ollamaModelLabel.setVisible(not collapsed)
        for b in self.nav_buttons + [w.btnNavHelp, w.btnTheme, w.btnSettings]:
            original = self._nav_info.get(b)
            if b in (w.btnTheme, w.btnSettings):
                if not hasattr(b, "_orig_text"):
                    b._orig_text = b.text()
                b.setText("" if collapsed else b._orig_text)
            else:
                b.setText("" if collapsed else original[0])
        self.go_to_page(self.win.pageStack.currentIndex())
        set_kind(w.btnNavHelp, "sidebarNavCollapsed" if collapsed else "sidebarNav")

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.app.setStyleSheet(load_stylesheet(self.theme))
        self.win.btnTheme.setText("Light Mode" if self.theme == "light" else "Dark Mode")
        self.win.btnTheme._orig_text = self.win.btnTheme.text()

    # ------------------------------------------------------------------ dashboard
    def _wire_dashboard(self):
        d = self.dashboard
        for btn in (d.btnHeaderCamera, d.btnLiveCamera):
            btn.clicked.connect(lambda: self.todo("Live camera"))
        for btn in (d.btnHeaderUpload, d.btnUploadImage):
            btn.clicked.connect(lambda: self.todo("Upload photo"))
        d.btnViewManuals.clicked.connect(lambda: self.go_to_page(2))
        d.btnManageManuals.clicked.connect(lambda: self.go_to_page(2))
        make_clickable(d.qaUploadImage, lambda: self.todo("Upload image"))
        make_clickable(d.qaLiveCamera, lambda: self.todo("Live camera scan"))
        make_clickable(d.qaUploadVideo, lambda: self.todo("Upload video"))
        make_clickable(d.qaAskAI, lambda: self.go_to_page(1))

    # ------------------------------------------------------------------ AI assistant
    def _wire_assistant(self):
        a = self.assistant
        a.btnCollapseChats.clicked.connect(lambda: (a.chatSidebar.hide(), a.btnExpandChats.show()))
        a.btnExpandChats.clicked.connect(lambda: (a.chatSidebar.show(), a.btnExpandChats.hide()))
        a.btnSend.clicked.connect(lambda: self.todo("Send chat message"))
        a.btnNewChat.clicked.connect(lambda: self.todo("New chat"))
        for i in range(1, 7):                     # clicking a suggested question fills the input box
            card = getattr(a, f"suggestion{i}")
            text = getattr(a, f"suggestion{i}Text").text()
            make_clickable(card, lambda t=text: a.chatInput.setPlainText(t))

    # ------------------------------------------------------------------ library (manuals)
    def _wire_library(self):
        lib = self.library
        lib.btnSegLoaded.clicked.connect(lambda: self._library_tab(0))
        lib.btnSegGuide.clicked.connect(lambda: self._library_tab(1))
        for n in ("Esp32", "Uno"):                # "View" on a sample card opens the PDF viewer page
            getattr(lib, f"manual{n}BtnView").clicked.connect(lambda: lib.libraryStack.setCurrentIndex(1))
            getattr(lib, f"manual{n}BtnAsk").clicked.connect(lambda: self.go_to_page(1))
        lib.btnBackToLibrary.clicked.connect(lambda: lib.libraryStack.setCurrentIndex(0))
        lib.manualSearch.addAction(QtGui.QIcon(os.path.join(MMI_DIR, "icons", "search__6B8273.svg")), QtWidgets.QLineEdit.LeadingPosition)
        lib.btnAddManuals.clicked.connect(lambda: self.todo("Add manuals"))

    def _library_tab(self, idx):
        lib = self.library
        lib.manualsMainStack.setCurrentIndex(idx)
        set_kind(lib.btnSegLoaded, "chipActive" if idx == 0 else "chip")
        set_kind(lib.btnSegGuide, "chipActive" if idx == 1 else "chip")

    # ------------------------------------------------------------------ user guide
    def _wire_guide(self):
        g = self.guide
        sections = [g.secGettingStarted, g.secDashboard, g.secAssistant, g.secLibrary, g.secManuals,
                    g.secVoice, g.secExport, g.secSafety, g.secFaq]
        for i, b in enumerate(getattr(g, f"btnToc{n}") for n in range(1, 10)):
            b.clicked.connect(lambda _=False, s=sections[i]: g.docScroll.verticalScrollBar().setValue(
                s.mapTo(g.docScrollContents, QtCore.QPoint(0, 0)).y()))
        # FAQ answers start collapsed; clicking the question toggles them
        for q in g.findChildren(QtWidgets.QPushButton):
            if q.property("role") == "faqQuestion":
                answer = q.parentWidget().findChild(QtWidgets.QLabel, q.objectName().replace("Question", "Answer"))
                answer.hide()
                q.clicked.connect(lambda _=False, a=answer: a.setVisible(not a.isVisible()))
        # simple live filter of the documentation sections
        def filter_sections(text):
            text = text.lower().strip()
            for s in sections:
                corpus = " ".join(l.text() for l in s.findChildren(QtWidgets.QLabel)).lower()
                s.setVisible(not text or text in corpus)
        g.docSearchInput.textChanged.connect(filter_sections)
        g.btnOpenHardwareHub.clicked.connect(lambda: (self.go_to_page(2), self._library_tab(0)))
        g.btnOpenComponentLibrary.clicked.connect(lambda: self.todo("Component library"))
        g.btnOpenLightbox.clicked.connect(lambda: self.todo("Lightbox viewer"))

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def todo(what):
        print(f"[GUI preview] '{what}' clicked - backend not connected yet.")

    def show(self):
        self.win.show()


# --------------------------------------------------------------------------- #
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("dark"))

    if len(sys.argv) > 1:                          # preview a single .ui file
        single = uic.loadUi(sys.argv[1])
        single.show()
        sys.exit(app.exec_())

    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
