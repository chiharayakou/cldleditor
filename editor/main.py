import sys
from PySide6.QtWidgets import QApplication
from editor.workspace.paths import ensure_app_identity, debug_paths

def main():
    app = QApplication(sys.argv)
    ensure_app_identity("Chihara Yakou", "CLDL Editor")
    debug_paths()
    
    from editor.ui.main_window import MainWindow
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())

if __name__ == "__main__":
    main()