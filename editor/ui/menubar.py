from PySide6.QtGui import QAction, QKeySequence

def build_menubar(window):
    menubar = window.menuBar()

    file_menu = menubar.addMenu("File")
    edit_menu = menubar.addMenu("Edit")
    view_menu = menubar.addMenu("View")
    tools_menu = menubar.addMenu("Tools")
    help_menu = menubar.addMenu("Help")

    actions = {}

    # File
    actions["new"] = QAction("New Project…", window)
    actions["open"] = QAction("Open…", window)
    actions["save"] = QAction("Save", window)
    actions["save_as"] = QAction("Save As…", window)
    actions["import"] = QAction("Import…", window)
    actions["export_folder"] = QAction("Export as Folder…", window)
    actions["exit"] = QAction("Exit", window)

    actions["open"].setShortcut(QKeySequence.Open)
    actions["save"].setShortcut(QKeySequence.Save)
    actions["save_as"].setShortcut(QKeySequence.SaveAs)
    actions["exit"].setShortcut(QKeySequence.Quit)

    file_menu.addAction(actions["new"])
    file_menu.addAction(actions["open"])
    file_menu.addSeparator()
    file_menu.addAction(actions["save"])
    file_menu.addAction(actions["save_as"])
    file_menu.addSeparator()
    file_menu.addAction(actions["import"])
    file_menu.addAction(actions["export_folder"])
    file_menu.addSeparator()
    file_menu.addAction(actions["exit"])

    # Tools
    actions["validate"] = QAction("Validate Project", window)
    tools_menu.addAction(actions["validate"])

    # Help
    actions["about"] = QAction("About", window)
    help_menu.addAction(actions["about"])

    actions["new"].triggered.connect(window.action_new_project)
    actions["open"].triggered.connect(window.action_open_project)
    actions["save"].triggered.connect(window.action_save_project)
    actions["save_as"].triggered.connect(window.action_save_as)
    actions["import"].triggered.connect(window.action_import)
    actions["export_folder"].triggered.connect(window.action_export_folder)
    actions["validate"].triggered.connect(window.action_validate)
    actions["about"].triggered.connect(window.action_about)
    actions["exit"].triggered.connect(window.close)

    return actions