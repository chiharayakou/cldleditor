import sys
from PySide6.QtWidgets import QApplication
from editor.ui.main_window import MainWindow
from editor.workspace.paths import ensure_app_identity

def main():
    app = QApplication(sys.argv)
    ensure_app_identity("Chihara Yakou", "CLDL Editor")
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())

if __name__ == "__main__":
    main()